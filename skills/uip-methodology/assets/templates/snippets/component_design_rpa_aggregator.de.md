{%- set c = namespace(found=none) %}
{%- for item in (containers or []) %}
{%- if item.archetype == "rpa_aggregator" and c.found is none %}
{%- set c.found = item %}
{%- endif %}
{%- endfor %}
{%- set f = c.found or {} %}
[TBD — ein Absatz: was dieser Aggregator sammelt, wann er im Verhältnis zum Performer läuft und was er erzeugt.]

| Position | Entscheidung | Begründung |
| --- | --- | --- |
| Auslöser | {{ f.trigger or "[TBD — zeitgesteuert nach dem Performer / Signal der Tiefe der Warteschlange]" }} | |
| Eingabe | [TBD — Ergebnisse der Orchestrator-Warteschlange / Ausgabedatei / API] | |
| Ausgabe | [TBD — Berichtsdatei / E-Mail / Aufruf einer nachgelagerten API] | |
| Art der Konfiguration | Orchestrator-Assets / TOML | |
