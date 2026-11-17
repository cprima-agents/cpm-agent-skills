{%- if application_errors %}
| Name | Schritt | Auslöser | Aktion des Roboters |
| --- | --- | --- | --- |
{%- for e in application_errors %}
| {{ e.name }} | {{ e.step or "" }} | {{ e.trigger or "" }} | {{ e.robot_action or "" }} |
{%- endfor %}
{%- else %}
[TBD]
{%- endif %}
