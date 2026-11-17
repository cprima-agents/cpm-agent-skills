{%- if sdd_approvals %}
| Version | Rolle | Name | Abteilung | Datum |
| --- | --- | --- | --- | --- |
{%- for a in sdd_approvals %}
| {{ a.version or "" }} | {{ a.role or "" }} | {{ a.name or "" }} | {{ a.department or "" }} | {{ a.date or "" }} |
{%- endfor %}
{%- else %}
[TBD]
{%- endif %}
