{%- set c = namespace(found=none) %}
{%- for item in (containers or []) %}
{%- if item.archetype == "rpa_aggregator" and c.found is none %}
{%- set c.found = item %}
{%- endif %}
{%- endfor %}
{%- set f = c.found or {} %}
[TBD — one paragraph: what this aggregator collects, when it runs relative to the Performer, and what it produces.]

| Item | Decision | Rationale |
| --- | --- | --- |
| Trigger | {{ f.trigger or "[TBD — scheduled after Performer / queue-depth signal]" }} | |
| Input | [TBD — Orchestrator queue results / output file / API] | |
| Output | [TBD — report file / email / downstream API call] | |
| Config method | Orchestrator Assets / TOML | |
