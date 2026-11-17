| Szenario | Volumen | Nötige Laufzeiten | Hinweise |
| --- | --- | --- | --- |
| Normallast | {{ daily_volume or "[TBD]" }} | {{ runtimes_standard or "[TBD]" }} | |
| Spitzenlast | {{ peak_volume or "[TBD]" }} | {{ runtimes_peak or "[TBD]" }} | Spitzenauslastung: {{ peak_utilisation_pct or "[TBD]" }}% |
| Auslöser der Skalierung | — | — | {{ scaling_trigger or "[TBD — Tiefe der Warteschlange / Zeitschwelle]" }} |
