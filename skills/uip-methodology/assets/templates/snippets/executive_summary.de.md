{%- set s = executive_summary or {} %}
| {{ table_headings["executive_summary"][0] }} | {{ table_headings["executive_summary"][1] }} |
| --- | --- |
| Geschäftlicher Zweck | {{ s.purpose or "[TBD]" }} |
| Auslöser | {{ s.trigger or "[TBD]" }} |
| Bearbeitungsvolumen | {{ s.volume or "[TBD]" }} |
| Beteiligte Systeme | {{ s.systems | join(", ") if s.systems else "[TBD]" }} |
| Mögliche Ergebnisse | {% if s.results %}{% for r in s.results %}– {{ r }}{{ "<br>" if not loop.last else "" }}{% endfor %}{% else %}[TBD]{% endif %} |
