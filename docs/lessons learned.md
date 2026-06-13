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
