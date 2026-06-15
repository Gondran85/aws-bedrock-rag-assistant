"""
acme-rag-query — Lambda handler for the Acme RAG Assistant.

Receives a user question, queries the Bedrock Knowledge Base via
RetrieveAndGenerate, stores the exchange in DynamoDB, and returns the
answer with its source citations.

MOCK_MODE lets us test the whole flow today (error handling, response
shaping, DynamoDB write) WITHOUT calling Bedrock — useful while the
account's daily token limit is exhausted. Flip the env var to go live.
"""

import os
import json
import uuid
import datetime
import boto3
from botocore.exceptions import ClientError

# ---- Configuration (read from environment variables, not hardcoded) ----
# Set these in Lambda console -> Configuration -> Environment variables.
KB_ID = os.environ.get("KB_ID", "")                  # e.g. XS3LLUWNYD
MODEL_ARN = os.environ.get("MODEL_ARN", "")          # Nova Lite inference profile/model ARN
TABLE_NAME = os.environ.get("TABLE_NAME", "")        # DynamoDB table for history
MOCK_MODE = os.environ.get("MOCK_MODE", "true").lower() == "true"

# Clients are created once per container (reused across invocations = cheaper/faster).
# region_name is inferred from the Lambda's region.
bedrock_agent = boto3.client("bedrock-agent-runtime")
dynamodb = boto3.resource("dynamodb")


def _cors_headers():
    """Headers so the browser front-end (different origin) can call this API."""
    return {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",          # tighten to your domain in production
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "OPTIONS,POST",
    }


def _response(status_code, body):
    """Shape the HTTP response API Gateway expects."""
    return {
        "statusCode": status_code,
        "headers": _cors_headers(),
        "body": json.dumps(body, ensure_ascii=False),
    }


def _extract_question(event):
    """
    Pull the user's question out of the event.
    Works both for direct console test events ({"question": "..."})
    and for API Gateway proxy events (question inside event['body'] as JSON).
    """
    if "body" in event and event["body"]:
        try:
            parsed = json.loads(event["body"])
            return parsed.get("question", "").strip()
        except (json.JSONDecodeError, TypeError):
            return ""
    return event.get("question", "").strip()


def _mock_answer(question):
    """Simulated KB response — same shape the real path returns."""
    return {
        "answer": (
            f"[MOCK] You asked: '{question}'. "
            "Full-time employees accrue 20 vacation days in their first year, "
            "rising to 22 after one year of service. (Simulated answer — "
            "Bedrock not called.)"
        ),
        "citations": [
            {"source": "hr-policies/vacation-policy.pdf", "snippet": "Annual vacation entitlement..."}
        ],
        "mode": "mock",
    }


def _real_answer(question):
    """Query the Bedrock Knowledge Base for a grounded, cited answer."""
    result = bedrock_agent.retrieve_and_generate(
        input={"text": question},
        retrieveAndGenerateConfiguration={
            "type": "KNOWLEDGE_BASE",
            "knowledgeBaseConfiguration": {
                "knowledgeBaseId": KB_ID,
                "modelArn": MODEL_ARN,
            },
        },
    )
    # Collect citations (source files) so the front-end can show them.
    citations = []
    for c in result.get("citations", []):
        for ref in c.get("retrievedReferences", []):
            loc = ref.get("location", {}).get("s3Location", {}).get("uri", "unknown")
            text = ref.get("content", {}).get("text", "")[:160]
            citations.append({"source": loc, "snippet": text})

    return {
        "answer": result["output"]["text"],
        "citations": citations,
        "mode": "live",
    }


def _save_history(question, answer_obj):
    """Best-effort write of the exchange to DynamoDB. Never breaks the response."""
    if not TABLE_NAME:
        return
    try:
        table = dynamodb.Table(TABLE_NAME)
        table.put_item(Item={
            "id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "question": question,
            "answer": answer_obj["answer"],
            "mode": answer_obj["mode"],
        })
    except ClientError as e:
        print(f"[WARN] Could not write history to DynamoDB: {e}")


def _http_method(event):
    """
    Get the HTTP method regardless of API Gateway payload version.
    HTTP API (payload v2) -> event['requestContext']['http']['method']
    REST API (payload v1) -> event['httpMethod']
    """
    v2 = event.get("requestContext", {}).get("http", {}).get("method")
    return v2 or event.get("httpMethod")


def lambda_handler(event, context):
    # Handle CORS preflight from the browser (works for v1 and v2).
    if _http_method(event) == "OPTIONS":
        return _response(200, {"ok": True})

    question = _extract_question(event)
    if not question:
        return _response(400, {"error": "Missing 'question' in request."})

    try:
        answer_obj = _mock_answer(question) if MOCK_MODE else _real_answer(question)
    except ClientError as e:
        code = e.response["Error"]["Code"]
        # Map AWS error codes to clear client responses (the diagnosis discipline
        # we learned: 403 vs 429 vs 400 are different problems).
        if code in ("ThrottlingException", "TooManyRequestsException"):
            return _response(429, {"error": "Rate or daily token limit reached. Try again later."})
        if code == "AccessDeniedException":
            return _response(403, {"error": "Lambda role lacks Bedrock permission."})
        return _response(500, {"error": f"Bedrock error: {code}"})
    except Exception as e:  # noqa
        return _response(500, {"error": f"Unexpected error: {str(e)}"})

    _save_history(question, answer_obj)
    return _response(200, answer_obj)
