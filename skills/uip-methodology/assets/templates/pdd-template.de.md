# Prozessdefinitionsdokument (PDD)

**Prozessname:** {{ process_name or "[TBD]" }}

<!-- #region pdd_header -->
| Position | Wert |
| --- | --- |
| PDD-Version | 0.1 |
| PDD-Datum | [JJJJ-MM-TT] |
| PDD-Status | Entwurf |
<!-- #endregion pdd_header -->

## Dokumentenhistorie

<!-- #region pdd_history -->
| Version | Datum | Autor | Rolle | Änderungen |
| --- | --- | --- | --- | --- |
| 1.0 | [JJJJ-MM-TT] | [TBD] | Business Analyst | Erster Entwurf |
<!-- #endregion pdd_history -->

## Freigaben

<!-- #region pdd_approvals -->
| Version | Rolle | Name | Abteilung | Datum |
| --- | --- | --- | --- | --- |
| 1.0 | Prozessverantwortlicher | [TBD] | [TBD] | |
<!-- #endregion pdd_approvals -->

## Zusammenfassung

<!-- #region executive_summary -->
[TBD]
<!-- #endregion executive_summary -->

## 1. Einleitung

### 1.1 Ziele

Die messbaren fachlichen Ergebnisse festhalten, die von der Automatisierung erwartet werden, damit das Projektteam den Erfolg der Lieferung beurteilen kann.

<!-- #region objectives -->
- [TBD]
- [TBD]
<!-- #endregion objectives -->

### 1.2 Beteiligte

Alle wichtigen Ansprechpartner festhalten, damit jeder weiß, an wen er sich für fachliche Entscheidungen, Freigaben, Systemzugriff und Compliance wenden kann.

<!-- #region contacts_business -->
[TBD]
<!-- #endregion contacts_business -->

### 1.3 Voraussetzungen für die Automatisierung

Die Bedingungen auflisten, die vor Beginn der Entwicklung erfüllt sein müssen, damit Hindernisse vom ersten Projekttag an sichtbar sind und jemandem gehören.

<!-- #region prerequisites -->
| Kriterium | Status |
| --- | --- |
| Vollständiges und freigegebenes PDD | Offen |
<!-- #endregion prerequisites -->

## 2. AS-IS-Prozessbeschreibung

### 2.1 Prozessname und Verantwortung

Die offizielle Bezeichnung des Prozesses und die Verantwortlichkeiten festlegen, bevor die Konzeption beginnt.

<!-- #region process_overview -->
| Position | Wert |
| --- | --- |
| Prozessname | [TBD] |
<!-- #endregion process_overview -->

### 2.2 Volumen, Spitzen und Häufigkeit

Durchsatz, Spitzenlast und Zeitpunkte beziffern, damit die Architektur richtig bemessen und Service Level festgelegt werden können.

<!-- #region volume -->
| Position | Wert |
| --- | --- |
| Zeitplan | [TBD] |
<!-- #endregion volume -->

### 2.3 Anwendungsliste

Jede Anwendung und Plattformkomponente auflisten, mit der der Roboter arbeiten muss.

<!-- #region applications -->
[TBD]
<!-- #endregion applications -->

### 2.4 AS-IS-Prozessdiagramm

<!-- Das Übersichtsdiagramm wird aus process.yaml erzeugt (render-diagrams, dann build-data --diagrams-dir): als Bild, wenn der Export möglich war, sonst als Mermaid-Text, sonst [TBD]. -->

<!-- #region process_map -->
[TBD — Übersichtsdiagramm beifügen]
<!-- #endregion process_map -->

### 2.5 AS-IS-Prozessschritte

Jeden Schritt abbilden, einschließlich Verzweigungen, Ausnahmen und Systemkontakten. Die Schrittnummern werden aus den Verbindungen im Prozess-Yaml abgeleitet und nie von Hand gepflegt.

<!-- #region process_steps -->
[TBD]
<!-- #endregion process_steps -->

### 2.6 Beschreibung der Eingabedaten

Jede Eingabe auflisten, mit der der Prozess arbeitet: woher sie kommt und in welcher Form.

<!-- #region process_data -->
| Eingabe | Schritte | Quellsystem | Eingabeformat | Ablageort | Strukturiert |
| --- | --- | --- | --- | --- | --- |
| [TBD] | | | | | |
<!-- #endregion process_data -->

