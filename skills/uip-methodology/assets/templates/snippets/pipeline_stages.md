{#- The pipeline stages of the robot run and what happens in each, generated from process.yaml (the to-be steps). -#}
{%- if pipeline %}
The robot works through these stages, in this order:

{% for stage in pipeline -%}
- **{{ (stage.number ~ " ") if stage.number else "" }}{{ stage.name }}:** {{ stage.purpose }}
  - Steps: {% for s in stage.steps %}{{ (s.number ~ " ") if s.number else "" }}{{ s.label }}{{ "; " if not loop.last else "" }}{% else %}none yet{% endfor %}
  - Systems: {{ stage.systems | join(", ") if stage.systems else "—" }}
  - Data: {{ stage.data | join("; ") if stage.data else "—" }}
{% endfor -%}
{%- else %}
[TBD — attach TO-BE map with automated steps highlighted]
{%- endif %}
