{%- if system_prerequisites %}
| System | Voraussetzung | Einzelheiten | Verantwortlich | Status | Schranke |
| --- | --- | --- | --- | --- | --- |
{%- for p in system_prerequisites %}
| {{ p.system }} | {{ p.prerequisite }} | {{ p.detail or "" }} | {{ p.owner or "" }} | {{ p.status or "Offen" }} | {{ p.gate or "" }} |
{%- endfor %}
{%- else %}
[TBD]
{%- endif %}
