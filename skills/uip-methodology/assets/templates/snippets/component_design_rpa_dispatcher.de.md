{%- set c = namespace(found=none) %}
{%- for item in (containers or []) %}
{%- if item.archetype == "rpa_dispatcher" and c.found is none %}
{%- set c.found = item %}
{%- endif %}
{%- endfor %}
{%- set f = c.found or {} %}
[TBD — ein Absatz: was dieser Dispatcher abfragt, wann er läuft und die wichtige Entscheidung zur Duplikaterkennung.]

| Position | Entscheidung | Begründung |
| --- | --- | --- |
| Quelle | [TBD — System / Postfach / API / Datenbank] | |
| Duplikaterkennung | Referenz = [TBD]; überspringen, wenn der Vorgang schon in der Warteschlange ist | Verhindert doppelte Vorgänge, wenn der Dispatcher erneut läuft, bevor der Performer die Warteschlange abgearbeitet hat |
| Bei leerer Quelle | [TBD — still beenden / warnen / alarmieren] | |
| Zeitplan | {{ f.trigger or "[TBD]" }} | |
| Beschriebene Warteschlange | `{{ f.queue_writes or "[TBD]" }}` | |
| Art der Konfiguration | Orchestrator-Assets / TOML | |
