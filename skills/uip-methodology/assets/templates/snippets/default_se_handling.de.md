{%- if default_se_handling %}
{%- for item in default_se_handling %}
- {{ item }}
{%- endfor %}
{%- else %}
- Den aktuellen Schritt bis zu `[DEFAULT: 3]`-mal wiederholen
- Falls ungelöst: Fehler protokollieren, Alarm an `[TBD — ops@company.com]` senden, sauber beenden
{%- endif %}
