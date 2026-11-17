| Nr. | Berichtsart | Häufigkeit | Einzelheiten | Werkzeug |
| --- | --- | --- | --- | --- |
{%- if reporting_requirements %}
{%- for r in reporting_requirements %}
| {{ r.no }} | {{ r.report_type }} | {{ r.frequency }} | {{ r.details }} | {{ r.tool }} |
{%- endfor %}
{%- else %}
| 1 | Prozessprotokolle | Täglich | Anzahl der Läufe, durchschnittliche Dauer | Orchestrator / Kibana |
| 2 | Transaktionsprotokolle | Täglich | Anzahl der Transaktionen, Verhältnis Erfolg/Fehler | Orchestrator |
| 3 | Fehlerprotokolle | Täglich | Anzahl der Fehler je Art | Orchestrator / Kibana |
{%- endif %}
