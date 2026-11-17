{%- if process_map and process_map.image %}
![{{ process_map.title }}]({{ process_map.image }})
{%- if process_map.source %}

Quelle (draw.io): [{{ process_map.name }}]({{ process_map.source }})
{%- endif %}
{%- elif process_map and process_map.mermaid %}
```mermaid
{{ process_map.mermaid }}
```
{%- else %}
[TBD — Übersichtsdiagramm beifügen]
{%- endif %}
