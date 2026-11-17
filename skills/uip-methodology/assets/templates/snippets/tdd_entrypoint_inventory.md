{%- if project and project.entryPoints %}
| Workflow | Stage | In | Out |
| --- | --- | --- | --- |
{%- for ep in project.entryPoints %}
{%- set in_args = [] -%}
{%- for arg in ep.input -%}
  {%- set _ = in_args.append('`' + arg.name + ': ' + arg.type + ('*' if arg.hasDefault else '') + '`') -%}
{%- endfor -%}
{%- set out_args = [] -%}
{%- for arg in ep.output -%}
  {%- set _ = out_args.append('`' + arg.name + ': ' + arg.type + '`') -%}
{%- endfor %}
| `{{ ep.filePath }}` | {{ ep.filePath | to_stage }} | {{ in_args | join(', ') }} | {{ out_args | join(', ') or '—' }} |
{%- endfor %}
{%- else %}
| Workflow | Stage | In | Out |
| --- | --- | --- | --- |
| [TBD] | [TBD] | [TBD] | [TBD] |
{%- endif %}
