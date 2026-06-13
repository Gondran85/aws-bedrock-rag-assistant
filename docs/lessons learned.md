## Phase 4 — Data preparation

- **Pretty for humans = noisy for machines.** The branded header bar
  ("ACME CORP — Human Resources") that makes the PDFs look professional was
  picked up by the text extractor (pdfplumber) as if it were document content.
  In a RAG pipeline this pollutes chunks: decorative layout becomes data.
  Decision: keep the noise intentionally to observe its effect on answers in
  the query phase, then mitigate via the Knowledge Base parsing/chunking
  strategy — rather than hiding the problem by pre-cleaning the source.
- **Always validate text extraction before ingestion.** A PDF that looks
  correct can still extract badly (merged columns, header/footer bleed,
  scrambled tables). Checking extraction first is the cheapest debugging you
  will ever do.
## Phase 6 — Bedrock model access (platform change observed)
- The manual "Model access" enablement step was retired by AWS. Serverless
  foundation models are now auto-enabled on first invocation in any commercial
  region. Anthropic (Claude) still requires first-time use-case submission.
- Exam-relevant: restricting *which* models a team may use is still done via
  IAM policies / SCPs — the default just flipped from deny-until-enabled to
  allow-until-restricted.
  ## Phase 6 — Knowledge Base creation
- S3 Vectors over OpenSearch Serverless saved ~$50/month of idle cost — the
  single biggest cost decision. S3 Vectors trades ultra-low latency for cost;
  fine for internal Q&A.
- Service role (not user credentials) grants the KB access to S3 + Titan +
  vector index — least privilege in practice.
- Teardown order matters: delete the Knowledge Base BEFORE the S3 Vectors
  bucket, or the vector store can be left dangling.
  ## Phase 6 — First sync: 429 throttling (not a permissions error)
- Initial sync failed with HTTP 429 "Too many requests" on the Titan embedding
  model. This is RATE LIMITING, not access denial. New accounts have low
  default Bedrock throughput quotas; the sync's burst exceeded them.
- Diagnosis discipline: 403 = permission (fix IAM), 429 = rate (retry/raise
  quota), 400 = malformed request. Reading the status code first avoids
  debugging the wrong layer.
- Fix: re-run Sync. Throttling is transient.
