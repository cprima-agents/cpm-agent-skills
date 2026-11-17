# Technical Design Document (TDD)

**Process / Master Project Name:** {{ process_name or "[TBD]" }}

<!-- #region tdd_header -->
| Item | Value |
| --- | --- |
| TDD Version | 0.1 |
| TDD Date | [YYYY-MM-DD] |
| TDD Status | Draft |
| SDD Reference | [TBD] |
<!-- #endregion tdd_header -->

## Document History

<!-- #region tdd_history -->
| Version | Date | Author | Role | Changes |
| --- | --- | --- | --- | --- |
| 1.0 | [YYYY-MM-DD] | [TBD] | RPA Developer | Initial draft |
<!-- #endregion tdd_history -->

## Document Approvals

<!-- #region tdd_approvals -->
| Version | Role | Name | Department | Date |
| --- | --- | --- | --- | --- |
| 1.0 | Solution Architect | [TBD] | [TBD] | |
| 1.0 | Development Lead | [TBD] | [TBD] | |
<!-- #endregion tdd_approvals -->

## 1. Implementation Overview

### 1.1 Solution Structure

<!-- #region tdd_environment -->
| Item | Value |
| --- | --- |
| GitHub organization | [TBD] |
| GitHub repository | [TBD] |
| UiPath Studio version | [TBD] |
| Target robot version(s) | [TBD] |
| Expression language | [TBD] |
| Target framework | [TBD] |
| Workflow Analyzer ruleset | [TBD] |
| CI/CD configured | [TBD] |
| Development environment | [TBD] |
| Config method | [TBD] |
<!-- #endregion tdd_environment -->

### 1.2 Solution Components

