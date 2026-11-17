# Technisches Design-Dokument (TDD)

**Prozess- / Master-Projektname:** {{ process_name or "[TBD]" }}

<!-- #region tdd_header -->
| Position | Wert |
| --- | --- |
| TDD-Version | 0.1 |
| TDD-Datum | [JJJJ-MM-TT] |
| TDD-Status | Entwurf |
| SDD-Referenz | [TBD] |
<!-- #endregion tdd_header -->

## Dokumentenhistorie

<!-- #region tdd_history -->
| Version | Datum | Autor | Rolle | Änderungen |
| --- | --- | --- | --- | --- |
| 1.0 | [JJJJ-MM-TT] | [TBD] | RPA-Entwickler | Erster Entwurf |
<!-- #endregion tdd_history -->

## Freigaben

<!-- #region tdd_approvals -->
| Version | Rolle | Name | Abteilung | Datum |
| --- | --- | --- | --- | --- |
| 1.0 | Solution Architect | [TBD] | [TBD] | |
| 1.0 | Entwicklungsleitung | [TBD] | [TBD] | |
<!-- #endregion tdd_approvals -->

## 1. Umsetzungsüberblick

### 1.1 Lösungsstruktur

<!-- #region tdd_environment -->
| Position | Wert |
| --- | --- |
| GitHub-Organisation | [TBD] |
| GitHub-Repository | [TBD] |
| UiPath-Studio-Version | [TBD] |
| Ziel-Roboterversion(en) | [TBD] |
| Ausdruckssprache | [TBD] |
| Zielframework | [TBD] |
| Regelsatz des Workflow Analyzers | [TBD] |
| CI/CD eingerichtet | [TBD] |
| Entwicklungsumgebung | [TBD] |
| Konfigurationsmethode | [TBD] |
<!-- #endregion tdd_environment -->

### 1.2 Lösungskomponenten

