| Item | Value |
| --- | --- |
| Production environment | UiPath Orchestrator — cg371p / Shared (Production tenant) |
| Trigger / Schedule | Daily 06:00 CET Mon–Fri via Orchestrator time trigger |
| Process input | Orchestrator queue InvoicePosting — items enqueued by Dispatcher |
| Expected output | SAP MIRO FI document posted; queue item set to Succeeded |
| Orchestrator queues | InvoicePosting (Performer), InvoicePosting_Dispatcher (Dispatcher) |
| Orchestrator asset names | cg371p/cred_SAP_Prod, cg371p/cred_SMTP |
| Credentials storage | Orchestrator Assets (Credential type) — never hardcoded |
| Multiple resolutions supported | No — tested on 1920×1080 |
| Recommended resolution | 1920×1080 |
