{%- if components %}
| ID | Stufe | Archetyp | Modul | Aufgabe | Anwendung | Schnittstelle | Erhält | Erzeugt | Ausnahmeverweise |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
{%- for c in components %}
| {{ c.id }} | {{ c.stage }} | {{ c.archetype or "[TBD]" }} | {{ c.module or "[TBD]" }} | {{ c.responsibility or "[TBD]" }} | {{ c.application or "—" }} | {{ c.surface or "—" }} | {{ c.receives or "—" }} | {{ c.produces or "—" }} | {{ c.exception_refs or "—" }} |
{%- endfor %}

> ‡ Standard-REFramework-Modul — Aufwand aus dem Katalog, keine eigene Schätzung.
> † Prozessspezifisch — Aufwand abhängig von Archetyp, Anwendung und Anzahl der Ausnahmen.
> **Katalog der Archetypen:** `standard_ref_shell` · `email_ingest` · `ui_ingest` · `api_ingest` · `file_ingest` · `file_parse` · `api_enrich` · `ui_enrich` · `db_enrich` · `dto_mapping` · `rule_decide` · `sap_gui_execute` · `api_execute` · `ui_execute` · `queue_enqueue` · `api_complete` · `ui_complete`
> Anwendungen, die noch nicht automatisiert wurden, brauchen zusätzlichen Aufwand für robuste Selektoren — mit dem Kennzeichen `previously_automated` der Anwendungsliste abgleichen.
{%- else %}
| ID | Stufe | Archetyp | Modul | Aufgabe | Anwendung | Schnittstelle | Erhält | Erzeugt | Ausnahmeverweise |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cmp_shell_init | shell | standard_ref_shell | InitAllApplications ‡ | Vor der Transaktionsschleife alle Zielanwendungen öffnen und anmelden | [TBD] | ui | — | — | SE-01 |
| cmp_shell_close | shell | standard_ref_shell | CloseAllApplications ‡ | Alle geöffneten Anwendungen unabhängig vom Ausgang der Transaktion schließen | [TBD] | ui | — | — | — |
| cmp_init_validate | initialize | standard_ref_shell | Validate ‡ | Prüfen, dass die nötigen Felder des Vorgangs vorhanden sind; Transaktionsbereich initialisieren | — | — | TransactionItem | InitResult | BE-01 |
| [TBD] | ingest | [TBD] | Ingest[Source] † | Den vollständigen Quelldatensatz für diese Transaktion lesen | [TBD] | [TBD] | InitResult | RawData | SE-01 |
| [TBD] | enrich | [TBD] | Enrich[Reference] † | Um Referenzdaten oder Abfragen ergänzen, die nicht im Vorgang stehen | [TBD] | [TBD] | RawData | EnrichedItem | [TBD] |
| [TBD] | decide | rule_decide | Decide † | Geschäftsregeln anwenden; Verarbeitungspfad wählen; fachliche Ausnahmen erkennen | — | — | EnrichedItem | Decision | BE-01, BE-02 |
| [TBD] | execute | [TBD] | Execute[Target] † | Ergebnis in das Zielsystem schreiben — Hauptaktion der Automatisierung | [TBD] | [TBD] | Decision | ExecutionResult | SE-02 |
| [TBD] | complete | [TBD] | Complete[Source] † | Status im Quellsystem aktualisieren; Ausgabeeigenschaften des Orchestrators schreiben | [TBD] | [TBD] | ExecutionResult | CompletedItem | SE-01 |
| cmp_finalize | finalize | standard_ref_shell | Finalize ‡ | Ressourcen freigeben; strukturierten Prüfeintrag schreiben; Status an REFramework zurückgeben | — | — | CompletedItem | — | — |

> ‡ Standard-REFramework-Modul — Aufwand aus dem Katalog, keine eigene Schätzung.
> † Prozessspezifisch — Aufwand abhängig von Archetyp, Anwendung und Anzahl der Ausnahmen.
> **Katalog der Archetypen:** `standard_ref_shell` · `email_ingest` · `ui_ingest` · `api_ingest` · `file_ingest` · `file_parse` · `api_enrich` · `ui_enrich` · `db_enrich` · `dto_mapping` · `rule_decide` · `sap_gui_execute` · `api_execute` · `ui_execute` · `queue_enqueue` · `api_complete` · `ui_complete`
> Anwendungen, die noch nicht automatisiert wurden, brauchen zusätzlichen Aufwand für robuste Selektoren — mit dem Kennzeichen `previously_automated` der Anwendungsliste abgleichen.
{%- endif %}
