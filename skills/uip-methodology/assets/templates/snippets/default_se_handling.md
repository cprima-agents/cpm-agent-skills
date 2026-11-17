{%- if default_se_handling %}
{%- for item in default_se_handling %}
- {{ item }}
{%- endfor %}
{%- else %}
[TBD]
{%- endif %}
