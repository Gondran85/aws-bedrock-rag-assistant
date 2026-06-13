# 🎓 Lessons Learned

> Updated at the end of every phase. Real lessons from building this project — not platitudes.

## Phase 1 — Use case & requirements

- **Justify the architecture before building it.** The first question is not "how do I build a RAG?" but "why RAG instead of keyword search, a static FAQ, or fine-tuning?". Being able to explain *why not the simpler option* is what separates a real project from a copied tutorial.
- **RAG wins when data changes often and citations are required.** HR policies change monthly; fine-tuning would freeze knowledge at training time. RAG retrieves the current document at query time and can cite sources — at a fraction of the cost.

## Phase 2 — Account hardening & identity

- **Lock the root user, work as an IAM identity.** Root has unrestricted power and cannot be limited by policy. It gets MFA, zero access keys, and is then left alone. Daily work happens under an IAM user with its own MFA.
- **IAM user = long-term credential (avoid); IAM role = temporary credential (prefer).** This distinction drives every later decision — the Knowledge Base and Lambda use roles, never hardcoded keys.
- **Always confirm the Region before creating anything.** Resources live inside a Region; creating in the wrong one produces invisible, orphaned, billing resources. us-east-1 was fixed for the broadest Bedrock catalog.

## Phase 3 — Cost guardrails & storage

- **Budget alerts come before the first resource, not after.** A USD 5 budget with layered alerts (50% / 80% actual, 100% forecasted) was armed first. Forecasted alerts need ~5 weeks of history to work — never rely on them alone in a fresh account.
- **"Stopped" is not "free".** Leftover stopped EC2 instances still bill for EBS volumes and public IPv4 addresses (~USD 3.6/month each, even idle). A clean teardown means checking three traps: orphaned EBS volumes (*Delete on termination* flag), unreleased Elastic IPs, and forgotten snapshots/AMIs.
- **Verify deletion in the bill, not the console.** Cost data lags up to 24h; the day-after check in Cost Explorer (daily granularity, flat zero) is what confirms a clean teardown.
- **Bedrock has no Free Tier.** Every embedding and generation token bills from the first call. Cost control in GenAI is per-call discipline, not instance scheduling.
- **Tools have distinct jobs:** Pricing Calculator estimates *before*, Budgets alerts *during*, Cost Explorer analyzes *after*.
- **The default vector store would have destroyed the budget.** Bedrock's classic Quick Create path provisions OpenSearch Serverless (fixed monthly cost even idle). Choosing S3 Vectors instead is the single most important cost decision in this project.
- **S3 charges for what's inside; EC2 charges for what's attached.** A small parked bucket costs cents; a parked instance keeps billing through its disks and IPs. Knowing *what exactly each service bills for* is the core of cost optimization.

## Phase 4 — Data preparation

- **Pretty for humans = noisy for machines.** The branded header bar ("ACME CORP — Human Resources") that makes the PDFs look professional was picked up by the text extractor (pdfplumber) as if it were document content. In a RAG pipeline this pollutes chunks: decorative layout becomes data. Decision: keep the noise intentionally to observe its effect on answers, then mitigate via parsing/chunking — rather than hiding the problem by pre-cleaning the source.
- **Always validate text extraction before ingestion.** A PDF that looks correct can still extract badly (merged columns, header/footer bleed, scrambled tables). Checking extraction first is the cheapest debugging there is.

## Phase 5 — Knowledge Base creation

- **S3 Vectors over OpenSearch Serverless saved ~USD 50/month of idle cost** — confirmed as the biggest cost decision. S3 Vectors trades ultra-low latency for cost; perfectly fine for internal Q&A.
- **A service role (not user credentials) grants the KB access** to S3 + Titan + the vector index. Least privilege in practice — the role exists only for the KB's tasks.
- **Chunking strategy is permanent.** It cannot be changed after the data source is created; changing it means recreating and re-ingesting. So it is a decision, not an experiment. Fixed-size (~300 tokens) chosen for short, well-sectioned documents.
- **Data deletion policy DELETE** removes vectors when the data source is deleted — the clean-teardown behavior (vs. RETAIN, which leaves orphaned vectors).
- **Teardown order matters:** delete the Knowledge Base BEFORE the S3 Vectors bucket, or the vector store can be left dangling.

## Phase 6 — First sync: 429 throttling (not a permissions error)

- **HTTP 429 "Too many requests" is rate limiting, not access denial.** Initial sync failed because new accounts have low default Bedrock throughput quotas; the sync's burst on the Titan embedding model exceeded them.
- **Diagnosis discipline by status code:** 403 = permission (fix IAM), 429 = rate (retry / raise quota), 400 = malformed request. Reading the code first avoids debugging the wrong layer — e.g., rewriting a perfectly correct IAM policy to fix a rate problem.
- **Fix: re-run Sync.** Throttling is transient.

<!-- Next phases append below -->

## Phase 6 (cont.) — Root cause: account-level quota = 0 (provisioning bug)

- **The 429 was not a burst problem — it was a provisioning bug.** Checked Service Quotas for Bedrock: every on-demand embeddings model (Titan V2, Titan G1, Titan/Nova Multimodal) showed **Applied account-level quota value = 0** while the AWS default is 2,000–6,000 RPM and 300,000 TPM. Quota 0 means every InvokeModel call is rejected, regardless of payload size.
- **Why batching would have wasted effort:** splitting the ingestion into one file at a time only reduces burst size. Against a quota of 0, one chunk fails exactly like one hundred. Verifying the quota first prevented pointless manual work.
- **Why switching embedding models would not help:** the zero quota is account-wide across all embedding models, not specific to Titan V2.
- **Diagnosis ladder for Bedrock 429:** (1) read the status code — 403=permission, 429=rate, 400=bad request; (2) check Service Quotas → Applied value; (3) if Applied is a normal number, it is real burst → retry with exponential backoff + jitter, or use cross-Region inference profiles; (4) if Applied is 0 and "Not adjustable", it is an account provisioning issue → wait for auto-initialization or open an AWS Support case.
- **Production-grade mitigations to cite:** exponential backoff with jitter on the client (the Lambda will implement this), and cross-Region inference profiles to spread load across Regions.
