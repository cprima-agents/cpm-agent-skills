{%- if contacts_business %}
| Rolle | Name | E-Mail | Organisationseinheit | Hinweise |
| --- | --- | --- | --- | --- |
{%- for c in contacts_business %}
| {{ c.role }} | {{ c.name }} | {{ c.email or "" }} | {{ c.org_unit or "" }} | {{ c.notes or "" }} |
{%- endfor %}
{%- else %}
[TBD]
{%- endif %}
