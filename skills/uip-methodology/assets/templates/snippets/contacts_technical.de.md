{%- if contacts_technical %}
| Rolle | Name | System | E-Mail | Hinweise |
| --- | --- | --- | --- | --- |
{%- for c in contacts_technical %}
| {{ c.role }} | {{ c.name }} | {{ c.system or "" }} | {{ c.email or "" }} | {{ c.notes or "" }} |
{%- endfor %}
{%- else %}
[TBD]
{%- endif %}
