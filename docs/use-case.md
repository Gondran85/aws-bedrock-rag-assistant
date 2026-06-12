# 🎯 Use Case & Requirements

## The problem

Acme Corp's HR team spends hours every week answering repetitive questions about internal policies (vacation, remote work, expense reimbursement, code of conduct). The documents exist as PDFs, but employees can't find answers because **keyword search fails when the question's wording differs from the document's wording** — e.g., an employee asks *"can I take the Friday off after a holiday?"* while the policy says *"bridge days"*.

**Goal:** a web assistant where employees ask questions in natural language and receive answers grounded **exclusively** in the official documents, with source citations — at near-zero cost.

## Why this approach (alternatives rejected)

| Alternative | Why it is not enough |
|---|---|
| 🔍 **Keyword search** (Ctrl+F, lexical search) | No literal match → no result. Semantic search with embeddings captures *meaning*, not spelling |
| 📃 **Static FAQ** | Doesn't scale: every new question requires manual editing |
| 🔧 **Fine-tuning a model** | Expensive, slow, and knowledge freezes at training time. Policies change monthly → **RAG retrieves the *current* document at query time** |
| 🏗️ **Training a model from scratch** | Orders of magnitude more expensive; doesn't even guarantee citations |

**Decision: RAG (Retrieval-Augmented Generation) with Amazon Bedrock Knowledge Bases.**
Exam connection (AIF-C01, Domain 3): *frequently changing data + need for source citations + limited budget → RAG, not fine-tuning.*

## Functional requirements

1. ❓ User asks questions in natural language through a web page
2. 📚 Answers are grounded **only** in the internal documents, with source citation
3. 🚫 If the answer is not in the documents, the system says so — it never invents (anti-hallucination)
4. 🗂️ Question history is stored

## Non-functional requirements

| Requirement | Target |
|---|---|
| 💰 Total project cost | **< USD 5** |
| ⚡ Response latency | < 10 s |
| 🔒 Data exposure | Zero public access to documents |
| 🛡️ Permissions | Least privilege on every role |
| 🧹 Reversibility | 100% of resources removable at teardown |

## Users & business value

**Users:** Acme Corp employees consulting HR policies.
**Value:** HR hours saved + consistent, auditable answers across the company.
