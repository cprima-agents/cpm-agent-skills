{%- if project and project.dependencies %}
{%- set prefix = company_package_prefix or '' %}
{%- set libs = [] %}
{%- for name, version in project.dependencies.items() %}
{%- if not name.startswith('UiPath.') and (not prefix or name.startswith(prefix)) %}
{%- set _ = libs.append({'name': name, 'version': version}) %}
{%- endif %}
{%- endfor %}
{%- if libs %}
| Komponente | Version | Quelle | Zweck |
| --- | --- | --- | --- |
{%- for lib in libs %}
| `{{ lib.name }}` | {{ lib.version }} | Interne Bibliothek | |
{%- endfor %}
{%- else %}
entfällt — keine internen Bibliotheksabhängigkeiten.
{%- endif %}
{%- else %}
entfällt — keine internen Bibliotheksabhängigkeiten.
{%- endif %}
