{%- if reporting_requirements %}
| # | Report Type | Frequency | Details | Tool |
| --- | --- | --- | --- | --- |
{%- for r in reporting_requirements %}
| {{ r.no }} | {{ r.report_type }} | {{ r.frequency or "" }} | {{ r.details or "" }} | {{ r.tool or "" }} |
{%- endfor %}
{%- else %}
[TBD]
{%- endif %}
