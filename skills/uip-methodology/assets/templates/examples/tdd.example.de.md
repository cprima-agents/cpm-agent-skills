# TDD-Beispiel — so sehen die ausgefüllten Abschnitte aus

Beispielinhalt (ein Roboter für die Rechnungsbuchung) für die statischen Abschnitte von `tdd-template.de.md`. Er wird nie
gerendert. Die Regionen mit Snippet haben ihre eigenen Beispiele neben ihren Snippets: `snippets/tdd_*.example.de.md`.

### 1.2 Lösungskomponenten

| Komponente | Archetyp | Einstiegspunkt | Warteschlange (Eingang) | Warteschlange (Ausgang) |
| --- | --- | --- | --- | --- |
| `InvoicePosting.Dispatcher` | rpa_dispatcher | `Dispatcher.xaml` | — | InvoicePosting |
| `InvoicePosting.Performer` | rpa_performer | `Performer.xaml` | InvoicePosting | — |
| `InvoicePosting.Aggregator` | rpa_aggregator | `Aggregator.xaml` | — | — |

### 1.5 Deployment-Ziele

| Umgebung | Orchestrator-Ordner | Roboterkonto | SAP-System | Hinweise |
| --- | --- | --- | --- | --- |
| Entwicklung | cg371p/Dev | cg371p | DEV (100) | SAP-Adapter: mock |
| Test (UAT) | cg371p/Test | cg371p | TST (200) | SAP-Adapter: live |
| Produktion | cg371p/Shared | cg371p | PRD (300) | SAP-Adapter: live |

### 2.2 Feldzuordnungsverträge

| Quellfeld | Quellsystem | Zielfeld | Zielsystem | Transformation |
| --- | --- | --- | --- | --- |
| invoice_number | Betreff im AP-Postfach | InvoiceNumber | SAP MIRO | keine |
| total_amount | PDF | TotalAmount | SAP MIRO | DE-Dezimal → decimal |
| invoice_date | PDF | InvoiceDate | SAP MIRO | DD.MM.YYYY → DateTime |

### 2.4 Serialisierung und Formate

| Feld | Übertragungsformat | Kultur | Beispiel |
| --- | --- | --- | --- |
| invoice_date | DD.MM.YYYY | de-DE | 15.01.2024 |
| total_amount | #.##0,00 | de-DE | 1.234,56 |
| unit_price | #.##0,00 | de-DE | 12,50 |
| po_item | 5-stellig, mit führenden Nullen | — | 00010 |

### 3.1 `InvoicePosting.Dispatcher` *(rpa_dispatcher)*

| Workflow | Verantwortung | Eingabe | Ausgabe |
| --- | --- | --- | --- |
| `Process/ReadMailbox.xaml` | Ungelesene E-Mails aus dem AP-Postfach lesen | Name des Postfachordners | Liste von MailMessage |
| `Process/ExtractInvoice.xaml` | InvoiceDto aus E-Mail + PDF extrahieren | MailMessage | InvoiceDto |
| `Process/EnqueueInvoice.xaml` | InvoiceDto in die Orchestrator-Warteschlange einstellen | InvoiceDto, Warteschlangenname | Referenz auf das QueueItem |

### 3.2 `InvoicePosting.Performer` *(rpa_performer)*

Auf Basis des REFramework. Eine Transaktion = ein Queue-Element von InvoicePosting. Reference des Queue-Elements = invoice_number.

#### initialize

Zugangsdaten (`cred_SAP_Prod`, `cred_SMTP`) aus den Orchestrator-Assets holen. `CodedConfig` laden. SAP-Anmeldung prüfen.

#### ingest

Die JSON-Nutzdaten des Queue-Elements in `InvoiceDto` deserialisieren. Pflichtfelder prüfen; bei einem Verstoß eine `BusinessRuleException` auslösen.

#### enrich

Den Bestellkopf in SAP MM03 nachschlagen, um zu bestätigen, dass po_number existiert und offen ist. vendor_id in die SAP-Lieferantenkontonummer auflösen.

#### decide

