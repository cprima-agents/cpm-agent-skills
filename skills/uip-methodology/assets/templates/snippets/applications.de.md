{%- if applications %}
| Name | Zweck | Automatisierungsschnittstelle | Zugriffsart | Im Umfang | Bereits automatisiert |
| --- | --- | --- | --- | --- | --- |
{%- for a in applications %}
{%- set in_scope = ('Ja' if a.in_scope else 'Nein') if a.in_scope is defined else '[TBD]' %}
{%- if a.previously_automated is defined %}
{%- set prev = 'entfällt' if a.previously_automated == 'not-applicable' else ('Ja' if a.previously_automated else 'Nein') %}
{%- elif a.category == 'application' %}
{%- set prev = '[TBD]' %}
{%- else %}
{%- set prev = '—' %}
{%- endif %}
| {{ a.name }} | {{ a.purpose or "" }} | {{ a.automation_surface or "" }} | {{ a.access_method or "" }} | {{ in_scope }} | {{ prev }} |
{%- endfor %}
{%- else %}
[TBD]
{%- endif %}
