{#- Die Pipeline-Stufen des Roboterlaufs und was in jeder geschieht, aus process.yaml erzeugt (die TO-BE-Schritte). -#}
{%- if pipeline %}
Der Roboter durchläuft diese Stufen in dieser Reihenfolge:

{% for stage in pipeline -%}
- **{{ stage.name }}:** {{ stage.purpose }}
  - Schritte: {% for s in stage.steps %}{{ s.label }}{{ "; " if not loop.last else "" }}{% else %}noch keiner{% endfor %}
  - Systeme: {{ stage.systems | join(", ") if stage.systems else "—" }}
  - Daten: {{ stage.data | join("; ") if stage.data else "—" }}
{% endfor -%}
{%- else %}
[TBD — TO-BE-Diagramm mit hervorgehobenen automatisierten Schritten beifügen]
{%- endif %}
