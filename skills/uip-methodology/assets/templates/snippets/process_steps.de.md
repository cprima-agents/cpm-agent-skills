{#- Zwei Spalten. Die Daten sagen, was ein Schritt ist; dieses Snippet entscheidet, wo es erscheint: die Zelle enthält die
    Beschreibung, das System, die Screenshots, dann einen Trenner und darunter die nächsten Schritte, Regeln und Ausnahmen.
    Jeder Teil ist ein <span custom-style="…">, das ein Konverter (pandoc) in eine benannte Word-Formatvorlage umsetzt; die
    Teile sind durch <br> getrennt, das der Filter assets/pandoc/cell-breaks.lua in einen Word-Zeilenumbruch umsetzt.
    Kein <hr>: es zerstört die Umwandlung. Die Namen der Formatvorlagen sind in beiden Sprachen gleich. -#}
{%- macro part(style, text) %}<span custom-style="{{ style }}">{{ text }}</span>{% endmacro %}
{%- set divider = "<br>" ~ part("StepDivider", "―――") ~ "<br>" %}
{%- if process_steps %}
| Schritt | Was geschieht |
| --- | --- |
{%- for s in process_steps %}
{%- set c = namespace(top=part("StepDescription", "**" ~ s.description ~ "**"), lines=[]) %}
{%- if s.where %}{% set c.top = c.top ~ "<br>" ~ part("StepSystem", "*" ~ s.where ~ "*") %}{% endif %}
{%- for shot in s.screenshots %}{% set c.top = c.top ~ "<br>![" ~ shot.caption ~ "](" ~ shot.file ~ ")" %}{% endfor %}
{%- for n in s.next %}{% set _ = c.lines.append(part("StepNext", "→ " ~ ((n.condition ~ ": ") if n.condition else "") ~ n.target)) %}{% endfor %}
{%- if s.ruleset %}{% set _ = c.lines.append(part("StepRule", "Regeln: siehe 4." ~ s.ruleset.index ~ " " ~ s.ruleset.question)) %}{% endif %}
{%- for r in s.rules %}{% set _ = c.lines.append(part("StepRule", "Regel: " ~ r)) %}{% endfor %}
{%- for x in s.exceptions %}{% set _ = c.lines.append(part("StepException", "⚠ Ausnahme: " ~ x)) %}{% endfor %}
| {{ s.number }} | {{ c.top }}{{ (divider ~ (c.lines | join("<br>"))) if c.lines else "" }} |
{%- endfor %}
{%- else %}
[TBD]
{%- endif %}
