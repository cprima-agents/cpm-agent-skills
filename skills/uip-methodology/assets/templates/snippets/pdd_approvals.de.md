{%- if pdd_approvals %}
| Version | Rolle | Name | Abteilung | Datum |
| --- | --- | --- | --- | --- |
{%- for a in pdd_approvals %}
| {{ a.version or "" }} | {{ a.role or "" }} | {{ a.name or "" }} | {{ a.department or "" }} | {{ a.date or "" }} |
{%- endfor %}
{%- else %}
[TBD]
{%- endif %}
