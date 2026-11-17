{%- if access_control %}
| Position | Wert |
| --- | --- |
{%- for row in access_control %}
| {{ row.item_label }} | {{ row.value or "[TBD]" }} |
{%- endfor %}
{%- else %}
{%- set infra = namespace(robot_type="[TBD]", unattended=false, attended=false) %}
{%- if technology_overview %}
{%- for item in technology_overview %}
{%- if item.used == "✓" %}
{%- if item.component == "RPA — Unattended (BOR)" %}{%- set infra.unattended = true %}{% endif %}
{%- if item.component == "RPA — Attended (FOR)" %}{%- set infra.attended = true %}{% endif %}
{%- endif %}
{%- endfor %}
{%- set infra.robot_type = "Unbeaufsichtigt (BOR)" if infra.unattended else ("Beaufsichtigt (FOR)" if infra.attended else "[TBD]") %}
{%- endif %}
{%- set robot_prereqs = namespace(rows=[]) %}
{%- if system_prerequisites %}
{%- for p in system_prerequisites %}
{%- if p.system and "robot" in p.system | lower %}
{%- set robot_prereqs.rows = robot_prereqs.rows + [p] %}
{%- endif %}
{%- endfor %}
{%- endif %}
| Position | Wert |
| --- | --- |
| Robotertyp | {{ infra.robot_type }} |
{%- if robot_prereqs.rows %}
{%- for p in robot_prereqs.rows %}
| {{ p.prerequisite }} | {{ p.detail or "[TBD]" }} |
{%- endfor %}
{%- else %}
| Roboterkonto | [TBD — eigenes Entra-ID-Automatisierungskonto; kein persönliches Entwicklerkonto] |
| Berechtigungsstufe | [TBD — lokaler Administrator / Standardbenutzer] |
| MFA / Sitzungsrichtlinie | [TBD] |
{%- endif %}
{%- endif %}
