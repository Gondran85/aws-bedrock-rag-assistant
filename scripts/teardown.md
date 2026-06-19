# Teardown — tearing the project down safely

This project uses pay-per-use services. Some (Amazon S3 Vectors, the Knowledge Base, stored objects) keep costing while they exist, so when the project is no longer needed, everything should be removed in a **specific order**.

> **Critical ordering rule:** delete the **Knowledge Base before** its underlying **S3 Vectors** store. The KB depends on the vector store; removing the vector store first can orphan the KB and leave resources that fail to delete cleanly.

All resources are in **us-east-1**, account `765936999166`, tagged `projeto=rag-aifc01`.

## Order of deletion

| # | Resource | Why this order |
|---|---|---|
| 1 | Bedrock **Knowledge Base** (`acme-hr-kb`) | Depends on the vector store — must go first |
| 2 | **S3 Vectors** vector bucket / index | Safe to remove only after the KB that uses it is gone |
| 3 | **API Gateway** HTTP API (`acme-rag-api`) | Front door; no dependents once the front-end is gone |
| 4 | **Lambda** function (`acme-rag-query`) | Remove after the API that triggers it |
| 5 | **DynamoDB** table (`acme-rag-history`) | Independent; delete any time after Lambda |
| 6 | **IAM** roles/policies (Lambda exec role, KB service role) | Remove after the resources that used them |
| 7 | **S3** documents bucket (`acme-rag-docs-jeff-2026`) | Empty it first (versioning is on — delete all versions), then delete the bucket |
| 8 | **S3** front-end bucket (`acme-rag-frontend-jeff-2026`) | Empty, then delete |
| 9 | **CloudWatch** log groups (`/aws/lambda/acme-rag-query`) | Logs persist and can accrue cost; remove last |

## Step-by-step (AWS Console)

1. **Knowledge Base** — Bedrock → Knowledge bases → `acme-hr-kb` → Delete. Confirm.
2. **S3 Vectors** — delete the vector index, then the vector bucket created for the KB.
3. **API Gateway** — API Gateway → `acme-rag-api` → Actions → Delete.
4. **Lambda** — Lambda → `acme-rag-query` → Actions → Delete.
5. **DynamoDB** — DynamoDB → Tables → `acme-rag-history` → Delete.
6. **IAM** — IAM → Roles → delete the Lambda execution role and the Bedrock KB service role (and their inline policies).
7. **Documents bucket** — S3 → `acme-rag-docs-jeff-2026` → Empty (this deletes all object versions, since versioning is enabled) → then Delete bucket.
8. **Front-end bucket** — S3 → `acme-rag-frontend-jeff-2026` → Empty → Delete bucket.
9. **CloudWatch Logs** — CloudWatch → Log groups → delete `/aws/lambda/acme-rag-query`.

## Verification after teardown

- **Billing / Cost Explorer:** filter by tag `projeto=rag-aifc01` → confirm no active resources remain.
- **Service Quotas / Bedrock:** no active Knowledge Bases.
- **S3:** both project buckets gone.
- Keep the **AWS Budget** alert active for a few days as a safety net to catch anything missed.

## Notes

- **Versioning gotcha:** the documents bucket has versioning enabled, so a normal delete leaves old versions behind. Use **Empty** (which removes all versions) before deleting the bucket, or the bucket delete will fail.
- **Support case:** if the Bedrock quota Support case is still open, it can be resolved/closed separately — it does not block teardown.
- This file documents the manual console process. A CLI/script version (`teardown.sh`) can be added later for a one-command teardown, once AWS CLI is configured locally.
