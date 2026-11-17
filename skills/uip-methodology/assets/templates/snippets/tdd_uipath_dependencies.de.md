{%- set known = {
  'UiPath.System.Activities':              'Zentrale Workflow-Aktivitäten',
  'UiPath.System.Activities.Runtime':      'Zentrale Laufzeit (automatisch hinzugefügt)',
  'UiPath.CodedWorkflows':                 'Unterstützung für C#-Coded-Workflows (automatisch hinzugefügt)',
  'UiPath.UIAutomation.Activities':        'UI-Automatisierung — Desktop und Web',
  'UiPath.Excel.Activities':               'Excel lesen und schreiben',
  'UiPath.Mail.Activities':                'E-Mail über SMTP / IMAP / Exchange',
  'UiPath.MicrosoftOffice365.Activities':  'Microsoft 365 — Mail, Teams, SharePoint',
  'UiPath.PDF.Activities':                 'Textextraktion aus PDF',
  'UiPath.Testing.Activities':             'Framework für Testautomatisierung',
  'UiPath.WebAPI.Activities':              'Aufrufe von REST- und SOAP-Webdiensten',
  'UiPath.FTP.Activities':                 'Dateiübertragung per FTP / SFTP',
  'UiPath.Database.Activities':            'Datenbankanbindung (ADO.NET)',
  'UiPath.IntelligentOCR.Activities':      'Document Understanding — OCR-Pipeline',
  'UiPath.DocumentUnderstanding.ML.Activities': 'Document Understanding — ML-Extraktion',
} -%}
{%- if project and project.dependencies %}
| Paket | Version | Regel | Zweck |
| --- | --- | --- | --- |
{%- for name, version in project.dependencies.items() %}
{%- if name.startswith('UiPath.') %}
| `{{ name }}` | {{ version }} | {{ 'Strikt' if version.startswith('[') and version.endswith(']') else 'Niedrigste passende Version' }} | {{ known.get(name, '') }} |
{%- endif %}
{%- endfor %}
{%- else %}
| Paket | Version | Regel | Zweck |
| --- | --- | --- | --- |
| `UiPath.Excel.Activities` | [2.24.3] | Strikt | Excel lesen und schreiben |
| `UiPath.Mail.Activities` | [2.2.10] | Strikt | E-Mail über SMTP / IMAP / Exchange |
| `UiPath.MicrosoftOffice365.Activities` | [2.7.24] | Strikt | Microsoft 365 — Mail, Teams, SharePoint |
| `UiPath.System.Activities` | [24.10.4] | Strikt | Zentrale Workflow-Aktivitäten |
| `UiPath.Testing.Activities` | [24.10.4] | Strikt | Framework für Testautomatisierung |
| `UiPath.UIAutomation.Activities` | [25.10.12] | Strikt | UI-Automatisierung — Desktop und Web |
{%- endif %}
