{%- if parallel_initiatives %}
| Initiative | Betroffene Schritte | Auswirkung auf die Automatisierung | Voraussichtliche Fertigstellung | Kontakt |
| --- | --- | --- | --- | --- |
{%- for item in parallel_initiatives %}
| {{ item.initiative }} | {{ item.affected_steps }} | {{ item.impact_on_automation }} | {{ item.expected_completion }} | {{ item.contact }} |
{%- endfor %}
{%- else %}
| Initiative | Betroffene Schritte | Auswirkung auf die Automatisierung | Voraussichtliche Fertigstellung | Kontakt |
| --- | --- | --- | --- | --- |
| entfällt | | | | |
{%- endif %}
