# Sample data — Acme Corp HR policies

The knowledge base is grounded in four fictional HR policy documents for a made-up company, **Acme Corp**. They were written specifically for this project — no real company data is used. The PDFs live in the documents bucket under `hr-policies/` and are the only source the assistant retrieves from.

> All content is fictional and exists solely to demonstrate retrieval-augmented generation over private documents.

## Documents

| File | Topic | Example questions it answers |
|---|---|---|
| `vacation-policy.pdf` | Paid time off, accrual, carry-over, bridge days | "How many vacation days do I get in my first year?" |
| `remote-work-policy.pdf` | Eligibility, equipment, working hours, in-office days | "How many days a week can I work from home?" |
| `expense-reimbursement-policy.pdf` | What is reimbursable, limits, approval, deadlines | "Can I expense home internet while working remotely?" |
| `code-of-conduct.pdf` | Professional conduct, confidentiality, reporting | "Who do I contact to report a conduct concern?" |

## Key facts (so answers can be verified against the source)

These are the ground-truth values an answer should match once the system runs in live mode. They are intentionally specific so retrieval accuracy can be checked.

**Vacation policy**
- Full-time employees accrue **20 vacation days** in their first year, rising to **22** after one year of service.
- Up to **5 unused days** may be carried over into the next year; the rest expire.
- A **bridge day** is a working day between a public holiday and a weekend that the company designates as paid time off.

**Remote-work policy**
- Eligible employees may work remotely up to **3 days per week**, with at least **2 in-office days**.
- The company provides a laptop and a one-time **home-office stipend**; ongoing internet costs are addressed in the expense policy.

**Expense-reimbursement policy**
- Home internet is **partially reimbursable** for approved remote workers, up to a monthly cap.
- Expenses must be submitted within **30 days** with a receipt and manager approval.

**Code of conduct**
- Confidential information must not be shared outside the company.
- Conduct concerns are reported to the employee's manager or to HR; anonymous reporting is available.

## How the data is used

1. The four PDFs are uploaded to Amazon S3 (`hr-policies/`).
2. The Bedrock Knowledge Base ingests them: text is extracted, split into chunks, embedded with **Titan Text Embeddings V2**, and stored in **Amazon S3 Vectors**.
3. At query time, the user's question is embedded, the most relevant chunks are retrieved, and the foundation model (**Amazon Nova Lite**) generates an answer grounded in those chunks — returning the source document as a citation.

> **Note on the PDFs:** the source files include deliberate header/footer "noise" so the project exercises real-world text-extraction behaviour, not an idealized clean document.
