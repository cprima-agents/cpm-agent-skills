{%- set items = observations | by_kind('removal') if observations else [] %}
{%- if items %}
| ID | Entfernter Punkt | Grund | Auswirkung |
| --- | --- | --- | --- |
{%- for item in items %}
| `{{ item.id or gen_id('obs', item.title) }}` | {{ item.title }} | {{ item.description or "" }} | {{ item.impact or "" }} |
{%- endfor %}
{%- else %}
*Nichts wurde aus dem Umfang genommen.*
{%- endif %}
