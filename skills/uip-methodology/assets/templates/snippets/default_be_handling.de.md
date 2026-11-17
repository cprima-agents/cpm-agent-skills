{%- if default_be_handling %}
{%- for item in default_be_handling %}
- {{ item }}
{%- endfor %}
{%- else %}
[TBD]
{%- endif %}
