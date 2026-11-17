{%- set c = namespace(found=none) %}
{%- for item in (containers or []) %}
{%- if item.archetype == "rpa_performer" and c.found is none %}
{%- set c.found = item %}
{%- endif %}
{%- endfor %}
{%- set f = c.found or {} %}
One REFramework transaction = one [TBD — business entity]. The queue item `Reference` carries [TBD — unique field] — used as the deduplication key and the correlation ID in all log messages.

[TBD — one sentence on idempotency: state whether the target write is idempotent and what retry policy that implies.]

| Item | Decision | Rationale |
| --- | --- | --- |
| Retry count (PROD) | [TBD — 0 if target is not idempotent] | [TBD — state why retrying is safe or unsafe for this target system] |
| Retry count (DEV/TEST) | [TBD — typically 1] | Recovers from transient test-environment flakiness |
| Max consecutive SE | 3 | Three consecutive faults indicate infrastructure failure — abort and page ops |
| ShouldMarkJobAsFaulted | true (PROD) | Ensures Orchestrator alerts ops when the abort threshold is reached |
| Multiple resolutions | [TBD — Yes / No] | [TBD — state tested resolution if No] |
| Queue read | `{{ f.queue_reads or "[TBD]" }}` | |
| Config method | Orchestrator Assets / TOML | |

**Queue contract (read from `{{ f.queue_reads or "[TBD]" }}`):**

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| Reference | string | yes | [TBD — unique key; must never be blank] |
| [TBD field] | string | yes | |
