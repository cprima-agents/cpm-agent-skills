{%- if applications %}
| Name | Purpose | Automation Surface | Access Method | In Scope | Previously Automated |
| --- | --- | --- | --- | --- | --- |
{%- for a in applications %}
{%- set in_scope = ("Yes" if a.in_scope else "No") if a.in_scope is defined else "[TBD]" %}
{%- if a.previously_automated is defined %}
{%- set prev = "n/a" if a.previously_automated == "not-applicable" else ("Yes" if a.previously_automated else "No") %}
{%- elif a.category == 'application' %}
{%- set prev = "[TBD]" %}
{%- else %}
{%- set prev = "—" %}
{%- endif %}
| {{ a.name }} | {{ a.purpose or "" }} | {{ a.automation_surface or "" }} | {{ a.access_method or "" }} | {{ in_scope }} | {{ prev }} |
{%- endfor %}
{%- else %}
[TBD]
{%- endif %}
