{%- if branches %}
| Branch | Muster | Umgebung | Deploy-Auslöser | Geschützt | Zweck |
| --- | --- | --- | --- | --- | --- |
{%- for b in branches %}
| `{{ b.name }}` | {{ b.pattern or 'exakt' }} | {{ b.environment or '[TBD]' }} | {{ b.deploy_trigger or '[TBD]' }} | {{ 'ja' if b.protected else 'nein' }} | {{ b.purpose or '' }} |
{%- endfor %}
{%- else %}
| Branch | Muster | Umgebung | Deploy-Auslöser | Geschützt | Zweck |
| --- | --- | --- | --- | --- | --- |
| `main` | exakt | Produktion | Merge des Pull Requests | ja | Stabiles Release |
| `uat` | exakt | UAT | Merge des Pull Requests | ja | Validierung vor dem Release |
| `development` | `development*` | Entwicklung | Push | nein | Aktive Entwicklung |
{%- endif %}
