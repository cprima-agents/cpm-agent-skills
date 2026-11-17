<!-- Nur ein Beispiel (ein erfundenes Projekt zur Rechnungsbuchung). Wird nie gerendert. So sieht ein gefüllter Bereich aus. -->

### 4.2 `InvoicePosting_Performer` *(rpa_performer)*

Eine REFramework-Transaktion = eine Lieferantenrechnung. Das `Reference` des Vorgangs trägt die Rechnungsnummer — sie dient als Schlüssel zur Duplikaterkennung und als Korrelations-ID in allen Protokollmeldungen.

Die Buchung mit SAP MIRO ist **nicht idempotent** — eine Wiederholung einer fehlgeschlagenen Buchung riskiert ein doppeltes FI-Dokument. Die Anzahl der Wiederholungen in PROD ist deshalb 0. In DEV/TEST ist eine Wiederholung erlaubt, um vorübergehende Instabilität der Testumgebung aufzufangen, ohne ein Buchungsrisiko einzugehen.

| Position | Entscheidung | Begründung |
| --- | --- | --- |
| Anzahl Wiederholungen (PROD) | 0 | Die MIRO-Buchung ist nicht idempotent — eine Wiederholung könnte ein doppeltes FI-Dokument erzeugen |
| Anzahl Wiederholungen (DEV/TEST) | 1 | Toleriert vorübergehende Instabilität von SAP TST; kein Risiko für die Produktion |
| Max. aufeinanderfolgende SE | 3 | Drei Fehler in Folge deuten auf einen Infrastrukturausfall — abbrechen und den Betrieb alarmieren |
| ShouldMarkJobAsFaulted | true (PROD) | Stellt sicher, dass der Orchestrator den Betrieb alarmiert, wenn die Abbruchschwelle erreicht ist |
| Mehrere Auflösungen | Nein | SAP GUI braucht 1920×1080; eine VM mit einer Standardauflösung genügt bei diesem Volumen |
| Gelesene Warteschlange | `InvoicePosting` | |
| Art der Konfiguration | Orchestrator-Assets / TOML | |

**Vertrag der Warteschlange (gelesen aus `InvoicePosting`):**

| Feld | Typ | Pflicht | Hinweise |
| --- | --- | --- | --- |
| Reference | string | ja | Rechnungsnummer — Schlüssel zur Duplikaterkennung; darf nie leer sein |
| vendor_id | string | ja | SAP-Kontonummer des Lieferanten |
| invoice_date | string | ja | TT.MM.JJJJ — in der Stufe Init in DateTime umgewandelt |
| total_amount | string | ja | Deutsches Dezimalformat (1.234,56) — in der Stufe Init in decimal normalisiert |
| currency | string | ja | EUR / USD / GBP — löst BE-01 aus, wenn der Wert außerhalb dieser Menge liegt |
| po_number | string | ja | Muss in SAP MM03 existieren — eine fehlende Bestellung löst BE-02 aus |
| source_email_id | string | nein | IMAP-Message-ID, für die Nachvollziehbarkeit aufbewahrt; wird in der Verarbeitung nicht genutzt |
