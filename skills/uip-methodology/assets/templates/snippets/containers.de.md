{%- if containers %}
| ID | Komponente | Archetyp | Framework | Auslöser | Laufzeit | Grenze der Warteschlange |
| --- | --- | --- | --- | --- | --- | --- |
{%- for c in containers %}
| `{{ c.id or gen_id('cmp', c.name) }}` | {{ c.name }} | {{ c.archetype or "[TBD]" }} | {{ c.framework or "[TBD]" }} | {{ c.trigger or "[TBD]" }} | {{ c.runtime or "Unbeaufsichtigt" }} | {{ c.queue_writes and ("Schreibt -> `" + c.queue_writes + "`") or c.queue_reads and ("Liest <- `" + c.queue_reads + "`") or "—" }} |
{%- endfor %}
{%- else %}
| ID | Komponente | Archetyp | Framework | Auslöser | Laufzeit | Grenze der Warteschlange |
| --- | --- | --- | --- | --- | --- | --- |
| `cmp_[tbd]` | `[TBD]_Dispatcher` | rpa_dispatcher | Linearer Workflow | Zeitgesteuert — [TBD] | Unbeaufsichtigt | Schreibt -> `[TBD]` |
| `cmp_[tbd]` | `[TBD]_Performer` | rpa_performer | REFramework | Durch die Warteschlange ausgelöst + zeitgesteuertes Stoppsignal | Unbeaufsichtigt | Liest <- `[TBD]` |
| `cmp_[tbd]` | `[TBD]_Aggregator` | rpa_aggregator | Linearer Workflow | Zeitgesteuert — [TBD] | Unbeaufsichtigt | *(optional — entfernen, wenn nicht zutreffend)* |
{%- endif %}
