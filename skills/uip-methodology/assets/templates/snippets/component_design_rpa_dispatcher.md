{%- set c = namespace(found=none) %}
{%- for item in (containers or []) %}
{%- if item.archetype == "rpa_dispatcher" and c.found is none %}
{%- set c.found = item %}
{%- endif %}
{%- endfor %}
{%- set f = c.found or {} %}
[TBD — one paragraph: what this dispatcher queries, when it runs, and the key deduplication decision.]

| Item | Decision | Rationale |
| --- | --- | --- |
| Source | [TBD — system / mailbox / API / database] | |
| Deduplication | Reference = [TBD]; skip if item already in queue | Prevents duplicate items when Dispatcher reruns before Performer drains the queue |
| On empty source | [TBD — complete silently / warn / alert] | |
| Schedule | {{ f.trigger or "[TBD]" }} | |
| Queue written | `{{ f.queue_writes or "[TBD]" }}` | |
| Config method | Orchestrator Assets / TOML | |
