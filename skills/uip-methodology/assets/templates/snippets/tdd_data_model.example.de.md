#### Invoice

**DTO:** `CpmRpa.InvoicePosting.Domain.InvoiceDto`  
**Quelle:** SAP ECC — AP-Postfach (E-Mail + PDF-Anhang)  
**Ziel:** SAP ECC — Transaktion MIRO (FI-Beleg)

##### Felder

| Feld | Typ | Pflicht | Kennung | Nullable | Enum | Format | Beispiel |
| --- | --- | --- | --- | --- | --- | --- | --- |
| invoice_number | string | true | true | false | | | INV-2024-001234 |
| invoice_date | date → DateTime | true | false | false | | DD.MM.YYYY | 15.01.2024 |
| total_amount | number → decimal | true | false | false | | | 1.234,56 |
| currency | enum | true | false | false | EUR, USD, GBP | | EUR |
| vendor_id | string | true | false | false | | | VEND-001 |
| po_number | string | true | false | false | | | 4500012345 |
| line_items | list<InvoiceLineItem> | false | false | true | | | |

##### Umwandlungen

| Von | Nach | Regel | Verlustfrei |
| --- | --- | --- | --- |
| total_amount | decimal | Tausendertrennzeichen (.) entfernen und das Dezimalkomma (,) durch einen Punkt ersetzen. Währungssymbole entfernen. | true |
| invoice_date | DateTime | DD.MM.YYYY mit CultureInfo.GetCultureInfo("de-DE") einlesen. | true |

##### C#-Typen

```csharp
public class InvoiceDto
{
    public string InvoiceNumber { get; set; } = string.Empty;
    public DateTime InvoiceDate { get; set; }
    public decimal TotalAmount { get; set; }
    public string Currency { get; set; } = string.Empty;
    public string VendorId { get; set; } = string.Empty;
    public string PoNumber { get; set; } = string.Empty;
    public List<InvoiceLineItemDto>? LineItems { get; set; }
}
```

#### InvoiceLineItem

**DTO:** `CpmRpa.InvoicePosting.Domain.InvoiceLineItemDto`  
**Quelle:** SAP ECC — PDF-Anhang der Rechnung (Tabelle der Positionen)  
**Ziel:** keines (Unterentität, nur lesend)

##### Felder

| Feld | Typ | Pflicht | Kennung | Nullable | Enum | Format | Beispiel |
| --- | --- | --- | --- | --- | --- | --- | --- |
| line_number | integer | true | true | false | | | 1 |
| description | string | false | false | true | | | Büromaterial Q1 |
| quantity | number | true | false | false | | | 10.0 |
| unit_price | number → decimal | true | false | false | | | 12,50 |
| amount | number → decimal | true | false | false | | | 125,00 |
| tax_code | string | false | false | true | | | V1 |
| po_item | string | true | false | false | | 5-stellig, mit führenden Nullen | 00010 |

##### Umwandlungen

| Von | Nach | Regel | Verlustfrei |
| --- | --- | --- | --- |
| unit_price | decimal | Deutsches Dezimalformat — gleiche Normalisierung wie Invoice.total_amount. | true |
| amount | decimal | Deutsches Dezimalformat — gleiche Normalisierung wie Invoice.total_amount. | true |

##### C#-Typen

```csharp
public class InvoiceLineItemDto
{
    public int LineNumber { get; set; }
    public string? Description { get; set; }
    public double Quantity { get; set; }
    public decimal UnitPrice { get; set; }
    public decimal Amount { get; set; }
    public string? TaxCode { get; set; }
    public string PoItem { get; set; } = string.Empty;
}
```
