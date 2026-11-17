{%- set c = namespace(found=none) %}
{%- for item in (containers or []) %}
{%- if item.archetype == "rpa_library" and c.found is none %}
{%- set c.found = item %}
{%- endif %}
{%- endfor %}
{%- set f = c.found or {} %}
[TBD — ein Absatz: welche wiederverwendbare Fähigkeit diese Bibliothek bereitstellt, welche Komponenten sie nutzen und warum sie als Bibliothek herausgelöst und nicht eingebettet wurde.]

| Position | Entscheidung | Begründung |
| --- | --- | --- |
| NuGet-Paket-ID | [TBD — z. B. `Org.RPA.Team.{{ f.name or "[Name]" }}`] | |
| Exportierte Workflows | [TBD — Name(Eingabeargument: Typ, …) → Ausgabeargument: Typ] | Öffentliche Schnittstelle der Bibliothek |
| Nutzer | [TBD — welche Komponenten aus Abschnitt 3.3 diese Bibliothek einbinden] | |
| Framework | {{ f.framework or "[TBD — XAML / Coded / Hybrid]" }} | |
| Übergabe der Konfiguration | Nur Argumente — keine Orchestrator-Assets | Die Bibliothek hat keinen Roboterkontext zur Laufzeit; die Aufrufer übergeben die gesamte Konfiguration |
| Versionierungsstrategie | SemVer — Änderungen an Argumenten, die Bestehendes brechen, erhöhen die Hauptversion | Verhindert stilles Brechen in den nutzenden Projekten |
