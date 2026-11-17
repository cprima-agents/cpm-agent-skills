{%- if in_scope %}
| Schritt | Beschreibung |
| --- | --- |
{%- for item in in_scope %}
| {{ item.step }} | {{ item.description }} |
{%- endfor %}
{%- else %}
| Schritt | Beschreibung |
| --- | --- |
| [TBD] | |
{%- endif %}
