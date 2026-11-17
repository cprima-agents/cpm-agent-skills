| Step | Input | Description | Next Step | On Exception | Pipeline Stage | Business Rule |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Email with invoice PDF | Open SAP inbox | 2 | | ingest | |
| 2 | Email | Validate PO number in SAP | 3 | BE-01 | decide | PO must exist before posting |
| 3 | PO data | Post invoice in SAP MIRO | END | SE-01 | execute | |
| BE-01 | — | Log missing PO, skip transaction | END | | | |
| SE-01 | — | SAP login failed, retry | 3 | END | | |
