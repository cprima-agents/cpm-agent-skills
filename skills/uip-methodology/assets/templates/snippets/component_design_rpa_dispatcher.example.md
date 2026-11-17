<!-- Example only (an invented invoice-posting project). Never rendered. A filled region looks like this. -->

### 4.1 `InvoicePosting_Dispatcher` *(rpa_dispatcher)*

Reads the AP inbox, extracts invoice metadata from each email–PDF pair, and enqueues one item per invoice. Runs at 05:45 CET so the queue is populated before the 06:00 CET Performer trigger. Deduplication happens here — the Performer never checks for duplicates.

| Item | Decision | Rationale |
| --- | --- | --- |
| Source | AP mailbox — IMAP, folder Inbox, subject filter "Invoice" | Business confirmed all invoices arrive via this single channel |
| Deduplication | Reference = invoice_number; skip if item already in queue | Prevents double-posting when Dispatcher reruns before Performer drains the queue |
| On empty mailbox | Complete silently | No invoices is normal on public holidays — an alert would create noise |
| Schedule | 05:45 CET Mon–Fri | 15 min lead time ensures queue is populated before Performer trigger |
| Queue written | `InvoicePosting` | |
| Config method | Orchestrator Assets / TOML | |
