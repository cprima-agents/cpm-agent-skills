{%- if entities %}
{%- for entity in entities %}
#### {{ entity.name }}

| Field | Rule | On failure |
| --- | --- | --- |
{%- for f in entity.fields %}
{%- if f.enum %}
| {{ f.name }} | must be one of: {{ f.enum | join(', ') }} | BusinessRuleException |
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

| Field | Rule | On failure |
| --- | --- | --- |
| [TBD] | | |
{%- endif %}