Routing-Regeln anwenden: ablehnen, wenn total_amount ≤ 0 ist oder po_number fehlt → `BusinessRuleException`. An die manuelle Bearbeitung weiterleiten, wenn currency ∉ {EUR, USD, GBP}.

#### execute

In SAP zu MIRO navigieren. Rechnungskopf eingeben (Lieferant, Datum, Betrag, Währung). Positionen buchen. FI-Belegnummer erfassen. Bei einem Fehler einen Screenshot aufnehmen.

#### complete

Status des Queue-Elements mit der Ausgabe `{fi_document: "...", posted_at: "..."}` auf Succeeded setzen. INFO mit der FI-Belegnummer protokollieren.

#### finalize

Den SAP-MIRO-Tab schließen. Zwischenablage leeren. Eine Zusammenfassung der Sitzung protokollieren.

### 3.3 `InvoicePosting.Aggregator` *(rpa_aggregator)* *(optional)*

| Workflow | Verantwortung | Eingabe | Ausgabe |
| --- | --- | --- | --- |
| `Aggregator.xaml` | Tägliche Zusammenfassung der Buchungen erstellen | Berichtsdatum, Ausgabeordner | XLSX-Berichtsdatei |

### 4.1 SAP-Automatisierung

| Transaktion | Umfang | Oberfläche | SAP-Adapter | Hinweise |
| --- | --- | --- | --- | --- |
| MIRO | Rechnungsbuchung | UI (SAP GUI) | mock (DEV) / live (TEST, PROD) | Nutzt die Bibliothek CPMForge.SAP |
| MM03 | Bestellabfrage / -prüfung | UI (SAP GUI) | mock (DEV) / live (TEST, PROD) | Nur lesend |

### 4.2 E-Mail-Verarbeitung

| Postfach | Protokoll | Ordner | Filter | Ausgabe |
| --- | --- | --- | --- | --- |
| AP-Postfach | IMAP / Exchange | Posteingang | Betreff enthält „Invoice" | MailMessage-Liste |

### 4.3 Dateiverarbeitung

| Dateityp | Quelle | Methode | Ausgabe |
| --- | --- | --- | --- |
| PDF (Rechnung) | E-Mail-Anhang | Document Understanding / Extraktion per Regex | Felder von InvoiceDto |

### 4.4 Warteschlangenverträge

| Warteschlange | Richtung | Elementschema | Max. Wiederholungen | Dead-Letter |
| --- | --- | --- | --- | --- |
| InvoicePosting | Eingang des Performers | InvoiceDto (JSON) | 0 (PROD), 1 (DEV/TEST) | Shared/dead-letter |
| InvoicePosting_Dispatcher | Ausgang des Dispatchers | InvoiceDto (JSON) | — | — |

### 5.1 Fachliche Ausnahmen

| Ausnahme | Bedingung | Queue-Status | Benachrichtigung |
| --- | --- | --- | --- |
| InvalidInvoiceNumber | invoice_number leer oder im falschen Format | Failed | SMTP-Alarm an das AP-Team |
| MissingPoNumber | po_number leer oder Bestellung in SAP nicht gefunden | Failed | SMTP-Alarm an das AP-Team |
| UnsupportedCurrency | currency ∉ {EUR, USD, GBP} | Failed | SMTP-Alarm |

### 5.2 Systemausnahmen

| Ausnahme | Bedingung | Wiederholung | Bei Ausschöpfung |
| --- | --- | --- | --- |
| SapLoginException | SAP-Anmeldung schlägt fehl | bis MaxConsecutiveSystemExceptions | Job im Status Faulted |
| SapTimeoutException | Zeitüberschreitung im MIRO-Bild | bis MaxConsecutiveSystemExceptions | Job im Status Faulted |

### 5.3 Wiederholungslogik

| Bereich | Max. Wiederholungen | Strategie | Konfigurationsschlüssel |
| --- | --- | --- | --- |
| Transaktion (REF) | 0 (PROD), 1 (DEV/TEST) | sofortige Wiedereinreihung | `MaxRetryNumber` |
| GetTransactionItem | 2 | sofort | `RetryNumberGetTransactionItem` |
| SetTransactionStatus | 2 | sofort | `RetryNumberSetTransactionStatus` |
| Aufeinanderfolgende Systemausnahmen | 3 | Job abbrechen | `MaxConsecutiveSystemExceptions` |

