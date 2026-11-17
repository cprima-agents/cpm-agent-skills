{#- The decisions chapter: one numbered section per decision of decisions.yaml. A decision is a thing of its own; a step
    only points at it (see process_steps.md). `chapter` is the number of the chapter in the PDD template. -#}
{%- set chapter = 4 %}
{%- if decisions %}
{%- for d in decisions %}
### {{ chapter }}.{{ loop.index }} {{ d.question }}

{% if d.made_in %}- **Made in step:** {{ d.made_in | join("; ") }}
{% endif %}
{%- if d.used_at %}- **The flow branches on it at:** {{ d.used_at | unique | join("; ") }}
{% endif %}
{%- if d.reads %}- **Reads:** {% for r in d.reads %}{{ r.name }}{{ (" (" ~ r.container ~ ")") if r.container else "" }}{{ "; " if not loop.last else "" }}{% endfor %}
{% endif %}
{%- if d.match %}- **How the rules apply:** {{ d.match }}
{% endif %}
{%- if d.no_match %}- **When no rule applies:** {{ d.no_match }}
{% endif %}
{%- for n in d.notes %}- {{ n }}
{% endfor %}
| Rule | When | Then | Status |
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
