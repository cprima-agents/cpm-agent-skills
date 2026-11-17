{%- if business_exceptions %}
| Name | Schritt | Auslöser | Aktion des Roboters |
| --- | --- | --- | --- |
{%- for e in business_exceptions %}
| {{ e.name }} | {{ e.step or "" }} | {{ e.trigger or "" }} | {{ e.robot_action or "" }} |
{%- endfor %}
{%- else %}
[TBD]
{%- endif %}
