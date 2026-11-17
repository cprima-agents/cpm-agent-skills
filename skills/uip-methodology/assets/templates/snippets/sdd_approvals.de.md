{%- if sdd_approvals %}
| Version | Rolle | Name | Abteilung | Datum |
| --- | --- | --- | --- | --- |
{%- for a in sdd_approvals %}
| {{ a.version or "" }} | {{ a.role or "" }} | {{ a.name or "" }} | {{ a.department or "" }} | {{ a.date or "" }} |
{%- endfor %}
{%- else %}
| Version | Rolle | Name | Abteilung | Datum |
| --- | --- | --- | --- | --- |
| 1.0 | Solution Architect | [TBD] | [TBD] | |
| 1.0 | Entwicklungsleitung | [TBD] | [TBD] | |
| 1.0 | Prozessverantwortlicher | [TBD] | [TBD] | |
{%- endif %}
