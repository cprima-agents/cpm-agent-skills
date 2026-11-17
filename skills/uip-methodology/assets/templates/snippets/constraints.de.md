{%- if constraints %}
| # | Art | Aussage |
| --- | --- | --- |
{%- for c in constraints %}
| {{ loop.index }} | {{ c.type }} | {{ c.statement }} |
{%- endfor %}
{%- else %}
| # | Art | Aussage |
| --- | --- | --- |
| 1 | Randbedingung | [TBD] |
| 2 | Annahme | [TBD] |
{%- endif %}
