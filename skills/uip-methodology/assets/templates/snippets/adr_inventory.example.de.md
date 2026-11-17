<!-- Nur ein Beispiel (zwei erfundene Entscheidungen). Wird nie gerendert. So sieht ein gefüllter Bereich aus. -->

| ID | Titel | Status | Betrifft |
| --- | --- | --- | --- |
| ADR-0001 | REFramework für Performer-Projekte mit Warteschlange verwenden | Angenommen | sdd, tdd |
| ADR-0002 | Coded Config (TOML) für Laufzeiteinstellungen | Angenommen | tdd |

#### ADR-0001 — REFramework für Performer-Projekte mit Warteschlange verwenden

**Status:** Angenommen
**Betrifft:** sdd, tdd

**Kontext:** Das Performer-Projekt bearbeitet Transaktionen der Orchestrator-Warteschlange nacheinander. Eine eigene Schleife für Wiederholungen und Zustandsverwaltung würde Verhalten nachbauen, das das Standard-REFramework von UiPath bereits bietet.

**Entscheidung:** REFramework wird als Shell des Performers übernommen. Die Geschäftslogik liegt ausschließlich in Workflows unter Process/, die aus Process Transaction aufgerufen werden. Die Zustände Init, GetTransactionData und SetTransactionStatus bleiben unverändert; am Ablauf des REFramework wird nichts geändert.

**Folgen:** Entwickler müssen die Zustandssemantik des REFramework verstehen. Eigene Wiederholungslogik ist im Zustand Process Transaction nicht erlaubt. Bei Framework-Aktualisierungen muss die Shell neu aus der aktuellen UiPath-Vorlage aufgebaut werden.

#### ADR-0002 — Coded Config (TOML) für Laufzeiteinstellungen

**Status:** Angenommen
**Betrifft:** tdd

**Kontext:** Config.xlsx ist unter Versionskontrolle fragil: binäre Unterschiede sind unlesbar, Merge-Konflikte lassen sich nicht auflösen, und umgebungsspezifische Werte erfordern beim Deployment das manuelle Überschreiben einer Datei.

**Entscheidung:** Config.xlsx wird durch TOML-Dateien je Umgebung ersetzt (Config_Dev.toml, Config_Test.toml, Config_Prod.toml), die eine CodedConfig-Aktivität lädt. TOML ist Klartext, eignet sich für Vergleiche und unterstützt typisierte Werte ohne zusätzliche Auswertung.

**Folgen:** Die Roboter brauchen .NET 8 und das NuGet-Paket CodedConfig. Alle Verweise auf Assets wandern in TOML-Schlüssel. Die alte Config.xlsx und ihr Ladeworkflow werden aus dem Projekt entfernt.
