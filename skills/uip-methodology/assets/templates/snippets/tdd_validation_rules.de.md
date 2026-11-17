{%- if entities %}
{%- for entity in entities %}
#### {{ entity.name }}

| Feld | Regel | Bei Fehler |
| --- | --- | --- |
{%- for f in entity.fields %}
{%- if f.enum %}
| {{ f.name }} | muss einer von diesen Werten sein: {{ f.enum | join(', ') }} | BusinessRuleException |
{%- endif %}
{%- endfor %}
{%- for v in entity.validations | default([]) %}
| {{ v.field }} | {{ v.rule }} | {{ v.on_failure }} |
{%- endfor %}
{%- if not loop.last %}

{% endif %}
{%- endfor %}
{%- else %}
#### [TBD]

| Feld | Regel | Bei Fehler |
| --- | --- | --- |
| [TBD] | | |
{%- endif %}
