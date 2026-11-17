{%- set c = namespace(found=none) %}
{%- for item in (containers or []) %}
{%- if item.archetype == "rpa_performer" and c.found is none %}
{%- set c.found = item %}
{%- endif %}
{%- endfor %}
{%- set f = c.found or {} %}
Eine REFramework-Transaktion = ein [TBD — fachliches Objekt]. Das `Reference` des Vorgangs trägt [TBD — eindeutiges Feld] — es dient als Schlüssel zur Duplikaterkennung und als Korrelations-ID in allen Protokollmeldungen.

[TBD — ein Satz zur Idempotenz: angeben, ob das Schreiben in das Zielsystem idempotent ist und welche Regel für Wiederholungen daraus folgt.]

| Position | Entscheidung | Begründung |
| --- | --- | --- |
| Anzahl Wiederholungen (PROD) | [TBD — 0, wenn das Ziel nicht idempotent ist] | [TBD — angeben, warum eine Wiederholung für dieses Zielsystem sicher oder unsicher ist] |
| Anzahl Wiederholungen (DEV/TEST) | [TBD — meist 1] | Fängt vorübergehende Instabilität der Testumgebung auf |
| Max. aufeinanderfolgende SE | 3 | Drei Fehler in Folge deuten auf einen Infrastrukturausfall — abbrechen und den Betrieb alarmieren |
| ShouldMarkJobAsFaulted | true (PROD) | Stellt sicher, dass der Orchestrator den Betrieb alarmiert, wenn die Abbruchschwelle erreicht ist |
| Mehrere Auflösungen | [TBD — Ja / Nein] | [TBD — bei Nein die getestete Auflösung angeben] |
| Gelesene Warteschlange | `{{ f.queue_reads or "[TBD]" }}` | |
| Art der Konfiguration | Orchestrator-Assets / TOML | |

**Vertrag der Warteschlange (gelesen aus `{{ f.queue_reads or "[TBD]" }}`):**

| Feld | Typ | Pflicht | Hinweise |
| --- | --- | --- | --- |
| Reference | string | ja | [TBD — eindeutiger Schlüssel; darf nie leer sein] |
| [TBD Feld] | string | ja | |
