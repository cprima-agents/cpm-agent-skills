{#- Two columns. The data says what a step is; this snippet decides where it appears: the cell holds the description, the
    system, the screenshots, then a divider and the next steps, rules and exceptions. Each part is a
    <span custom-style="…">, which a converter (pandoc) turns into a named Word style; the parts are separated by <br>,
    which the filter assets/pandoc/cell-breaks.lua turns into a Word line break. No <hr>: it breaks the conversion. -#}
{%- macro part(style, text) %}<span custom-style="{{ style }}">{{ text }}</span>{% endmacro %}
{%- set divider = "<br>" ~ part("StepDivider", "―――") ~ "<br>" %}
{%- if process_steps %}
| Step | What happens |
| --- | --- |
{%- for s in process_steps %}
{%- set c = namespace(top=part("StepDescription", "**" ~ s.description ~ "**"), lines=[]) %}
{%- if s.where %}{% set c.top = c.top ~ "<br>" ~ part("StepSystem", "*" ~ s.where ~ "*") %}{% endif %}
{%- for shot in s.screenshots %}{% set c.top = c.top ~ "<br>![" ~ shot.caption ~ "](" ~ shot.file ~ ")" %}{% endfor %}
{%- for n in s.next %}{% set _ = c.lines.append(part("StepNext", "→ " ~ ((n.condition ~ ": ") if n.condition else "") ~ n.target)) %}{% endfor %}
{%- if s.ruleset %}{% set _ = c.lines.append(part("StepRule", "Rules: see 4." ~ s.ruleset.index ~ " " ~ s.ruleset.question)) %}{% endif %}
{%- for r in s.rules %}{% set _ = c.lines.append(part("StepRule", "Rule: " ~ r)) %}{% endfor %}
{%- for x in s.exceptions %}{% set _ = c.lines.append(part("StepException", "⚠ Exception: " ~ x)) %}{% endfor %}
| {{ s.number }} | {{ c.top }}{{ (divider ~ (c.lines | join("<br>"))) if c.lines else "" }} |
{%- endfor %}
{%- else %}
[TBD]
{%- endif %}
