<!-- Nur ein Beispiel (ein erfundenes Projekt zur Rechnungsbuchung). Wird nie gerendert. So sieht ein gefüllter Bereich aus. -->

### 4.3 `InvoicePosting_Aggregator` *(rpa_aggregator)*

Erzeugt eine tägliche Buchungsübersicht, nachdem alle Transaktionen des Performers abgeschlossen sind. Wird durch einen zeitgesteuerten Job 30 Minuten nach dem Stoppsignal des Performers ausgelöst, damit die letzten Transaktionen Zeit zum Abschluss haben.

| Position | Entscheidung | Begründung |
| --- | --- | --- |
| Auslöser | Zeitgesteuert — 08:30 Uhr MEZ Mo–Fr | 30 Minuten nach dem Stoppsignal des Performers; lässt die letzten Transaktionen zur Ruhe kommen |
| Eingabe | Orchestrator-Warteschlange `InvoicePosting` — erfolgreiche und fehlgeschlagene Vorgänge des heutigen Laufs | |
| Ausgabe | XLSX-Bericht per E-Mail an den Verteiler des AP-Teams | Vom Fachbereich gewünschtes Format; es gibt noch kein Dashboard-Werkzeug |
| Art der Konfiguration | Orchestrator-Assets / TOML | |
