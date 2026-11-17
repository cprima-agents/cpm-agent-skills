<!-- Example only (an invented invoice-posting project). Never rendered. A filled region looks like this. -->

### 4.4 `SAPPosting.Library` *(rpa_library)*

Provides reusable SAP GUI automation workflows for the Invoice Posting solution — consumed by `InvoicePosting_Performer`. Packaged as a NuGet library so the posting logic can be tested and versioned independently from the Performer's REFramework shell.

| Item | Decision | Rationale |
| --- | --- | --- |
| NuGet package ID | `DHL.RPA.AP.SAPPosting` | Follows DHL team namespace convention |
| Exported workflows | `PostInvoice(vendor_id: string, amount: decimal, gl_account: string) → posted: boolean, doc_number: string` | Single entry point; all SAP navigation encapsulated inside |
| Consumers | `InvoicePosting_Performer` | Dispatcher has no SAP interaction; library is Performer-only |
| Framework | XAML (UI Automation activities) | SAP GUI requires XAML for selector-based navigation |
| Config passing | Arguments only — no Orchestrator Assets | Performer retrieves config from Assets/TOML and passes it as arguments |
| Versioning strategy | SemVer — breaking argument changes bump major version | Prevents silent breakage when Performer is upgraded separately |
