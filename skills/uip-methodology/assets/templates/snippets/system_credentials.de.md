{%- if system_credentials %}
| System | Umgebung | Authentifizierung | Zugangsdaten-Asset | Asset-Typ | Rotation | Status |
| --- | --- | --- | --- | --- | --- | --- |
{%- for c in system_credentials %}
| {{ c.system }} | {{ c.environment }} | {{ c.auth_method or "" }} | {{ c.credential_asset or "" }} | {{ c.asset_type or "" }} | {{ c.rotation or "" }} | {{ c.status or "Offen" }} |
{%- endfor %}
{%- else %}
[TBD]
{%- endif %}
