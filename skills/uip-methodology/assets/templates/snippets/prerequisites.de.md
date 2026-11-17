| Kriterium | Status |
| --- | --- |
{%- if prerequisites %}
{%- for p in prerequisites %}
| {{ p.criterion }} | {{ {'open': 'Offen', 'done': 'Erledigt', 'blocked': 'Blockiert'}.get(p.status | lower, p.status | capitalize) }} |
{%- endfor %}
{%- else %}
| Vollständiges und freigegebenes PDD | Offen |
| Zustimmung des Betriebsrats (Mitbestimmung) liegt vor | Offen |
| Zustimmung des Datenschutzbeauftragten liegt vor — Datenschutz-Folgenabschätzung durchgeführt, wenn personenbezogene Daten verarbeitet werden | Offen |
| Testdatensatz, der alle Ausnahmeszenarien abdeckt | Offen |
| Zugangsdaten liegen in Orchestrator-Assets (nichts fest im Code) | Offen |
| Abhängigkeiten zu anderen Projekten sind dokumentiert | Offen |
{%- for app in (applications or []) if app.in_scope and app.category == 'application' %}
| Roboter-Benutzerkonto hat Entwicklungs- und Testzugriff auf {{ app.name }} | {{ "Erledigt" if app.dev_test_access else "Offen" }} |
{%- endfor %}
{%- endif %}
