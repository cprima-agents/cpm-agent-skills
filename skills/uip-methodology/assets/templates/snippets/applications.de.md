{%- if applications %}
| Name | Kategorie | Version | Automatisierungsschnittstelle | Zugriffsart | Im Umfang | Bereits automatisiert |
| --- | --- | --- | --- | --- | --- | --- |
{%- for a in applications %}
{%- set cat = 'Anwendung' if a.category == 'application' else 'Plattform' %}
{%- set in_scope = ('Ja' if a.in_scope else 'Nein') if a.in_scope is defined else '[TBD]' %}
{%- if a.previously_automated is defined %}
{%- set prev = 'entfällt' if a.previously_automated == 'not-applicable' else ('Ja' if a.previously_automated else 'Nein') %}
{%- elif a.category == 'application' %}
{%- set prev = '[TBD]' %}
{%- else %}
{%- set prev = '—' %}
{%- endif %}
| {{ a.name }} | {{ cat }} | {{ a.version or "" }} | {{ a.automation_surface or "" }} | {{ a.access_method or "" }} | {{ in_scope }} | {{ prev }} |
{%- endfor %}
{%- else %}
[TBD]
{%- endif %}
