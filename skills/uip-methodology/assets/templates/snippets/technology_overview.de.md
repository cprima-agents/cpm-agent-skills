{%- if technology_overview %}
| Ebene | Komponente | Auswahl |
| --- | --- | --- |
{%- for item in technology_overview %}
| {{ item.layer }} | {{ item.component }} | {{ item.selection or item.used or "TBD" }} |
{%- endfor %}
{%- else %}
| Ebene | Komponente | Auswahl |
| --- | --- | --- |
| Discovery | Process Mining | TBD |
| Discovery | Task Mining | TBD |
| Discovery | Communications Mining (Discovery) | TBD |
| Automatisierung | RPA — Unbeaufsichtigt (BOR) | TBD |
| Automatisierung | RPA — Beaufsichtigt (FOR) | TBD |
| Automatisierung | Integration Service (API-Konnektoren) | TBD |
| Automatisierung | Maestro / Workflow-Orchestrierung | TBD |
| Automatisierung | Agents (agentisch / LLM-gesteuert) | TBD |
| Automatisierung | Testautomatisierung (Test Suite) | TBD |
| Kognitiv / KI | Document Understanding / IDP | TBD |
| Kognitiv / KI | AI Center (eigene Modelle) | TBD |
| Kognitiv / KI | Communications Mining (Laufzeit) | TBD |
| Mensch in der Schleife | Action Center | TBD |
| Mensch in der Schleife | Apps (eigene Oberfläche) | TBD |
| Daten & Berichte | Data Service | TBD |
| Daten & Berichte | Insights | TBD |
| Daten & Berichte | Process Mining (operativ) | TBD |
| Infrastruktur | Automation Cloud (SaaS) | TBD |
| Infrastruktur | Automation Suite (On-Premise / k8s) | TBD |
| Infrastruktur | Serverless-Roboter | TBD |
| Infrastruktur | VM-basierte Roboter | TBD |
{%- endif %}
