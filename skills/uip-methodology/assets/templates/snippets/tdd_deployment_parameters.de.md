| Position | Wert |
| --- | --- |
| Produktionsumgebung | {{ production_environment or '[TBD]' }} |
| Auslöser / Zeitplan | {{ trigger_schedule or '[TBD]' }} |
| Prozesseingang | {{ process_input or '[TBD]' }} |
| Erwartete Ausgabe | {{ expected_output or '[TBD]' }} |
| Orchestrator-Warteschlangen | {{ orchestrator_queues or '[TBD]' }} |
| Namen der Orchestrator-Assets | {{ orchestrator_asset_names or '[TBD]' }} |
| Ablage der Zugangsdaten | {{ credentials_storage or '[DEFAULT: Orchestrator-Assets (Typ Credential) — nie fest im Code]' }} |
| Mehrere Auflösungen unterstützt | {{ multiple_resolutions_supported or '[TBD]' }} |
| Empfohlene Auflösung | {{ recommended_resolution or '[TBD]' }} |
