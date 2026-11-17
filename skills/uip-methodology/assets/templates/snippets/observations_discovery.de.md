{%- set items = observations | by_kind('observation') if observations else [] %}
{%- if items %}
| ID | Kategorie | Beobachtung | Auswirkung | Verantwortlich | Status |
| --- | --- | --- | --- | --- | --- |
{%- for item in items %}
| `{{ item.id or gen_id('obs', item.title) }}` | {{ item.category or "" }} | {{ item.title }} | {{ item.impact or "" }} | {{ item.owner or item.resolution_owner or "" }} | {{ item.status or "New" }} |
{%- endfor %}
{%- else %}
[TBD — Überwachung, Revision, Compliance oder fachspezifische Beobachtungen aus den Prozessinterviews]
{%- endif %}
