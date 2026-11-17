<!-- Nur ein Beispiel (ein erfundenes Projekt zur Rechnungsbuchung). Wird nie gerendert. So sieht ein gefüllter Bereich aus. -->

### 4.4 `SAPPosting.Library` *(rpa_library)*

Stellt wiederverwendbare Workflows zur Automatisierung von SAP GUI für die Lösung Rechnungsbuchung bereit — genutzt von `InvoicePosting_Performer`. Als NuGet-Bibliothek verpackt, damit die Buchungslogik unabhängig von der REFramework-Shell des Performers getestet und versioniert werden kann.

| Position | Entscheidung | Begründung |
| --- | --- | --- |
| NuGet-Paket-ID | `DHL.RPA.AP.SAPPosting` | Folgt der Namenskonvention des DHL-Teams |
| Exportierte Workflows | `PostInvoice(vendor_id: string, amount: decimal, gl_account: string) → posted: boolean, doc_number: string` | Ein einziger Einstiegspunkt; die gesamte SAP-Navigation ist darin gekapselt |
| Nutzer | `InvoicePosting_Performer` | Der Dispatcher hat keine SAP-Interaktion; die Bibliothek wird nur vom Performer genutzt |
| Framework | XAML (UI-Automation-Aktivitäten) | SAP GUI braucht XAML für die Navigation über Selektoren |
| Übergabe der Konfiguration | Nur Argumente — keine Orchestrator-Assets | Der Performer holt die Konfiguration aus Assets/TOML und übergibt sie als Argumente |
| Versionierungsstrategie | SemVer — Änderungen an Argumenten, die Bestehendes brechen, erhöhen die Hauptversion | Verhindert stilles Brechen, wenn der Performer getrennt aktualisiert wird |
