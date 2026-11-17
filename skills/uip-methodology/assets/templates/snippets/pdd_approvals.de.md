{%- if pdd_approvals %}
| Version | Rolle | Name | Abteilung | Datum |
| --- | --- | --- | --- | --- |
{%- for a in pdd_approvals %}
| {{ a.version or "" }} | {{ a.role or "" }} | {{ a.name or "" }} | {{ a.department or "" }} | {{ a.date or "" }} |
{%- endfor %}
{%- else %}
| Version | Rolle | Name | Abteilung | Datum |
| --- | --- | --- | --- | --- |
| 1.0 | Prozessverantwortlicher | [TBD] | [TBD] | |
| 1.0 | Solution Architect | [TBD] | [TBD] | |
| 1.0 | Betriebsrat — Mitbestimmung | [TBD] | [TBD] | |
| 1.0 | Datenschutzbeauftragter | [TBD] | [TBD] | |
{%- endif %}
