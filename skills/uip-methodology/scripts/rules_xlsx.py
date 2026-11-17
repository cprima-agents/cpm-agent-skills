"""Write the business rules of a project into an Excel file that a business expert answers: one language, plain words.

Source: rules.yaml (and, for the steps and the data a rule set reads, process.yaml and data-model.yaml when given).
The file is a worksheet for elicitation: every rule set and every rule is a row with the current proposal and empty
columns for the answer of the business. It is generated; edit the yaml and run again, never the proposal columns.

Sheets:
  Lesehilfe / Guide   how to read and fill in the file
  Regelwerke          one row per rule set: the question, where it is applied, the data, how the rules match, what
                      happens when no rule matches; to confirm or correct
  Regeln              one row per rule: the reasons and the remark that select it, what happens, the status; to confirm

Technical codes (action codes, exception ids, audit texts) are left out: the business does not need them.

Usage:
    uv run --project <skill> <skill>/scripts/rules_xlsx.py --rules docs/solution-design/rules.yaml \\
        [--lang de|en] [--process docs/solution-design/process.yaml] [--data-model docs/solution-design/data-model/data-model.yaml] \\
        [--output <file>]     default: rules.generated.xlsx in the folder rules/ next to rules.yaml if that
                              folder exists, else next to rules.yaml
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from ruamel.yaml import YAML

sys.path.insert(0, str(Path(__file__).resolve().parent))
import migrations  # noqa: E402
from cpm_rpa.from_yaml import _field_of, _is_open_question  # noqa: E402

HEADER_FILL = PatternFill("solid", fgColor="FFCC00")
ANSWER_FILL = PatternFill("solid", fgColor="FFF9DB")
OPEN_FILL = PatternFill("solid", fgColor="FDE9E7")
DECIDED_FILL = PatternFill("solid", fgColor="E8F3E8")
WRAP = Alignment(wrap_text=True, vertical="top")

# Words of the file, per language.
W = {
    "de": {
        "guide": "Lesehilfe",
        "rulesets": "Regelwerke",
        "rules": "Regeln",
        "decided": "Entschieden",
        "open": "Offen: bitte entscheiden",
        "undecided": "Noch nicht entschieden",
        "answers": ["Passt", "Passt nicht", "Klärung nötig"],
        "guide_lines": [
            "Diese Datei hält fest, wonach der Roboter einen Fall bearbeitet. Bitte prüfen Sie jede Zeile.",
            "",
            "Blatt „Regelwerke“: Welche Regelwerke der Roboter anwendet, wo im Ablauf, mit welchen Daten, und was geschieht, wenn keine Regel passt.",
            "Blatt „Regeln“: Jede Zeile ist eine Regel. Sie gilt, wenn die Korrekturgründe und die Bemerkung eines Falls genau zu der Zeile passen.",
            "",
            "Status: „Entschieden“ heißt, die Regel ist abgestimmt. „Offen“ heißt, es ist noch keine Maßnahme festgelegt. Bitte entscheiden Sie.",
            "",
            "Bitte ausfüllen (gelbe Spalten): Antwort (Passt / Passt nicht / Klärung nötig), Richtig wäre, Kommentar.",
            "Ändern Sie bitte nicht die Spalten mit dem Vorschlag. Halten Sie Korrekturen in „Richtig wäre“ fest.",
        ],
        "d_head": ["Regelwerk", "Frage", "Wo im Ablauf", "Welche Daten", "So gelten die Regeln", "Wenn keine Regel gilt",
                   "Mögliche Ergebnisse", "Status", "Antwort", "Richtig wäre", "Kommentar"],
        "r_head": ["Regel", "Korrekturgründe", "Bemerkung", "Was geschieht", "Status", "Antwort", "Richtig wäre", "Kommentar"],
    },
    "en": {
        "guide": "Guide",
        "rulesets": "Rule sets",
        "rules": "Rules",
        "decided": "Decided",
        "open": "Open: please decide",
        "undecided": "Not decided yet",
        "answers": ["Correct", "Not correct", "Needs clarification"],
        "guide_lines": [
            "This file records how the robot handles a case. Please check every row.",
            "",
            "Sheet “Rule sets”: which rule sets the robot applies, where in the flow, with which data, and what happens when no rule matches.",
            "Sheet “Rules”: every row is a rule. It applies when the correction reasons and the remark of a case match the row exactly.",
            "",
            "Status: “Decided” means the rule is agreed. “Open” means no measure is set yet. Please decide.",
            "",
            "Please fill in (yellow columns): Answer (Correct / Not correct / Needs clarification), It should be, Comment.",
            "Please do not change the columns with the proposal. Write corrections in “It should be”.",
        ],
        "d_head": ["Rule set", "Question", "Where in the flow", "Which data", "How the rules match", "If no rule matches",
                   "Possible results", "Status", "Answer", "It should be", "Comment"],
        "r_head": ["Rule", "Correction reasons", "Remark", "What happens", "Status", "Answer", "It should be", "Comment"],
    },
}


def load(path: Path | None) -> dict[str, Any]:
    return (YAML(typ="safe").load(path.read_text(encoding="utf-8")) or {}) if path else {}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--rules", type=Path, required=True, help="rules.yaml")
    parser.add_argument("--lang", choices=("de", "en"), default="de", help="the one language of the file (default: de)")
    parser.add_argument("--process", type=Path, help="process.yaml: the steps that apply a rule set")
    parser.add_argument("--data-model", type=Path, help="data-model.yaml: the fields a rule set reads")
    parser.add_argument("--output", type=Path, help="default: see the top of this file")
    args = parser.parse_args()
    lang, w = args.lang, W[args.lang]

    def t(value: Any) -> str:
        if isinstance(value, dict):
            return str(value.get(lang) or value.get("en") or value.get("de") or "")
        return "" if value is None else str(value)

    rules_file, process, model = load(args.rules), load(args.process), load(args.data_model)
    if str(rules_file.get("version")) != migrations.current("rules"):
        sys.exit(f"ERROR: {args.rules}: version {rules_file.get('version')}, current {migrations.current('rules')}: run `cli.py migrate`.")
    actions = rules_file.get("actions") or {}
    steps = process.get("steps") or []

    ruleset_rows: list[list[Any]] = []
    rule_rows: list[list[Any]] = []
    for d in rules_file.get("rulesets") or []:
        d_open = _is_open_question(d)
        plain = []  # rules without reasons, for example yes and no: shown as possible results of the rule set
        for o in d.get("rules") or []:
            codes = o.get("actions") or []
            if "reasons" in o or o.get("id"):  # a rule: it has reasons, or an id of its own (R-ELSE: no rule matches)
                is_open = (not codes and not o.get("scope_reason") and "reasons" in o) or _is_open_question(o)
                measure = " + ".join(t(actions[c]["business_text"]) for c in codes if c in actions)
                reasons = "\n".join(t(r) for r in o.get("reasons") or []) or t(o.get("result"))
                rule_rows.append(
                    [
                        o.get("id", ""),
                        reasons,
                        t(o.get("remark")),
                        measure or (t(o.get("action")) if o.get("terminal") else w["undecided"]),
                        w["open"] if is_open else w["decided"],
                    ]
                )
            else:
                plain.append(f"{t(o.get('result'))}: {t(o.get('action'))}")
        made = [t(s.get("label")) for s in steps if s.get("ruleset") == d["id"] and s.get("type") != "gateway"]
        used = [t(s.get("label")) for s in steps if s.get("ruleset") == d["id"] and s.get("type") == "gateway"]
        reads = [_field_of(model, i["field"]) for i in d.get("inputs") or [] if i.get("field")]
        where = "\n".join(
            part for part in ("; ".join(made), ("→ " + "; ".join(dict.fromkeys(used))) if used else "") if part
        )
        ruleset_rows.append(
            [
                d["id"],
                t(d.get("question")),
                where,
                "\n".join(f"{t(r['name'])}" + (f" ({t(r['container'])})" if r["container"] else "") for r in reads),
                t(d.get("match")),
                t(d.get("no_match")),
                "\n".join(plain),
                w["open"] if d_open else w["decided"],
            ]
        )

    wb = Workbook()
    guide = wb.active
    guide.title = w["guide"]
    for line in w["guide_lines"]:
        guide.append([line])
    guide.column_dimensions["A"].width = 130
    for row in guide.iter_rows():
        row[0].alignment = WRAP

    def table(title: str, header: list[str], rows: list[list[Any]], widths: list[int], status_col: int, answers_from: int) -> None:
        ws = wb.create_sheet(title)
        ws.append(header)
        answer_cols = range(answers_from, len(header))  # the columns that the business fills in
        for row in rows:
            ws.append(row + [""] * (len(header) - len(row)))
        for cell in ws[1]:
            cell.font, cell.alignment = Font(bold=True), Alignment(wrap_text=True, vertical="center")
            cell.fill = ANSWER_FILL if cell.column - 1 in answer_cols else HEADER_FILL
        for column, width in enumerate(widths, start=1):
            ws.column_dimensions[get_column_letter(column)].width = width
        for row in ws.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = WRAP
            row[status_col].fill = OPEN_FILL if str(row[status_col].value).startswith(w["open"][:4]) else DECIDED_FILL
            for i in answer_cols:
                row[i].fill = ANSWER_FILL
        if len(rows):
            validation = DataValidation(type="list", formula1='"' + ",".join(w["answers"]) + '"', allow_blank=True)
            ws.add_data_validation(validation)
            validation.add(f"{get_column_letter(answers_from + 1)}2:{get_column_letter(answers_from + 1)}{len(rows) + 1}")
        ws.freeze_panes = "B2"
        ws.auto_filter.ref = ws.dimensions

    table(w["rulesets"], w["d_head"], ruleset_rows, [14, 34, 36, 40, 50, 50, 40, 22, 16, 36, 36], 7, 8)
    table(w["rules"], w["r_head"], rule_rows, [10, 46, 34, 40, 22, 16, 36, 36], 4, 5)

    folder = args.rules.with_suffix("")  # a folder named like the yaml (rules/) holds the output, when it exists
    out = args.output or (folder if folder.is_dir() else args.rules.parent) / "rules.generated.xlsx"
    wb.save(out)
    print(f"Written: {out}  ({len(rule_rows)} rules, {len(ruleset_rows)} rule sets, language {lang})")


if __name__ == "__main__":
    main()
