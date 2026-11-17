{%- if tdd_history %}
| Version | Datum | Autor | Rolle | Änderungen |
| --- | --- | --- | --- | --- |
{%- for h in tdd_history %}
| {{ h.version or "" }} | {{ h.date or "" }} | {{ h.author or "" }} | {{ h.role or "" }} | {{ h.changes or "" }} |
{%- endfor %}
{%- else %}
| Version | Datum | Autor | Rolle | Änderungen |
| --- | --- | --- | --- | --- |
| 1.0 | [JJJJ-MM-TT] | [TBD] | RPA-Entwickler | Erster Entwurf |
{%- endif %}
