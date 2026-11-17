{%- if default_be_handling %}
{%- for item in default_be_handling %}
- {{ item }}
{%- endfor %}
{%- else %}
- E-Mail an `[TBD — exceptions@company.com]` mit Screenshot senden
- Den Vorgang im Orchestrator als „Business Exception" protokollieren
- Mit dem nächsten Vorgang fortfahren
{%- endif %}
