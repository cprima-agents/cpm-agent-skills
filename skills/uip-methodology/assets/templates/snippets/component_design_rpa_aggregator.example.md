<!-- Example only (an invented invoice-posting project). Never rendered. A filled region looks like this. -->

### 4.3 `InvoicePosting_Aggregator` *(rpa_aggregator)*

Generates a daily posting summary after all Performer transactions complete. Triggered by a scheduled job 30 minutes after the Performer stop-signal, giving the last transactions time to close.

| Item | Decision | Rationale |
| --- | --- | --- |
| Trigger | Scheduled — 08:30 CET Mon–Fri | 30 min after Performer stop signal; allows last transactions to settle |
| Input | Orchestrator queue `InvoicePosting` — Succeeded and Failed items from today's run | |
| Output | XLSX report emailed to AP team distribution list | Format requested by business; no dashboard tooling available yet |
| Config method | Orchestrator Assets / TOML | |
