#### Invoice

| Feld | Regel | Bei Fehler |
| --- | --- | --- |
| currency | muss einer von diesen Werten sein: EUR, USD, GBP | BusinessRuleException |
| invoice_number | entspricht dem Muster INV-YYYY-NNNNNN | BusinessRuleException |
| total_amount | > 0 | BusinessRuleException |
| po_number | 10-stellige Ziffernfolge | BusinessRuleException |

#### InvoiceLineItem

| Feld | Regel | Bei Fehler |
| --- | --- | --- |
| line_number | >= 1 | BusinessRuleException |
| quantity | > 0 | BusinessRuleException |
| unit_price | > 0 | BusinessRuleException |
| amount | > 0 | BusinessRuleException |
| po_item | 5-stellige Ziffernfolge mit führenden Nullen | BusinessRuleException |
