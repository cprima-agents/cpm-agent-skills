{%- if integrations %}
| # | System | Integrationsart | Richtung | Authentifizierung |
| --- | --- | --- | --- | --- |
{%- for item in integrations %}
| {{ loop.index }} | {{ item.system }} | {{ item.integration_method or "[TBD]" }} | {{ item.direction or "[TBD]" }} | {{ item.auth_method or "[TBD]" }} |
{%- endfor %}
{%- elif applications %}
| # | System | Integrationsart | Richtung | Authentifizierung |
| --- | --- | --- | --- | --- |
{%- set row = namespace(n=1) %}
{%- for app in applications %}
{%- if app.in_scope %}
{%- set creds = system_credentials if system_credentials else [] %}
{%- set auth = "" %}
{%- for c in creds %}{% if c.system == app.name and not auth %}{%- set auth = c.auth_method or "" %}{% endif %}{%- endfor %}
{%- set comps = components if components else [] %}
{%- set dir = namespace(read=false, write=false) %}
{%- for c in comps %}
{%- if c.application == app.name %}
{%- if c.stage in ["ingest", "enrich"] %}{%- set dir.read = true %}{% endif %}
{%- if c.stage in ["execute", "complete"] %}{%- set dir.write = true %}{% endif %}
{%- endif %}
{%- endfor %}
{%- set direction = "Beides" if (dir.read and dir.write) else ("Schreiben" if dir.write else ("Lesen" if dir.read else "[TBD]")) %}
| {{ row.n }} | {{ app.name }} | {{ app.automation_surface or "[TBD]" }} | {{ direction }} | {{ auth or "[TBD]" }} |
{%- set row.n = row.n + 1 %}
{%- endif %}
{%- endfor %}
{%- else %}
| # | System | Integrationsart | Richtung | Authentifizierung |
| --- | --- | --- | --- | --- |
| 1 | [TBD] | REST-API / DB / UI / Datei | Lesen / Schreiben / Beides | OAuth / Basic / Windows |
{%- endif %}
