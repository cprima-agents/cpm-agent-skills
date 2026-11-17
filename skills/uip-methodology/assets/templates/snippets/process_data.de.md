| Eingabe | Schritte | Quellsystem | Eingabeformat | Ablageort | Strukturiert |
| --- | --- | --- | --- | --- | --- |
{%- if entities %}
{%- for e in entities %}
| {{ e.name }} | {{ e.steps | join(', ') if e.steps else '—' }} | {{ e.source.application or '—' }} | {{ e.source.input_type or '—' }} | {{ e.source.location or '—' }} | {{ '—' if e.structured is not defined else ('Ja' if e.structured else 'Nein') }} |
{%- endfor %}
{%- else %}
| [TBD] | | | | | |
{%- endif %}
