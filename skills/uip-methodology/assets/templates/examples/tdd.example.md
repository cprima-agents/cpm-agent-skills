# TDD example — what the filled sections look like

Sample content (an invoice-posting robot) for the static sections of `tdd-template.md`. It is never rendered. The
snippet-backed regions have their own examples next to their snippets: `snippets/tdd_*.example.md`.

### 1.2 Solution Components

| Component | Archetype | Entrypoint | Queue in | Queue out |
| --- | --- | --- | --- | --- |
| `InvoicePosting.Dispatcher` | rpa_dispatcher | `Dispatcher.xaml` | — | InvoicePosting |
| `InvoicePosting.Performer` | rpa_performer | `Performer.xaml` | InvoicePosting | — |
| `InvoicePosting.Aggregator` | rpa_aggregator | `Aggregator.xaml` | — | — |

### 1.5 Deployment Targets

| Environment | Orchestrator folder | Robot account | SAP system | Notes |
| --- | --- | --- | --- | --- |
| Development | cg371p/Dev | cg371p | DEV (100) | SAP adapter: mock |
| Test (UAT) | cg371p/Test | cg371p | TST (200) | SAP adapter: live |
| Production | cg371p/Shared | cg371p | PRD (300) | SAP adapter: live |

### 2.2 Field Mapping Contracts

| Source field | Source system | Target field | Target system | Transform |
| --- | --- | --- | --- | --- |
| invoice_number | AP mailbox subject | InvoiceNumber | SAP MIRO | none |
| total_amount | PDF | TotalAmount | SAP MIRO | DE decimal → decimal |
| invoice_date | PDF | InvoiceDate | SAP MIRO | DD.MM.YYYY → DateTime |

### 2.4 Serialization and Formats

| Field | Wire format | Culture | Example |
| --- | --- | --- | --- |
| invoice_date | DD.MM.YYYY | de-DE | 15.01.2024 |
| total_amount | #.##0,00 | de-DE | 1.234,56 |
| unit_price | #.##0,00 | de-DE | 12,50 |
| po_item | 5-digit zero-padded | — | 00010 |

### 3.1 `InvoicePosting.Dispatcher` *(rpa_dispatcher)*

| Workflow | Responsibility | Input | Output |
| --- | --- | --- | --- |
| `Process/ReadMailbox.xaml` | Read unread emails from AP mailbox | Mailbox folder name | List of MailMessage |
| `Process/ExtractInvoice.xaml` | Extract InvoiceDto from email + PDF | MailMessage | InvoiceDto |
| `Process/EnqueueInvoice.xaml` | Add InvoiceDto to Orchestrator queue | InvoiceDto, queue name | QueueItem reference |

### 3.2 `InvoicePosting.Performer` *(rpa_performer)*

REFramework-based. One transaction = one InvoicePosting queue item. Queue item Reference = invoice_number.

#### initialize

Fetch credentials (`cred_SAP_Prod`, `cred_SMTP`) from Orchestrator Assets. Load `CodedConfig`. Verify SAP logon.

#### ingest

Deserialize queue item JSON payload into `InvoiceDto`. Validate required fields; throw `BusinessRuleException` on violation.

#### enrich

Look up PO header in SAP MM03 to confirm po_number exists and is open. Resolve vendor_id to SAP vendor account number.

#### decide

Apply routing rules: reject if total_amount ≤ 0 or po_number missing → `BusinessRuleException`. Route to manual handling if currency ∉ {EUR, USD, GBP}.

#### execute

Navigate to SAP MIRO. Enter invoice header (vendor, date, amount, currency). Post line items. Capture FI document number. Take screenshot on failure.

#### complete

Set queue item status to Succeeded with output `{fi_document: "...", posted_at: "..."}`. Log INFO with FI document number.

#### finalize

Close SAP MIRO tab. Clear clipboard. Log session summary.

### 3.3 `InvoicePosting.Aggregator` *(rpa_aggregator)* *(optional)*

| Workflow | Responsibility | Input | Output |
| --- | --- | --- | --- |
| `Aggregator.xaml` | Generate daily posting summary report | Report date, output folder | XLSX report file |

### 4.1 SAP Automation

| Transaction | Scope | Surface | SAP adapter | Notes |
| --- | --- | --- | --- | --- |
| MIRO | Invoice posting | UI (SAP GUI) | mock (DEV) / live (TEST, PROD) | Uses CPMForge.SAP library |
| MM03 | PO lookup / validation | UI (SAP GUI) | mock (DEV) / live (TEST, PROD) | Read-only |

### 4.2 Email Handling

| Mailbox | Protocol | Folder | Filter | Output |
| --- | --- | --- | --- | --- |
| AP mailbox | IMAP / Exchange | Inbox | Subject contains "Invoice" | MailMessage list |

