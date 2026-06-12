# 🤖 AWS Bedrock RAG Assistant

> Enterprise knowledge assistant using **Retrieval-Augmented Generation (RAG)** on AWS — fully serverless, built with cost governance and Responsible AI from day one.

[![AWS](https://img.shields.io/badge/AWS-Cloud-FF9900?logo=amazonwebservices&logoColor=white)](https://aws.amazon.com/)
[![Amazon Bedrock](https://img.shields.io/badge/Amazon-Bedrock-232F3E?logo=amazonwebservices&logoColor=white)](https://aws.amazon.com/bedrock/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://python.org)
[![Serverless](https://img.shields.io/badge/Architecture-Serverless-FD5750?logo=serverless&logoColor=white)](https://aws.amazon.com/serverless/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-In%20Progress-blue)](#-project-phases)

---

## 📋 About the project

**Acme RAG Assistant** is a web application where employees ask questions in natural language and receive answers **grounded in the company's internal documents** (HR policies), with source citations. The goal is not the app itself — it is to demonstrate a **professional GenAI architecture**: managed RAG with Amazon Bedrock Knowledge Bases, low-cost vector storage with Amazon S3 Vectors, runtime safety with Bedrock Guardrails, and strict cost governance.

### 🎯 Simulated business problem

Acme Corp's HR team answers the same policy questions every day. The documents exist, but keyword search fails whenever employees phrase questions differently from the documents' wording. The company needs **grounded, citable answers at near-zero cost** before investing in a full internal tool.

### 🛠️ Technologies and services

**Cloud (AWS):** Amazon Bedrock (Knowledge Bases · Guardrails) · Amazon S3 · Amazon S3 Vectors · AWS Lambda · Amazon API Gateway · Amazon DynamoDB · AWS IAM · Amazon CloudWatch · AWS CloudTrail · AWS Budgets

**Application:** Python 3.12 · boto3 · HTML5 · CSS3 · JavaScript (vanilla)

**Tooling:** Bash · Git · Mermaid · draw.io

---

## 🏛️ Architecture

📄 Full diagram and request flow in [docs/architecture.md](docs/architecture.md) · Every design choice justified in [docs/decision-log.md](docs/decision-log.md)

- **Ingestion path:** documents stored in S3 (SSE-S3 encryption, versioning, Block Public Access) → Bedrock Knowledge Base → Titan Text Embeddings → S3 Vectors index
- **Query path:** static web front-end → API Gateway → Lambda (Python) → Bedrock `RetrieveAndGenerate` (Amazon Nova Lite) → Guardrails → answer **with source citations**
- **State:** DynamoDB stores question history
- **Observability:** CloudWatch logs and metrics · CloudTrail audit trail
- **Cost governance:** AWS Budgets (USD 5 cap, layered alerts at 50/80/100%) · cost-allocation tags on every resource

---

## 💰 Cost estimate

| Service | Pricing model | Free Tier? | Project estimate |
|---|---|---|---|
| Bedrock — Amazon Nova Lite | per 1K input/output tokens | ❌ **No Free Tier** | < $1 (testing volume) |
| Bedrock — Titan Text Embeddings | per 1K tokens | ❌ No | cents (ingestion) |
| Amazon S3 Vectors | per GB stored + per query | ❌ No | cents |
| Lambda / API Gateway / DynamoDB / S3 | per request / per GB | ✅ always-free tiers | ~$0 |
| **Total (full project lifecycle)** | | | **< $5** |

> ⚠️ **Key difference from compute-based projects:** GenAI services bill from the **first token**. Cost control here is per-call discipline (small models, capped output tokens, budget alerts) — not instance scheduling.

---

## 🛡️ Security applied

✅ **Least-privilege IAM roles** — no access keys in code, ever
✅ **S3 Block Public Access** on the documents bucket (all four settings on)
✅ **Encryption at rest** (SSE-S3) + **bucket versioning**
✅ **Bedrock Guardrails** — content filtering at runtime
✅ **CloudTrail** auditing all management events
✅ **AWS Budgets** with layered alerts (50% / 80% actual, 100% forecasted)

---

## 🧭 Responsible AI

| Principle | How this project applies it |
|---|---|
| **Grounding** | Answers are restricted to retrieved document chunks (RAG) |
| **Transparency** | Every answer returns its source citations |
| **Refusal over hallucination** | Out-of-scope questions return "not in the knowledge base" — never an invented answer |
| **Safety** | Guardrails enforce denied topics and content filters at runtime |

---

## 🏗️ Well-Architected Framework mapping

| Pillar | How it is applied in this project |
|---|---|
| **Operational Excellence** | CloudWatch logs/metrics, CloudTrail, version-controlled docs and code |
| **Security** | Least-privilege IAM, Block Public Access, SSE-S3, Guardrails |
| **Reliability** | Fully managed services (Bedrock, Lambda, DynamoDB) — no servers to fail |
| **Performance Efficiency** | Right-sized FM (Nova Lite), serverless auto-scaling |
| **Cost Optimization** | S3 Vectors over OpenSearch Serverless (~90% cheaper), Budgets, cost tags |
| **Sustainability** | Zero idle compute — every component is pay-per-use |

---

## 🎓 Certification mapping — AWS Certified AI Practitioner (AIF-C01)

| Exam domain | Where it appears in this project |
|---|---|
| **D1** Fundamentals of AI/ML | structured vs. unstructured data, managed AI services |
| **D2** Generative AI Fundamentals | tokens, embeddings, inference parameters, FM selection |
| **D3** Foundation Model Applications | RAG vs. fine-tuning, Knowledge Bases, prompt engineering, Guardrails |
| **D4** Responsible AI | grounding, source citations, content filtering, hallucination mitigation |
| **D5** Security, Compliance & Governance | IAM, encryption, CloudTrail, Budgets, cost-allocation tags |

---

## 🚀 Project phases

| # | Phase | Status |
|---|---|---|
| 1 | Use case, requirements and architecture | ✅ Done |
| 2 | Account hardening, IAM, cost guardrails | ✅ Done |
| 3 | Document storage (S3) | ✅ Done |
| 4 | Data preparation and ingestion | 🔄 In progress |
| 5 | Knowledge Base + S3 Vectors + Guardrails | ⏳ Planned |
| 6 | Backend — Lambda + API Gateway | ⏳ Planned |
| 7 | Front-end + full integration | ⏳ Planned |
| 8 | Observability, testing, teardown | ⏳ Planned |

---

## 📸 Evidence

Screenshots are added to [`screenshots/`](screenshots/) at the end of each phase.

---

## 🎓 Lessons learned

Updated at the end of every phase — see [docs/lessons-learned.md](docs/lessons-learned.md).

---

## 🔮 Future improvements

- [ ] Bedrock **Agents** with Action Groups (ticket creation)
- [ ] **Amazon Cognito** for real user authentication
- [ ] Infrastructure as Code with **Terraform**
- [ ] CI/CD with **GitHub Actions**
- [ ] Automated answer evaluation (LLM-as-a-judge)
- [ ] Prompt versioning

---

## 🧹 Teardown

All resources are removable. The full cleanup checklist (including S3 versioned-object emptying and Knowledge Base deletion) is documented in the final phase — **nothing is left running**.

---

## 👤 Author

**Jefferson Santos Gondran** — Cloud Engineer in training | AWS portfolio

- 🔗 [LinkedIn](https://linkedin.com/in/jefferson-santos-2136b2264)
- 📧 <gondran.jefferson@gmail.com>

---

## 📄 License

MIT — see [LICENSE](LICENSE).