<!-- Strukturiert: feste Felder, maschinenlesbar, z. B. Excel-Zelle, Formularfeld auf dem Bildschirm. Nicht strukturiert: PDF ohne eingebettete Felder, gescanntes Bild, Freitext. -->

## 3. TO-BE-Prozessbeschreibung

### 3.1 TO-BE-Prozessdiagramm

<!-- Aus process.yaml erzeugt: die Pipeline-Stufen des Roboterlaufs und was in jeder geschieht. -->

<!-- #region pipeline_stages -->
[TBD — TO-BE-Diagramm mit hervorgehobenen automatisierten Schritten beifügen]
<!-- #endregion pipeline_stages -->

### 3.2 Parallele Initiativen

Gleichzeitig laufende Projekte erfassen, die Schritte, Systeme oder Daten mit dieser Automatisierung teilen.

<!-- #region parallel_initiatives -->
| Initiative | Betroffene Schritte | Auswirkung auf die Automatisierung | Voraussichtliche Fertigstellung | Kontakt |
| --- | --- | --- | --- | --- |
| entfällt | | | | |
<!-- #endregion parallel_initiatives -->

### 3.3 Im Umfang / Außerhalb des Umfangs

Eine klare Grenze um das ziehen, was dieser Release automatisiert.

#### Im Umfang

<!-- #region in_scope -->
| Schritt | Beschreibung |
| --- | --- |
| [TBD] | |
<!-- #endregion in_scope -->

#### Außerhalb des Umfangs

<!-- #region out_of_scope -->
| Tätigkeit / Schritt | Grund | Auswirkung auf TO-BE | Weg zur künftigen Automatisierung |
| --- | --- | --- | --- |
| [TBD] | | | |
<!-- #endregion out_of_scope -->

### 3.4 Fachliche Ausnahmen

Die Datenbedingungen aufzählen, bei denen ein Vorgang nicht bearbeitet werden kann, damit der Roboter sie geordnet behandelt.

#### Bekannte fachliche Ausnahmen

<!-- #region business_exceptions -->
[TBD]
<!-- #endregion business_exceptions -->

#### Standardbehandlung unvorhergesehener fachlicher Ausnahmen

<!-- #region default_be_handling -->
- E-Mail an `[TBD — exceptions@company.com]` mit Screenshot senden
- Den Vorgang im Orchestrator als „Business Exception" protokollieren
- Mit dem nächsten Vorgang fortfahren
<!-- #endregion default_be_handling -->

### 3.5 Anwendungsfehler und Fehlerbehandlung

Bekannte Anwendungsfehler festhalten und das Verhalten des Roboters bei der Wiederherstellung festlegen.

#### Bekannte Anwendungsfehler

<!-- #region application_errors -->
[TBD]
<!-- #endregion application_errors -->

#### Standardbehandlung unvorhergesehener Anwendungsfehler

<!-- #region default_se_handling -->
- Den aktuellen Schritt bis zu `[DEFAULT: 3]`-mal wiederholen
- Falls ungelöst: Fehler protokollieren, Alarm an `[TBD — ops@company.com]` senden, sauber beenden
<!-- #endregion default_se_handling -->

### 3.6 Berichtsanforderungen

Die Überwachungs- und Berichtsausgaben festlegen, die Fachbereich und Betrieb brauchen.

<!-- #region reporting_requirements -->
| Nr. | Berichtsart | Häufigkeit | Einzelheiten | Werkzeug |
| --- | --- | --- | --- | --- |
| 1 | [TBD] | | | |
<!-- #endregion reporting_requirements -->

## 4. Entscheidungen

Die Entscheidungen, die der Prozess trifft, jeweils mit ihrer Frage, den Daten, die sie liest, und ihren Regeln. Eine Regel mit dem Status „Offen" ist von der Fachseite nicht entschieden. Die Schritte in den Kapiteln 2 und 3 verweisen hierher.

<!-- Aus decisions.yaml erzeugt: ein nummerierter Abschnitt je Entscheidung. -->

<!-- #region decisions -->
[TBD]
<!-- #endregion decisions -->

## 5. Weitere Dokumentation

[TBD]