| Component | Archetype | Entrypoint | Queue in | Queue out |
| --- | --- | --- | --- | --- |
| [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |

### 1.3 Entrypoints

Exact argument contract for every workflow file — authoritative source is `project.json`. Drives variable declarations and Invoke Workflow wiring. REFramework shell workflows (`Main.xaml`, `Init*`, `GetTransactionData.xaml`, `SetTransactionStatus.xaml`, `CloseAllApplications.xaml`) follow the standard REF contract; add them here only if their arguments deviate.

<!-- One row per entrypoint. In/Out columns list arguments as `name: Type` — asterisk (*) marks arguments with a default value defined in the XAML. Source: project.json entryPoints. -->

<!-- #region tdd_entrypoint_inventory -->
| Workflow | Stage | In | Out |
| --- | --- | --- | --- |
| [TBD] | [TBD] | [TBD] | [TBD] |
<!-- #endregion tdd_entrypoint_inventory -->

### 1.4 Branching Strategy

<!-- #region tdd_branching -->
| Branch | Pattern | Environment | Deploy trigger | Protected | Purpose |
| --- | --- | --- | --- | --- | --- |
| `main` | exact | Production | PR merge | yes | Stable release |
| `uat` | exact | UAT | PR merge | yes | Pre-release validation |
| `development` | `development*` | Development | push | no | Active development |
<!-- #endregion tdd_branching -->

### 1.5 Deployment Targets

| Environment | Orchestrator folder | Robot account | Target system(s) | Notes |
| --- | --- | --- | --- | --- |
| Development | [TBD] | [TBD] | [TBD] | |
| Test (UAT) | [TBD] | [TBD] | [TBD] | |
| Production | [TBD] | [TBD] | [TBD] | |

## 2. Domain Contracts

### 2.1 Domain Model

Record every domain entity the project works with — field names, types, identifiers, nullability, enum values, conversion rules, and DTO class path. This is the source of truth for DTO generation and workflow variable declarations.

<!-- For each entity: list all fields with type, required, identifier flag, nullability, enum values if applicable, wire format (e.g. DD.MM.YYYY), and a representative example. Add a conversions table for any field that requires type transformation at runtime. -->

<!-- #region tdd_data_model -->
#### [TBD]

**DTO:** [TBD]  
**Source:** [TBD]  
**Target:** [TBD]

##### Fields

| Field | Type | Required | Identifier | Nullable | Enum | Format | Example |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [TBD] | | | | | | | |

##### Conversions

| From | To | Rule | Lossless |
| --- | --- | --- | --- |
| [TBD] | | | |

##### C# Types

```csharp
// [TBD]
```
<!-- #endregion tdd_data_model -->

### 2.2 Field Mapping Contracts

| Source field | Source system | Target field | Target system | Transform |
| --- | --- | --- | --- | --- |
| [TBD] | | | | |

### 2.3 Validation Rules

One row per field-level guard. Enum membership checks are auto-derived from the domain model; explicit rows cover range, pattern, and length constraints. `on_failure` values: `BusinessRuleException`, `SystemException`, `Warn`, `Skip`.

<!-- #region tdd_validation_rules -->
#### [TBD]

| Field | Rule | On failure |
| --- | --- | --- |
| [TBD] | | |
<!-- #endregion tdd_validation_rules -->

### 2.4 Serialization and Formats

| Field | Wire format | Culture | Example |
| --- | --- | --- | --- |
| [TBD] | | | |

## 3. Component Implementation

One subsection per component from section 1.2. Structure follows the component's archetype.

### 3.1 `[TBD]` *(rpa_dispatcher)*

| Workflow | Responsibility | Input | Output |
| --- | --- | --- | --- |
| [TBD] | | | |

### 3.2 `[TBD]` *(rpa_performer)*

REFramework-based. One transaction = one queue item. Queue item Reference = [TBD].

#### initialize

[TBD]

#### ingest

[TBD]

#### enrich

[TBD]

#### decide

[TBD]

#### execute

[TBD]

#### complete

[TBD]

#### finalize

[TBD]

### 3.3 `[TBD]` *(rpa_aggregator)* *(optional)*

| Workflow | Responsibility | Input | Output |
| --- | --- | --- | --- |
| [TBD] | | | |

## 4. Integration Implementation

### 4.1 Application Automation

| Operation | Scope | Surface | Adapter | Notes |
| --- | --- | --- | --- | --- |
| [TBD] | | | | |

### 4.2 Email Handling

| Mailbox | Protocol | Folder | Filter | Output |
| --- | --- | --- | --- | --- |
| [TBD] | | | | |

### 4.3 File Processing

| File type | Source | Method | Output |
| --- | --- | --- | --- |
| [TBD] | | | |

### 4.4 Queue Contracts

| Queue | Direction | Item schema | Max retries | Dead-letter |
| --- | --- | --- | --- | --- |
| [TBD] | | | | |

### 4.5 External APIs *(optional)*

| API | Endpoint | Auth | Notes |
| --- | --- | --- | --- |
| [TBD] | | | |

## 5. Exception and Recovery Implementation

### 5.1 Business Exceptions

| Exception | Condition | Queue status | Notification |
| --- | --- | --- | --- |
| [TBD] | | | |

### 5.2 System Exceptions

| Exception | Condition | Retry | On exhaustion |
| --- | --- | --- | --- |
| [TBD] | | | |

### 5.3 Retry Logic

| Scope | Max retries | Strategy | Config key |
| --- | --- | --- | --- |
| Transaction (REF) | [TBD] | [TBD] | `MaxRetryNumber` |
| GetTransactionItem | [TBD] | [TBD] | `RetryNumberGetTransactionItem` |
| SetTransactionStatus | [TBD] | [TBD] | `RetryNumberSetTransactionStatus` |
| Consecutive system exceptions | [TBD] | [TBD] | `MaxConsecutiveSystemExceptions` |

### 5.4 Logging and Evidence

| Event | Log level | Evidence | Notes |
| --- | --- | --- | --- |
| Transaction start | INFO | [TBD] | |
| Business exception | WARN | [TBD] | |
| System exception | ERROR | [DEFAULT: screenshot + stack trace] | saved to `ExScreenshotsFolderPath` |
| Job end | INFO | [DEFAULT: transaction count, success/fail totals] | |

## 6. Configuration and Dependencies

Config class `CodedConfig` — generated by ConFormMold from per-environment TOML files (`Config_Dev.toml`, `Config_Test.toml`, `Config_Prod.toml`). Loaded at robot startup via `CodedConfig.Load()`. Pass `--config-dev`, `--config-test`, `--config-prod` to `cpm-rpa render` to populate automatically.

<!-- #region tdd_process_configuration -->
#### Settings

| Property | Type | DEV | TEST | PROD |
| --- | --- | --- | --- | --- |
| [TBD] | | | | |

#### Constants

| Property | Type | DEV | TEST | PROD |
| --- | --- | --- | --- | --- |
| [TBD] | | | | |

#### Assets

| Property | Type | DEV | TEST | PROD |
| --- | --- | --- | --- | --- |
| [TBD] | | | | |
<!-- #endregion tdd_process_configuration -->

### 6.4 UiPath Dependencies

UiPath activity packages — authoritative source is `project.json`. Runtime rule: Strict = only the pinned version is used; Lowest Applicable Version = resolves upward if exact version is unavailable.

<!-- #region tdd_uipath_dependencies -->
| Package | Version | Rule | Purpose |
| --- | --- | --- | --- |
| `UiPath.Excel.Activities` | [2.24.3] | Strict | Excel read/write |
| `UiPath.Mail.Activities` | [2.2.10] | Strict | Email via SMTP / IMAP / Exchange |
| `UiPath.MicrosoftOffice365.Activities` | [2.7.24] | Strict | Microsoft 365 — Mail, Teams, SharePoint |
| `UiPath.System.Activities` | [24.10.4] | Strict | Core workflow activities |
| `UiPath.Testing.Activities` | [24.10.4] | Strict | Test automation framework |
| `UiPath.UIAutomation.Activities` | [25.10.12] | Strict | UI automation — desktop and web |
<!-- #endregion tdd_uipath_dependencies -->

### 6.5 Reused Components / Libraries

Non-UiPath library dependencies — sourced from `project.json`. Internal libraries and third-party packages that are not standard UiPath activity packages.

<!-- #region tdd_reused_libraries -->
n/a — no non-UiPath library dependencies.
<!-- #endregion tdd_reused_libraries -->

### 6.6 New Reusable Components

| Component | Purpose | Placeholder in Automation Hub |
| --- | --- | --- |
| [TBD] | | |

## 7. Test Contracts

### 7.1 Unit-Test Scenarios

| # | Scenario | Input | Expected outcome |
| --- | --- | --- | --- |
| [TBD] | | | |

### 7.2 Integration-Test Scenarios

| # | Scenario | Precondition | Expected outcome |
| --- | --- | --- | --- |
| [TBD] | | | |

### 7.3 Test Data Requirements

| Dataset | Source | Volume | Notes |
| --- | --- | --- | --- |
| [TBD] | | | |

### 7.4 Acceptance Conditions

| # | Condition | Verification method |
| --- | --- | --- |
| [TBD] | | |
| [TBD] | [DEFAULT: No hardcoded credentials] | [DEFAULT: Static code analysis + credential scan] |

## 8. Operational Readiness

### 8.1 Deployment Parameters

<!-- #region tdd_deployment_parameters -->
| Item | Value |
| --- | --- |
| Production environment | [TBD] |
| Trigger / Schedule | [TBD] |
| Process input | [TBD] |
| Expected output | [TBD] |
| Orchestrator queues | [TBD] |
| Orchestrator asset names | [TBD] |
| Credentials storage | [DEFAULT: Orchestrator Assets (Credential type) — never hardcoded] |
| Multiple resolutions supported | [TBD] |
| Recommended resolution | [TBD] |
<!-- #endregion tdd_deployment_parameters -->

### 8.2 Monitoring Hooks

| Hook | Trigger | Target | Notes |
| --- | --- | --- | --- |
| [TBD] | | | |

### 8.3 Support Requirements

| Requirement | Details |
| --- | --- |
| [TBD] | |

## 9. Open Technical Issues

<!-- #region observations_issues -->
*No open issues.*
<!-- #endregion observations_issues -->
