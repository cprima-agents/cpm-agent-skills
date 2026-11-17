{%- set c = namespace(found=none) %}
{%- for item in (containers or []) %}
{%- if item.archetype == "rpa_library" and c.found is none %}
{%- set c.found = item %}
{%- endif %}
{%- endfor %}
{%- set f = c.found or {} %}
[TBD — one paragraph: what reusable capability this library provides, which components consume it, and why it was factored out as a library rather than inlined.]

| Item | Decision | Rationale |
| --- | --- | --- |
| NuGet package ID | [TBD — e.g. `Org.RPA.Team.{{ f.name or "[Name]" }}`] | |
| Exported workflows | [TBD — Name(InputArg: type, …) → OutputArg: type] | Public API of the library |
| Consumers | [TBD — which components from section 3.3 import this library] | |
| Framework | {{ f.framework or "[TBD — XAML / Coded / Hybrid]" }} | |
| Config passing | Arguments only — no Orchestrator Assets | Library has no robot runtime context; callers pass all config |
| Versioning strategy | SemVer — breaking argument changes bump major version | Prevents silent breakage in consuming projects |
