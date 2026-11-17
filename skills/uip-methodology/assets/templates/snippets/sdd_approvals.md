{%- if sdd_approvals %}
| Version | Role | Name | Department | Date |
| --- | --- | --- | --- | --- |
{%- for a in sdd_approvals %}
| {{ a.version or "" }} | {{ a.role or "" }} | {{ a.name or "" }} | {{ a.department or "" }} | {{ a.date or "" }} |
{%- endfor %}
{%- else %}
[TBD]
{%- endif %}
