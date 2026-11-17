{%- if reporting_requirements %}
| Nr. | Berichtsart | Häufigkeit | Einzelheiten | Werkzeug |
| --- | --- | --- | --- | --- |
{%- for r in reporting_requirements %}
| {{ r.no }} | {{ r.report_type }} | {{ r.frequency or "" }} | {{ r.details or "" }} | {{ r.tool or "" }} |
{%- endfor %}
{%- else %}
[TBD]
{%- endif %}
