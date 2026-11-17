"""Write the decisions of a project into an Excel file: what has to be implemented, one row per rule.

Source: decisions.yaml (and, for the steps and the data a decision reads, process.yaml and data-model.yaml when given).
The file is generated: it is overwritten on every run, so edit the yaml and run again, not the Excel file.

Sheets:
  Rules      one row per rule: the reasons and the remark that select it, the measures, whether the business has
             decided it, whether the case goes to a clerk, the exception, the text for the audit trail, the notes
  Decisions  one row per decision: the question, where it is made, what it reads, how the rules match
  Actions    the measures by code, with their business text

German and English texts stand side by side, so the file can be read in both languages.

Usage:
    uv run --project <skill> <skill>/scripts/decisions_xlsx.py --decisions docs/solution-design/decisions.yaml \\
        [--process docs/solution-design/process.yaml] [--data-model docs/solution-design/data-model/data-model.yaml] \\
        [--output docs/solution-design/decisions.generated.xlsx]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from ruamel.yaml import YAML

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cpm_rpa.from_yaml import _field_of, _is_open_question  # noqa: E402

HEADER_FILL = PatternFill("solid", fgColor="FFCC00")
OPEN_FILL = PatternFill("solid", fgColor="FDE9E7")
DECIDED_FILL = PatternFill("solid", fgColor="E8F3E8")
WRAP = Alignment(wrap_text=True, vertical="top")


def load(path: Path | None) -> dict[str, Any]:
    return (YAML(typ="safe").load(path.read_text(encoding="utf-8")) or {}) if path else {}


def pair(value: Any, lang: str) -> str:
    """One language of a text pair; a plain value as it is; nothing as an empty cell."""
    if isinstance(value, dict):
        return str(value.get(lang) or "")
    return "" if value is None else str(value)


def joined(values: list[Any], lang: str, sep: str) -> str:
    return sep.join(pair(v, lang) for v in values or [])


def sheet(wb: Workbook, title: str, header: list[str], rows: list[list[Any]], widths: list[int]) -> Any:
    ws = wb.create_sheet(title)
    ws.append(header)
    for row in rows:
        ws.append(row)
    for cell in ws[1]:
        cell.font, cell.fill, cell.alignment = Font(bold=True), HEADER_FILL, Alignment(wrap_text=True, vertical="center")
    for column, width in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(column)].width = width
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = WRAP
    ws.freeze_panes = "B2"
    ws.auto_filter.ref = ws.dimensions
    return ws


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--decisions", type=Path, required=True, help="decisions.yaml")
    parser.add_argument("--process", type=Path, help="process.yaml: the steps that make or use a decision")
    parser.add_argument("--data-model", type=Path, help="data-model.yaml: the fields a decision reads")
    parser.add_argument("--output", type=Path, help="default: decisions.generated.xlsx next to decisions.yaml")
    args = parser.parse_args()

    decisions, process, model = load(args.decisions), load(args.process), load(args.data_model)
    actions = decisions.get("actions") or {}
    steps = process.get("steps") or []

    rules: list[list[Any]] = []
    overview: list[list[Any]] = []
    for d in decisions.get("decisions") or []:
        d_open = _is_open_question(d)
        for o in d.get("outcomes") or []:
            codes = o.get("actions") or []
            if "reasons" in o:  # a rule on the correction reasons: open when it names no measure
                is_open = not codes or _is_open_question(o)
            else:  # a plain outcome, for example yes or no
                is_open = d_open or _is_open_question(o)
            measures_de = " + ".join(pair(actions[c]["business_text"], "de") for c in codes if c in actions)
            measures_en = " + ".join(pair(actions[c]["business_text"], "en") for c in codes if c in actions)
            rules.append(
                [
                    d["id"],
                    pair(d.get("question"), "de"),
                    pair(d.get("question"), "en"),
                    o.get("id", ""),
                    joined(o.get("reasons") or [], "de", " + ") or pair(o.get("result"), "de"),
                    joined(o.get("reasons") or [], "en", " + ") or pair(o.get("result"), "en"),
                    pair(o.get("remark"), "de"),
                    pair(o.get("remark"), "en"),
                    ", ".join(codes),
                    measures_de or pair(o.get("action"), "de"),
                    measures_en or pair(o.get("action"), "en"),
                    "Offen / Open" if is_open else "Entschieden / Decided",
                    "Ja / Yes" if o.get("terminal") else "",
                    o.get("exception", ""),
                    pair(o.get("observation"), "de"),
                    pair(o.get("observation"), "en"),
                    pair(o.get("note"), "de"),
                    pair(o.get("note"), "en"),
                ]
            )
        made = [s.get("label") for s in steps if s.get("decision") == d["id"] and s.get("type") != "gateway"]
        used = [s.get("label") for s in steps if s.get("decision") == d["id"] and s.get("type") == "gateway"]
        reads = [_field_of(model, i["field"]) for i in d.get("inputs") or [] if i.get("field")]
        overview.append(
            [
                d["id"],
                pair(d.get("question"), "de"),
                pair(d.get("question"), "en"),
                joined(made, "de", "; "),
                joined(used, "de", "; "),
                "; ".join(f"{pair(r['name'], 'de')} ({pair(r['container'], 'de')})" if r["container"] else pair(r["name"], "de") for r in reads),
                pair(d.get("match"), "de"),
                pair(d.get("match"), "en"),
                pair(d.get("no_match"), "de"),
                pair(d.get("no_match"), "en"),
                "Offen / Open" if d_open else "Entschieden / Decided",
            ]
        )

    wb = Workbook()
    wb.remove(wb.active)
    ws = sheet(
        wb,
        "Rules",
        ["Decision", "Question (de)", "Question (en)", "Rule", "Reasons (de)", "Reasons (en)", "Remark (de)", "Remark (en)",
         "Action codes", "Measures (de)", "Measures (en)", "Status", "Handover to a clerk", "Exception",
         "Audit text (de)", "Audit text (en)", "Note (de)", "Note (en)"],
        rules,
        [12, 32, 32, 11, 40, 40, 30, 30, 12, 32, 32, 20, 12, 26, 40, 40, 36, 36],
    )
    for row in ws.iter_rows(min_row=2):
        row[11].fill = OPEN_FILL if str(row[11].value).startswith("Offen") else DECIDED_FILL
    ws = sheet(
        wb,
        "Decisions",
        ["Decision", "Question (de)", "Question (en)", "Made in step", "Branches at", "Reads", "How the rules match (de)",
         "How the rules match (en)", "If no rule matches (de)", "If no rule matches (en)", "Status"],
        overview,
        [12, 32, 32, 28, 28, 44, 48, 48, 48, 48, 20],
    )
    for row in ws.iter_rows(min_row=2):
        row[10].fill = OPEN_FILL if str(row[10].value).startswith("Offen") else DECIDED_FILL
    sheet(
        wb,
        "Actions",
        ["Code", "Text (de)", "Text (en)"],
        [[code, pair(a.get("business_text"), "de"), pair(a.get("business_text"), "en")] for code, a in actions.items()],
        [18, 48, 48],
    )

    out = args.output or args.decisions.with_name("decisions.generated.xlsx")
    wb.save(out)
    print(f"Written: {out}  ({len(rules)} rules, {len(overview)} decisions, {len(actions)} actions)")


if __name__ == "__main__":
    main()
