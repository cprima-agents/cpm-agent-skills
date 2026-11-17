<!-- Example only (an invented invoice-posting project). Never rendered. A filled region looks like this. -->

### 4.2 `InvoicePosting_Performer` *(rpa_performer)*

One REFramework transaction = one vendor invoice. The queue item `Reference` carries the invoice number — used as the deduplication key and the correlation ID in all log messages.

SAP MIRO posting is **not idempotent** — retrying a failed post risks creating a duplicate FI document. Retry count in PROD is therefore 0. DEV/TEST allows 1 retry to recover from transient test-environment instability without incurring posting risk.

| Item | Decision | Rationale |
| --- | --- | --- |
| Retry count (PROD) | 0 | MIRO posting is not idempotent — a retry could produce a duplicate FI document |
| Retry count (DEV/TEST) | 1 | Tolerates transient SAP TST flakiness; no production risk |
| Max consecutive SE | 3 | Three consecutive faults indicate infrastructure failure — abort and page ops |
| ShouldMarkJobAsFaulted | true (PROD) | Ensures Orchestrator alerts ops when the abort threshold is reached |
| Multiple resolutions | No | SAP GUI requires 1920×1080; one standard resolution VM is sufficient at this volume |
| Queue read | `InvoicePosting` | |
| Config method | Orchestrator Assets / TOML | |

**Queue contract (read from `InvoicePosting`):**

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| Reference | string | yes | Invoice number — deduplication key; must never be blank |
| vendor_id | string | yes | SAP vendor account number |
| invoice_date | string | yes | DD.MM.YYYY — parsed to DateTime in Init stage |
| total_amount | string | yes | DE decimal format (1.234,56) — normalised to decimal in Init stage |
| currency | string | yes | EUR / USD / GBP — triggers BE-01 if outside this set |
| po_number | string | yes | Must exist in SAP MM03 — missing PO triggers BE-02 |
| source_email_id | string | no | IMAP Message-ID retained for traceability audit; not used in processing |
