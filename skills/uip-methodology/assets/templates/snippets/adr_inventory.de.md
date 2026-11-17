{%- macro trunc(text, n=40) -%}
{%- set ws = text.split() -%}
{{ ws[:n] | join(' ') }}{% if ws | length > n %} …{% endif %}
{%- endmacro -%}
{%- if adrs %}
| Code | Titel | Status | Betrifft |
| --- | --- | --- | --- |
{%- for adr in adrs %}
| {{ adr.code }} | {{ adr.title }} | {{ adr.status | capitalize }} | {{ adr.affects | default([]) | join(', ') }} |
{%- endfor %}
{%- for adr in adrs %}

#### {{ adr.code }} — {{ adr.title }}

**Status:** {{ adr.status | capitalize }}
{%- if adr.affects | default([]) %}
**Betrifft:** {{ adr.affects | join(', ') }}
{%- endif %}
{%- if adr.supersedes | default([]) %}
**Ersetzt:** {{ adr.supersedes | join(', ') }}
{%- endif %}

**Kontext:** {{ trunc(adr.context) }}

**Entscheidung:** {{ trunc(adr.decision) }}
{%- endfor %}
{%- else %}
| Code | Titel | Status | Betrifft |
| --- | --- | --- | --- |
| ADR-0001 | REFramework für Performer-Projekte mit Warteschlange verwenden | Angenommen | sdd, tdd |
| ADR-0002 | Coded Config (TOML) für Laufzeiteinstellungen | Angenommen | tdd |

#### ADR-0001 — REFramework für Performer-Projekte mit Warteschlange verwenden

**Status:** Angenommen
**Betrifft:** sdd, tdd

**Kontext:** Das Performer-Projekt bearbeitet Transaktionen der Orchestrator-Warteschlange nacheinander. Eine eigene Schleife für Wiederholungen und Zustandsverwaltung würde Verhalten nachbauen, das das Standard-REFramework von UiPath bereits bietet.

**Entscheidung:** REFramework wird als Shell des Performers übernommen. Die Geschäftslogik liegt ausschließlich in Workflows unter `Process/`, die aus Process Transaction aufgerufen werden. Die Zustände Init, GetTransactionData und SetTransactionStatus bleiben unverändert …

#### ADR-0002 — Coded Config (TOML) für Laufzeiteinstellungen

**Status:** Angenommen
**Betrifft:** tdd

**Kontext:** Config.xlsx ist unter Versionskontrolle fragil: binäre Unterschiede sind unlesbar, Merge-Konflikte lassen sich nicht auflösen, und umgebungsspezifische Werte erfordern beim Deployment das manuelle Überschreiben einer Datei.

**Entscheidung:** Config.xlsx wird durch TOML-Dateien je Umgebung ersetzt (`Config_Dev.toml`, `Config_Test.toml`, `Config_Prod.toml`), die eine `CodedConfig`-Aktivität lädt. TOML ist Klartext, eignet sich für Vergleiche und unterstützt typisierte Werte ohne zusätzliche Auswertung …
{%- endif %}
