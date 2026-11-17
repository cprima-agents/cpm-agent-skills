{%- if process_map and process_map.image %}
![{{ process_map.title }}]({{ process_map.image }})
{%- if process_map.name %}

Source: diagram {{ process_map.name }}
{%- endif %}
{%- elif process_map and process_map.mermaid %}
```mermaid
{{ process_map.mermaid }}
```
{%- else %}
[TBD — attach high-level map]
{%- endif %}
