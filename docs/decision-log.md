# 📐 Decision Log

> Lightweight Architecture Decision Record (ADR). One line per decision: what was chosen, what was rejected, and why. This is the file an interviewer should read first.

| # | Decision | Alternative rejected | Why |
|---|---|---|---|
| 1 | **RAG** with Bedrock Knowledge Bases | Fine-tuning / training from scratch | Policies change frequently; RAG retrieves current documents at query time, supports citations, and costs a fraction |
| 2 | **Amazon S3 Vectors** as vector store | OpenSearch Serverless | ~90% cheaper; OpenSearch Serverless has a fixed monthly cost even when idle — the classic budget killer for study RAG projects |
| 3 | **Amazon Nova Lite** as foundation model | Larger FMs (Nova Pro, Claude) | Cost per token; sufficient quality for factual Q&A when grounded by RAG |
| 4 | **SSE-S3** encryption | SSE-KMS | KMS adds USD 1/month per key + per-call charges; no key-audit requirement in this project. In a corporate setting with key-usage auditing requirements, SSE-KMS would be the choice |
| 5 | **Bucket versioning enabled** | No versioning | Protects against accidental overwrite/deletion; cost is irrelevant at this scale; accepted trade-off: emptying a versioned bucket takes one extra step at teardown |
| 6 | **us-east-1** region | Local region (me-central-1) | Broadest Bedrock model catalog and guaranteed S3 Vectors availability |
| 7 | **English** for all repo artifacts | Portuguese | International market reach; consistent with portfolio convention (`cloudops-finance`) |
| 8 | **Terminate** leftover resources from previous project | Keep instances stopped | Stopped EC2 still bills for EBS volumes and public IPs; recreating a study instance takes minutes |
