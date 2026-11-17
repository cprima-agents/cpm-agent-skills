{%- set s = executive_summary or {} %}
| {{ table_headings["executive_summary"][0] }} | {{ table_headings["executive_summary"][1] }} |
| --- | --- |
| Business purpose | {{ s.purpose or "[TBD]" }} |
| Trigger | {{ s.trigger or "[TBD]" }} |
| Processing volume | {{ s.volume or "[TBD]" }} |
| Systems involved | {{ s.systems | join(", ") if s.systems else "[TBD]" }} |
| Possible results | {% if s.results %}{% for r in s.results %}– {{ r }}{{ "<br>" if not loop.last else "" }}{% endfor %}{% else %}[TBD]{% endif %} |
