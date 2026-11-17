| Position | Wert |
| --- | --- |
| Produktionsumgebung | UiPath Orchestrator — cg371p / Shared (Produktions-Tenant) |
| Auslöser / Zeitplan | Täglich 06:00 Uhr MEZ, Mo–Fr, über einen Zeittrigger im Orchestrator |
| Prozesseingang | Orchestrator-Warteschlange InvoicePosting — Elemente werden vom Dispatcher eingestellt |
| Erwartete Ausgabe | SAP-MIRO-FI-Beleg gebucht; Queue-Element auf Succeeded gesetzt |
| Orchestrator-Warteschlangen | InvoicePosting (Performer), InvoicePosting_Dispatcher (Dispatcher) |
| Namen der Orchestrator-Assets | cg371p/cred_SAP_Prod, cg371p/cred_SMTP |
| Ablage der Zugangsdaten | Orchestrator-Assets (Typ Credential) — nie fest im Code |
| Mehrere Auflösungen unterstützt | Nein — getestet mit 1920×1080 |
| Empfohlene Auflösung | 1920×1080 |