| Komponente | Archetyp | Einstiegspunkt | Warteschlange (Eingang) | Warteschlange (Ausgang) |
| --- | --- | --- | --- | --- |
| [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |

### 1.3 Einstiegspunkte

Genauer Argumentvertrag für jede Workflow-Datei — maßgebliche Quelle ist `project.json`. Er bestimmt die Variablendeklarationen und die Verdrahtung von „Invoke Workflow". Die Workflows der REFramework-Hülle (`Main.xaml`, `Init*`, `GetTransactionData.xaml`, `SetTransactionStatus.xaml`, `CloseAllApplications.xaml`) folgen dem Standardvertrag des REFramework; hier nur aufführen, wenn ihre Argumente davon abweichen.

<!-- Eine Zeile je Einstiegspunkt. Die Spalten Eingabe/Ausgabe listen die Argumente als `name: Typ` — ein Stern (*) kennzeichnet Argumente mit einem im XAML festgelegten Standardwert. Quelle: project.json entryPoints. -->

<!-- #region tdd_entrypoint_inventory -->
| Workflow | Stufe | Eingabe | Ausgabe |
| --- | --- | --- | --- |
| [TBD] | [TBD] | [TBD] | [TBD] |
<!-- #endregion tdd_entrypoint_inventory -->

### 1.4 Branching-Strategie

<!-- #region tdd_branching -->
| Branch | Muster | Umgebung | Deploy-Auslöser | Geschützt | Zweck |
| --- | --- | --- | --- | --- | --- |
| `main` | exakt | Produktion | Merge des Pull Requests | ja | Stabiles Release |
| `uat` | exakt | UAT | Merge des Pull Requests | ja | Validierung vor dem Release |
| `development` | `development*` | Entwicklung | Push | nein | Aktive Entwicklung |
<!-- #endregion tdd_branching -->

### 1.5 Deployment-Ziele

| Umgebung | Orchestrator-Ordner | Roboterkonto | Zielsystem(e) | Hinweise |
| --- | --- | --- | --- | --- |
| Entwicklung | [TBD] | [TBD] | [TBD] | |
| Test (UAT) | [TBD] | [TBD] | [TBD] | |
| Produktion | [TBD] | [TBD] | [TBD] | |

## 2. Domänenverträge

### 2.1 Domänenmodell

Jede Domänenentität festhalten, mit der das Projekt arbeitet — Feldnamen, Typen, Kennungen, Nullbarkeit, Enum-Werte, Umwandlungsregeln und den Pfad der DTO-Klasse. Dies ist die maßgebliche Quelle für die DTO-Generierung und die Variablendeklarationen der Workflows.

<!-- Je Entität: alle Felder mit Typ, Pflicht, Kennungs-Kennzeichen, Nullbarkeit, Enum-Werten (falls zutreffend), Übertragungsformat (z. B. DD.MM.YYYY) und einem repräsentativen Beispiel. Für jedes Feld, das zur Laufzeit umgewandelt werden muss, eine Umwandlungstabelle ergänzen. -->

<!-- #region tdd_data_model -->
#### [TBD]

**DTO:** [TBD]  
**Quelle:** [TBD]  
**Ziel:** [TBD]

##### Felder

| Feld | Typ | Pflicht | Kennung | Nullable | Enum | Format | Beispiel |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [TBD] | | | | | | | |

##### Umwandlungen

| Von | Nach | Regel | Verlustfrei |
| --- | --- | --- | --- |
| [TBD] | | | |

##### C#-Typen

```csharp
// [TBD]
```
<!-- #endregion tdd_data_model -->

### 2.2 Feldzuordnungsverträge

| Quellfeld | Quellsystem | Zielfeld | Zielsystem | Transformation |
| --- | --- | --- | --- | --- |
| [TBD] | | | | |

### 2.3 Validierungsregeln

Eine Zeile je Prüfung auf Feldebene. Prüfungen der Enum-Zugehörigkeit werden automatisch aus dem Domänenmodell abgeleitet; ausdrückliche Zeilen decken Wertebereich, Muster und Längenbeschränkungen ab. Werte für `on_failure`: `BusinessRuleException`, `SystemException`, `Warn`, `Skip`.

<!-- #region tdd_validation_rules -->
#### [TBD]

| Feld | Regel | Bei Fehler |
| --- | --- | --- |
| [TBD] | | |
<!-- #endregion tdd_validation_rules -->

### 2.4 Serialisierung und Formate

| Feld | Übertragungsformat | Kultur | Beispiel |
| --- | --- | --- | --- |
| [TBD] | | | |

## 3. Umsetzung der Komponenten

Ein Unterabschnitt je Komponente aus Abschnitt 1.2. Die Struktur folgt dem Archetyp der Komponente.

### 3.1 `[TBD]` *(rpa_dispatcher)*

| Workflow | Verantwortung | Eingabe | Ausgabe |
| --- | --- | --- | --- |
| [TBD] | | | |

### 3.2 `[TBD]` *(rpa_performer)*

Auf Basis des REFramework. Eine Transaktion = ein Queue-Element. Reference des Queue-Elements = [TBD].

#### initialize

[TBD]

#### ingest

[TBD]

#### enrich

[TBD]

#### decide

[TBD]

#### execute

[TBD]

#### complete

[TBD]

#### finalize

[TBD]

### 3.3 `[TBD]` *(rpa_aggregator)* *(optional)*

| Workflow | Verantwortung | Eingabe | Ausgabe |
| --- | --- | --- | --- |
| [TBD] | | | |

## 4. Umsetzung der Integration

### 4.1 Anwendungsautomatisierung

| Operation | Umfang | Oberfläche | Adapter | Hinweise |
| --- | --- | --- | --- | --- |
| [TBD] | | | | |

### 4.2 E-Mail-Verarbeitung

| Postfach | Protokoll | Ordner | Filter | Ausgabe |
| --- | --- | --- | --- | --- |
| [TBD] | | | | |

### 4.3 Dateiverarbeitung

| Dateityp | Quelle | Methode | Ausgabe |
| --- | --- | --- | --- |
| [TBD] | | | |

### 4.4 Warteschlangenverträge

| Warteschlange | Richtung | Elementschema | Max. Wiederholungen | Dead-Letter |
| --- | --- | --- | --- | --- |
| [TBD] | | | | |

### 4.5 Externe APIs *(optional)*

| API | Endpunkt | Authentifizierung | Hinweise |
| --- | --- | --- | --- |
| [TBD] | | | |

## 5. Umsetzung von Ausnahmen und Wiederherstellung

### 5.1 Fachliche Ausnahmen

| Ausnahme | Bedingung | Queue-Status | Benachrichtigung |
| --- | --- | --- | --- |
| [TBD] | | | |

### 5.2 Systemausnahmen

| Ausnahme | Bedingung | Wiederholung | Bei Ausschöpfung |
| --- | --- | --- | --- |
| [TBD] | | | |

### 5.3 Wiederholungslogik

| Bereich | Max. Wiederholungen | Strategie | Konfigurationsschlüssel |
| --- | --- | --- | --- |
| Transaktion (REF) | [TBD] | [TBD] | `MaxRetryNumber` |
| GetTransactionItem | [TBD] | [TBD] | `RetryNumberGetTransactionItem` |
| SetTransactionStatus | [TBD] | [TBD] | `RetryNumberSetTransactionStatus` |
| Aufeinanderfolgende Systemausnahmen | [TBD] | [TBD] | `MaxConsecutiveSystemExceptions` |

### 5.4 Protokollierung und Nachweise

| Ereignis | Log-Stufe | Nachweis | Hinweise |
| --- | --- | --- | --- |
| Beginn der Transaktion | INFO | [TBD] | |
| Fachliche Ausnahme | WARN | [TBD] | |
| Systemausnahme | ERROR | [DEFAULT: Screenshot + Stacktrace] | gespeichert unter `ExScreenshotsFolderPath` |
| Ende des Jobs | INFO | [DEFAULT: Anzahl der Transaktionen, Summen für Erfolg/Fehler] | |

## 6. Konfiguration und Abhängigkeiten

Konfigurationsklasse `CodedConfig` — von ConFormMold aus TOML-Dateien je Umgebung erzeugt (`Config_Dev.toml`, `Config_Test.toml`, `Config_Prod.toml`). Wird beim Start des Roboters mit `CodedConfig.Load()` geladen. Mit `--config-dev`, `--config-test` und `--config-prod` an `cpm-rpa render` wird sie automatisch befüllt.

<!-- #region tdd_process_configuration -->
#### Einstellungen

| Eigenschaft | Typ | DEV | TEST | PROD |
| --- | --- | --- | --- | --- |
| [TBD] | | | | |

#### Konstanten

| Eigenschaft | Typ | DEV | TEST | PROD |
| --- | --- | --- | --- | --- |
| [TBD] | | | | |

#### Assets

| Eigenschaft | Typ | DEV | TEST | PROD |
| --- | --- | --- | --- | --- |
| [TBD] | | | | |
<!-- #endregion tdd_process_configuration -->

### 6.4 UiPath-Abhängigkeiten

UiPath-Aktivitätspakete — maßgebliche Quelle ist `project.json`. Laufzeitregel: Strikt = nur die festgelegte Version wird verwendet; Niedrigste passende Version = es wird nach oben aufgelöst, wenn die genaue Version nicht verfügbar ist.

<!-- #region tdd_uipath_dependencies -->
| Paket | Version | Regel | Zweck |
| --- | --- | --- | --- |
| `UiPath.Excel.Activities` | [2.24.3] | Strikt | Excel lesen und schreiben |
| `UiPath.Mail.Activities` | [2.2.10] | Strikt | E-Mail über SMTP / IMAP / Exchange |
| `UiPath.MicrosoftOffice365.Activities` | [2.7.24] | Strikt | Microsoft 365 — Mail, Teams, SharePoint |
| `UiPath.System.Activities` | [24.10.4] | Strikt | Zentrale Workflow-Aktivitäten |
| `UiPath.Testing.Activities` | [24.10.4] | Strikt | Framework für Testautomatisierung |
| `UiPath.UIAutomation.Activities` | [25.10.12] | Strikt | UI-Automatisierung — Desktop und Web |
<!-- #endregion tdd_uipath_dependencies -->

### 6.5 Wiederverwendete Komponenten / Bibliotheken

Abhängigkeiten von Bibliotheken außerhalb von UiPath — aus `project.json`. Interne Bibliotheken und Pakete von Drittanbietern, die keine UiPath-Standardpakete für Aktivitäten sind.

<!-- #region tdd_reused_libraries -->
entfällt — keine Bibliotheksabhängigkeiten außerhalb von UiPath.
<!-- #endregion tdd_reused_libraries -->

### 6.6 Neue wiederverwendbare Komponenten

| Komponente | Zweck | Platzhalter im Automation Hub |
| --- | --- | --- |
| [TBD] | | |

## 7. Testverträge

### 7.1 Unit-Test-Szenarien

| Nr. | Szenario | Eingabe | Erwartetes Ergebnis |
| --- | --- | --- | --- |
| [TBD] | | | |

### 7.2 Integrationstest-Szenarien

| Nr. | Szenario | Vorbedingung | Erwartetes Ergebnis |
| --- | --- | --- | --- |
| [TBD] | | | |

### 7.3 Testdatenanforderungen

| Datensatz | Quelle | Umfang | Hinweise |
| --- | --- | --- | --- |
| [TBD] | | | |

### 7.4 Abnahmebedingungen

| Nr. | Bedingung | Prüfmethode |
| --- | --- | --- |
| [TBD] | | |
| [TBD] | [DEFAULT: Keine fest codierten Zugangsdaten] | [DEFAULT: Statische Codeanalyse + Prüfung auf Zugangsdaten] |

## 8. Betriebsbereitschaft

### 8.1 Deployment-Parameter

<!-- #region tdd_deployment_parameters -->
| Position | Wert |
| --- | --- |
| Produktionsumgebung | [TBD] |
| Auslöser / Zeitplan | [TBD] |
| Prozesseingang | [TBD] |
| Erwartete Ausgabe | [TBD] |
| Orchestrator-Warteschlangen | [TBD] |
| Namen der Orchestrator-Assets | [TBD] |
| Ablage der Zugangsdaten | [DEFAULT: Orchestrator-Assets (Typ Credential) — nie fest im Code] |
| Mehrere Auflösungen unterstützt | [TBD] |
| Empfohlene Auflösung | [TBD] |
<!-- #endregion tdd_deployment_parameters -->

### 8.2 Monitoring-Hooks

| Hook | Auslöser | Ziel | Hinweise |
| --- | --- | --- | --- |
| [TBD] | | | |

### 8.3 Support-Anforderungen

| Anforderung | Einzelheiten |
| --- | --- |
| [TBD] | |

## 9. Offene technische Punkte

<!-- #region observations_issues -->
*Keine offenen Punkte.*
<!-- #endregion observations_issues -->
