{%- if exception_handling %}
| Ausnahmeart | Auslöser | Aktion des Roboters | Max. Wiederholungen | Eskalation |
| --- | --- | --- | --- | --- |
{%- for e in exception_handling %}
| {{ e.exception_type }} | {{ e.trigger or "" }} | {{ e.robot_action or "" }} | {{ e.max_retries }} | {{ e.escalation or "" }} |
{%- endfor %}
{%- else %}
[TBD]
{%- endif %}
