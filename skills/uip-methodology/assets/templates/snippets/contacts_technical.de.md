{%- if contacts_technical %}
| Rolle | Name | System | E-Mail |
| --- | --- | --- | --- |
{%- for c in contacts_technical %}
| {{ c.role }} | {{ c.name }} | {{ c.system or "" }} | {{ c.email or "" }} |
{%- endfor %}
{%- else %}
[TBD]
{%- endif %}
