{#- Das Kapitel Entscheidungen: ein nummerierter Abschnitt je Entscheidung aus decisions.yaml. Eine Entscheidung ist ein
    eigenes Ding; ein Schritt verweist nur auf sie (siehe process_steps.de.md). `chapter` ist die Kapitelnummer im PDD. -#}
{%- set chapter = 4 %}
{%- if decisions %}
{%- for d in decisions %}
### {{ chapter }}.{{ loop.index }} {{ d.question }}

{% if d.made_in %}- **Getroffen im Schritt:** {{ d.made_in | join("; ") }}
{% endif %}
{%- if d.used_at %}- **Der Ablauf verzweigt danach bei:** {{ d.used_at | unique | join("; ") }}
{% endif %}
{%- if d.reads %}- **Liest:** {% for r in d.reads %}{{ r.name }}{{ (" (" ~ r.container ~ ")") if r.container else "" }}{{ "; " if not loop.last else "" }}{% endfor %}
{% endif %}
{%- if d.match %}- **So gelten die Regeln:** {{ d.match }}
{% endif %}
{%- if d.no_match %}- **Wenn keine Regel gilt:** {{ d.no_match }}
{% endif %}
{%- for n in d.notes %}- {{ n }}
{% endfor %}
| Regel | Wenn | Dann | Status |
| --- | --- | --- | --- |
{%- for r in d.rules %}
| {{ r.id }} | {{ r.when }} | {{ r.then }} | {{ r.status }} |
{%- endfor %}
{% if not loop.last %}
{% endif %}
{%- endfor %}
{%- else %}
[TBD]
{%- endif %}
