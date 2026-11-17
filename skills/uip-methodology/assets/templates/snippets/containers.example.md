| Component | Archetype | Framework | Trigger | Queue boundary |
| --- | --- | --- | --- | --- |
| InvoicePosting_Dispatcher | rpa_dispatcher | Linear | Schedule 05:45 CET Mon–Fri | writes → `InvoicePosting` |
| InvoicePosting_Performer | rpa_performer | REFramework | Queue — `InvoicePosting` | reads ← `InvoicePosting` |
| InvoicePosting_Aggregator | rpa_aggregator | Linear | Schedule 08:30 CET Mon–Fri | reads ← `InvoicePosting` (completed items) |
