{%- if system_context %}
| Name | Rolle | Richtung | Im Umfang | Hinweise |
| --- | --- | --- | --- | --- |
{%- for s in system_context %}
| {{ s.name }} | {{ s.role or "" }} | {{ s.direction or "" }} | {{ "Ja" if s.in_scope else "Nein" }} | {{ s.notes or "" }} |
{%- endfor %}
{%- else %}
[TBD]
{%- endif %}
