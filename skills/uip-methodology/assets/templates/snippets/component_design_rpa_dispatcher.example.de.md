<!-- Nur ein Beispiel (ein erfundenes Projekt zur Rechnungsbuchung). Wird nie gerendert. So sieht ein gefüllter Bereich aus. -->

### 4.1 `InvoicePosting_Dispatcher` *(rpa_dispatcher)*

Liest das AP-Postfach, entnimmt aus jedem Paar von E-Mail und PDF die Rechnungsdaten und stellt je Rechnung einen Vorgang in die Warteschlange. Läuft um 05:45 Uhr MEZ, damit die Warteschlange vor dem Auslöser des Performers um 06:00 Uhr MEZ gefüllt ist. Die Duplikaterkennung geschieht hier — der Performer prüft nie auf Duplikate.

| Position | Entscheidung | Begründung |
| --- | --- | --- |
| Quelle | AP-Postfach — IMAP, Ordner Posteingang, Betrefffilter „Invoice“ | Der Fachbereich hat bestätigt, dass alle Rechnungen über diesen einen Kanal eingehen |
| Duplikaterkennung | Referenz = invoice_number; überspringen, wenn der Vorgang schon in der Warteschlange ist | Verhindert doppeltes Buchen, wenn der Dispatcher erneut läuft, bevor der Performer die Warteschlange abgearbeitet hat |
| Bei leerem Postfach | Still beenden | Keine Rechnungen sind an Feiertagen normal — ein Alarm würde nur stören |
| Zeitplan | 05:45 Uhr MEZ Mo–Fr | 15 Minuten Vorlauf stellen sicher, dass die Warteschlange vor dem Auslöser des Performers gefüllt ist |
| Beschriebene Warteschlange | `InvoicePosting` | |
| Art der Konfiguration | Orchestrator-Assets / TOML | |
