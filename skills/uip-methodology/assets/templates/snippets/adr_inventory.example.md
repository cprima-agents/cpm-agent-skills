<!-- Example only (two invented decisions). Never rendered. A filled region looks like this. -->

| ID | Title | Status | Affects |
| --- | --- | --- | --- |
| ADR-0001 | Use REFramework for queue-based Performer projects | Accepted | sdd, tdd |
| ADR-0002 | Coded Config (TOML) for runtime settings | Accepted | tdd |

#### ADR-0001 — Use REFramework for queue-based Performer projects

**Status:** Accepted
**Affects:** sdd, tdd

**Context:** The Performer project processes Orchestrator queue transactions one at a time. A custom retry and state-management loop would replicate behaviour already provided by the standard UiPath REFramework.

**Decision:** Adopt REFramework as the Performer shell. Business logic lives exclusively in Process/ workflows invoked from Process Transaction. The Init, GetTransactionData, and SetTransactionStatus states are left intact; no modifications are made to the REFramework flow.

**Consequences:** Developers must understand REFramework state semantics. Non-standard retry logic is not permitted inside the Process Transaction state. Framework upgrades require re-baselining the shell from the current UiPath template.

#### ADR-0002 — Coded Config (TOML) for runtime settings

**Status:** Accepted
**Affects:** tdd

**Context:** Config.xlsx is fragile under source control: binary diffs are unreadable, merge conflicts cannot be resolved, and environment-specific values require a manual file overwrite at deploy time.

**Decision:** Replace Config.xlsx with per-environment TOML files (Config_Dev.toml, Config_Test.toml, Config_Prod.toml) loaded by a CodedConfig activity. TOML is plain text, diff-friendly, and supports typed values natively without extra parsing.

**Consequences:** Robots require .NET 8 and the CodedConfig NuGet package. All asset references migrate to TOML keys. The legacy Config.xlsx and its loading workflow are removed from the project.
