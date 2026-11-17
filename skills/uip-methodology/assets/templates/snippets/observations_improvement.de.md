{%- set items = observations | by_kind('improvement') if observations else [] %}
{%- if items %}
| ID | Verbesserung | Beschreibung | Verantwortlich | Status |
| --- | --- | --- | --- | --- |
{%- for item in items %}
| `{{ item.id or gen_id('obs', item.title) }}` | {{ item.title }} | {{ item.description or "" }} | {{ item.owner or "" }} | {{ item.status or "offen" }} |
{%- endfor %}
{%- else %}
- [ ] [TBD]
- [ ] [TBD]
{%- endif %}