### 5.4 Protokollierung und Nachweise

| Ereignis | Log-Stufe | Nachweis | Hinweise |
| --- | --- | --- | --- |
| Beginn der Transaktion | INFO | Reference des Queue-Elements | |
| SAP-FI-Beleg gebucht | INFO | FI-Belegnummer | |
| Fachliche Ausnahme | WARN | Ausnahmemeldung + invoice_number | |
| Systemausnahme | ERROR | Screenshot + Stacktrace | gespeichert unter `ExScreenshotsFolderPath` |
| Ende des Jobs | INFO | Anzahl der Transaktionen, Summen für Erfolg/Fehler | |

### 7.1 Unit-Test-Szenarien

| Nr. | Szenario | Eingabe | Erwartetes Ergebnis |
| --- | --- | --- | --- |
| U-01 | Gültige Rechnung wird korrekt eingelesen | Rechnungs-PDF mit allen Pflichtfeldern | InvoiceDto befüllt, keine Ausnahme |
| U-02 | Fehlende Bestellnummer löst BusinessRuleException aus | InvoiceDto mit po_number = null | BusinessRuleException |
| U-03 | Normalisierung des deutschen Dezimalformats | "1.234,56" | 1234.56m |

### 7.2 Integrationstest-Szenarien

| Nr. | Szenario | Vorbedingung | Erwartetes Ergebnis |
| --- | --- | --- | --- |
| I-01 | Durchgängige Buchung in SAP TST | Gültiges Queue-Element mit Rechnung, SAP TST erreichbar | FI-Beleg erstellt, Element = Succeeded |
| I-02 | Ungültige Bestellung wird sauber abgelehnt | Queue-Element mit nicht vorhandener Bestellung | Element = Failed, SMTP-Alarm gesendet |

### 7.3 Testdatenanforderungen

| Datensatz | Quelle | Umfang | Hinweise |
| --- | --- | --- | --- |
| Rechnungs-PDFs (gültig) | Beispiel-E-Mails des AP | ≥ 10 | Währungen EUR / USD / GBP abdecken |
| Rechnungs-PDFs (ungültig) | Synthetisch | ≥ 5 | Fehlende Bestellung, falsches Format, Betrag null |
| SAP-MIRO-Testlieferanten | SAP TST | ≥ 3 | Müssen offene Bestellungen haben |

### 7.4 Abnahmebedingungen

| Nr. | Bedingung | Prüfmethode |
| --- | --- | --- |
| A-01 | Alle gültigen Rechnungen werden ohne manuellen Eingriff gebucht | Erfolgsquote des Integrationstests I-01 = 100 % |
| A-02 | Fachliche Ausnahmen lösen innerhalb von 5 Minuten einen SMTP-Alarm aus | Test I-02 + Prüfung des Posteingangs |
| A-03 | Keine fest codierten Zugangsdaten | Statische Codeanalyse + Prüfung auf Zugangsdaten |

### 8.2 Monitoring-Hooks

| Hook | Auslöser | Ziel | Hinweise |
| --- | --- | --- | --- |
| Alarm bei Job im Status Faulted | ShouldMarkJobAsFaulted = true | Orchestrator-Alarm / SMTP | Nur PROD |
| Alarm bei fachlicher Ausnahme | BusinessRuleException abgefangen | SMTP → AP-Team | Alle Umgebungen |

### 8.3 Support-Anforderungen

| Anforderung | Einzelheiten |
| --- | --- |
| Zugriff des Roboterkontos | cg371p muss auf SAP PRD und dem AP-Postfach freigeschaltet sein |
| Überwachung der Orchestrator-Warteschlangen | Dead-Letter-Warteschlange Shared/dead-letter wird täglich geprüft |
| Aufbewahrung von Screenshots | Ordner Exceptions_Screenshots — 30 Tage Aufbewahrung |
