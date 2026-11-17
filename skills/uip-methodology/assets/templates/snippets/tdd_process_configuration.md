{%- if config_sections %}
{%- for section in config_sections %}
#### {{ section.name }}

| Property | Type |{% for env in config_envs %} {{ env | upper }} |{% endfor %}
| --- | --- |{% for env in config_envs %} --- |{% endfor %}
{%- for prop in section.properties %}
| `{{ prop.name }}` | `{{ prop.type }}` |{% for env in config_envs %} {{ prop.get(env, '—') }} |{% endfor %}
{%- endfor %}

{%- endfor %}
{%- else %}
#### Settings

| Property | Type | DEV | TEST | PROD |
| --- | --- | --- | --- | --- |
| [TBD] | | | | |

#### Constants

| Property | Type | DEV | TEST | PROD |
| --- | --- | --- | --- | --- |
| [TBD] | | | | |

#### Assets

| Property | Type | DEV | TEST | PROD |
| --- | --- | --- | --- | --- |
| [TBD] | | | | |
{%- endif %}