### 4.3 File Processing

| File type | Source | Method | Output |
| --- | --- | --- | --- |
| PDF (invoice) | Email attachment | Document Understanding / regex extraction | InvoiceDto fields |

### 4.4 Queue Contracts

| Queue | Direction | Item schema | Max retries | Dead-letter |
| --- | --- | --- | --- | --- |
| InvoicePosting | Performer input | InvoiceDto (JSON) | 0 (PROD), 1 (DEV/TEST) | Shared/dead-letter |
| InvoicePosting_Dispatcher | Dispatcher output | InvoiceDto (JSON) | — | — |

### 5.1 Business Exceptions

| Exception | Condition | Queue status | Notification |
| --- | --- | --- | --- |
| InvalidInvoiceNumber | invoice_number null or wrong format | Failed | SMTP alert to AP team |
| MissingPoNumber | po_number null or PO not found in SAP | Failed | SMTP alert to AP team |
| UnsupportedCurrency | currency ∉ {EUR, USD, GBP} | Failed | SMTP alert |

### 5.2 System Exceptions

| Exception | Condition | Retry | On exhaustion |
| --- | --- | --- | --- |
| SapLoginException | SAP logon fails | up to MaxConsecutiveSystemExceptions | Faulted job |
| SapTimeoutException | MIRO screen timeout | up to MaxConsecutiveSystemExceptions | Faulted job |

### 5.3 Retry Logic

| Scope | Max retries | Strategy | Config key |
| --- | --- | --- | --- |
| Transaction (REF) | 0 (PROD), 1 (DEV/TEST) | immediate re-queue | `MaxRetryNumber` |
| GetTransactionItem | 2 | immediate | `RetryNumberGetTransactionItem` |
| SetTransactionStatus | 2 | immediate | `RetryNumberSetTransactionStatus` |
| Consecutive system exceptions | 3 | abort job | `MaxConsecutiveSystemExceptions` |

### 5.4 Logging and Evidence

| Event | Log level | Evidence | Notes |
| --- | --- | --- | --- |
| Transaction start | INFO | queue item Reference | |
| SAP FI document posted | INFO | FI document number | |
| Business exception | WARN | exception message + invoice_number | |
| System exception | ERROR | screenshot + stack trace | saved to `ExScreenshotsFolderPath` |
| Job end | INFO | transaction count, success/fail totals | |

### 7.1 Unit-Test Scenarios

| # | Scenario | Input | Expected outcome |
| --- | --- | --- | --- |
| U-01 | Valid invoice parses correctly | Invoice PDF with all required fields | InvoiceDto populated, no exception |
| U-02 | Missing PO number throws BusinessRuleException | InvoiceDto with po_number = null | BusinessRuleException |
| U-03 | DE decimal normalisation | "1.234,56" | 1234.56m |

### 7.2 Integration-Test Scenarios

| # | Scenario | Precondition | Expected outcome |
| --- | --- | --- | --- |
| I-01 | End-to-end posting on SAP TST | Valid invoice queue item, SAP TST accessible | FI document created, item = Succeeded |
| I-02 | Invalid PO rejected cleanly | Queue item with non-existent PO | Item = Failed, SMTP alert sent |

### 7.3 Test Data Requirements

| Dataset | Source | Volume | Notes |
| --- | --- | --- | --- |
| Invoice PDFs (valid) | Sample AP emails | ≥ 10 | Cover EUR / USD / GBP currencies |
| Invoice PDFs (invalid) | Synthetic | ≥ 5 | Missing PO, wrong format, zero amount |
| SAP MIRO test vendors | SAP TST | ≥ 3 | Must have open POs |

### 7.4 Acceptance Conditions

| # | Condition | Verification method |
| --- | --- | --- |
| A-01 | All valid invoices post without manual intervention | I-01 integration test pass rate = 100% |
| A-02 | Business exceptions produce SMTP alert within 5 min | I-02 test + inbox check |
| A-03 | No hardcoded credentials | Static code analysis + credential scan |

### 8.2 Monitoring Hooks

| Hook | Trigger | Target | Notes |
| --- | --- | --- | --- |
| Job faulted alert | ShouldMarkJobAsFaulted = true | Orchestrator alert / SMTP | PROD only |
| Business exception alert | BusinessRuleException caught | SMTP → AP team | All environments |

### 8.3 Support Requirements

| Requirement | Details |
| --- | --- |
| Robot account access | cg371p must be whitelisted on SAP PRD and AP mailbox |
| Orchestrator queue monitoring | Dead-letter queue Shared/dead-letter reviewed daily |
| Screenshot retention | Exceptions_Screenshots folder — 30-day retention |
