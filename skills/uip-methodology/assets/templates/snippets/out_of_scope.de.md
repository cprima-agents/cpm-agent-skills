{%- if out_of_scope %}
| Tätigkeit / Schritt | Grund | Auswirkung auf TO-BE | Weg zur künftigen Automatisierung |
| --- | --- | --- | --- |
{%- for item in out_of_scope %}
| {{ item.activity }} | {{ item.reason }} | {{ item.impact_on_to_be or "" }} | {{ item.future_automation_path or "" }} |
{%- endfor %}
{%- else %}
| Tätigkeit / Schritt | Grund | Auswirkung auf TO-BE | Weg zur künftigen Automatisierung |
| --- | --- | --- | --- |
| [TBD] | | | |
{%- endif %}
