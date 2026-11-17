"""The big picture of a process: the robot, the systems it talks to, the data it reads and the handover to a person.

One Graphviz diagram per language, built from the same yaml files as everything else: the systems of systems.yaml
(role, scope, description), the direction of each system from the pipeline stages of process.yaml (read or write),
the data each system delivers from data-model.yaml, and what the robot does in a system from the steps of the
execute and complete stages. It is meant as the teaser image on the first page of the PDD.

File names: `overview.<lang>.generated.dot` and `.png`. The generator owns these files, like the other diagrams.
Graphviz (`dot`) is needed for the image; without it only the `.dot` file is written and the caller gets a warning.
"""

from __future__ import annotations

import html
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

_SCRIPTS = Path(__file__).resolve().parent.parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from cpm_rpa.from_yaml import _directions  # noqa: E402
from yaml_graph import models_of, stage_of  # noqa: E402

RED, YELLOW, INK, SOFT = "#D40511", "#FFCC00", "#1A1A1A", "#FFF9DB"
FONT = "Calibri"

# Display words of the picture. Values are (de, en).
_WORDS = {
    "robot": ("RPA-Roboter", "RPA robot"),
    "human": ("Mitarbeiter", "Clerk"),
    "handover": ("Übergabe an einen Mitarbeiter", "Handover to a clerk"),
    "data": ("Vorgangsdaten", "Domain data"),
    "trigger": ("löst den Fall aus", "reports the case"),
}


def _t(value: Any, lang: str) -> str:
    """A text pair in one language, escaped for a Graphviz HTML label."""
    text = value.get(lang) or value.get("en") or "" if isinstance(value, dict) else str(value)
    return html.escape(text)


def _word(key: str, lang: str) -> str:
    return html.escape(_WORDS[key][0 if lang == "de" else 1])


def _delivered(model: dict[str, Any], system_id: str, lang: str) -> list[str]:
    """The data containers a system delivers: the containers of the data-model entities that come from it."""
    found: list[str] = []
    for entity in model.get("entities") or []:
        source = entity.get("source") or {}
        if source.get("application") == system_id and source.get("container"):
            text = _t(source["container"], lang)
            if text not in found:
                found.append(text)
    return found


def _done_in(process: dict[str, Any], system_id: str, lang: str) -> list[str]:
    """What the robot does in a system: the to-be tasks of the execute and complete stages that use it."""
    return [
        _t(s["label"], lang)
        for s in process["steps"]
        if s.get("system") == system_id
        and s.get("type") == "task"
        and s.get("parent")
        and "to-be" in models_of(s)
        and stage_of(process, s, "to-be") in ("execute", "complete")
    ]


def _card(title: str, lines: list[str]) -> str:
    body = "".join(f'<TR><TD ALIGN="LEFT"><FONT POINT-SIZE="10.5" COLOR="#333333">· {line}</FONT></TD></TR>' for line in lines)
    return (
        '<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="3">'
        f'<TR><TD ALIGN="LEFT"><FONT POINT-SIZE="17"><B>{title}</B></FONT></TD></TR>{body}</TABLE>>'
    )


def build_dot(process: dict[str, Any], systems: dict[str, Any], model: dict[str, Any], lang: str) -> str:
    """The Graphviz source of the overview in one language."""
    directions = _directions(process)
    out = [
        "digraph overview {",
        f'  graph [charset="UTF-8", rankdir=LR, bgcolor="white", pad=0.3, nodesep=0.5, ranksep=1.6, fontname="{FONT}"];',
        f'  node [fontname="{FONT}", fontsize=12, shape=box, style="rounded,filled", fillcolor="#FFFFFF", color="{INK}", penwidth=1.8, margin="0.22,0.16"];',
        f'  edge [fontname="{FONT}", fontsize=10.5, color="{RED}", penwidth=2.2, arrowsize=0.9, fontcolor="#333333"];',
        f'  robot [style="rounded,filled", fillcolor="{YELLOW}", penwidth=3, margin="0.5,0.4", '
        f'label=<<FONT POINT-SIZE="22"><B>{_word("robot", lang)}</B></FONT><BR/><FONT POINT-SIZE="11">{_word("data", lang)}</FONT>>];',
        f'  human [style="rounded,filled,dashed", color="{RED}", penwidth=2.4, '
        f'label=<<FONT POINT-SIZE="17"><B>{_word("human", lang)}</B></FONT>>];',
    ]
    for system in systems.get("systems") or []:
        sid, label = system["id"], html.escape(system.get("label") or system["id"])
        if system.get("role") == "orchestration":  # the platform: supports the robot, no data flow of its own
            out.append(f'  {sid} [label={_card(label, [_t(system.get("description") or "", lang)])}, fillcolor="#F2F2F2"];')
            out.append(f'  {sid} -> robot [style=dashed, color="#888888"];')
        elif system.get("in_scope") is False:  # outside the automation: where the case starts
            out.append(f'  {sid} [label={_card(label, [_word("trigger", lang)])}, style="rounded,dashed", color="#888888"];')
        else:
            lines = _delivered(model, sid, lang) or [_t(system.get("description") or "", lang)]
            out.append(f'  {sid} [label={_card(label, lines)}, fillcolor="{SOFT}"];')
            direction = directions.get(sid)
            if direction in ("read", "both"):
                out.append(f"  {sid} -> robot;")
            if direction in ("write", "both"):
                done = "<BR/>".join(_done_in(process, sid, lang)[:3])
                out.append(f"  robot -> {sid}" + (f" [label=<{done}>];" if done else ";"))
    out.append(
        f'  robot -> human [style=dashed, color="{RED}", penwidth=2.6, label=<<B>{_word("handover", lang)}</B>>];'
    )
    out.append("}")
    return "\n".join(out) + "\n"


def find_dot() -> str | None:
    """The Graphviz `dot` program: $GRAPHVIZ_DOT, then the PATH, then the usual install places."""
    candidates = [
        os.environ.get("GRAPHVIZ_DOT"),
        shutil.which("dot"),
        r"C:\Program Files\Graphviz\bin\dot.exe",
        "/usr/bin/dot",
        "/opt/homebrew/bin/dot",
    ]
    return next((c for c in candidates if c and Path(c).exists()), None)


def write_overview(
    process: dict[str, Any],
    systems: dict[str, Any],
    model: dict[str, Any],
    out_dir: Path,
    langs: list[str],
) -> tuple[list[Path], list[str]]:
    """Write `overview.<lang>.generated.dot` and `.png` for every language. Returns the paths and the warnings."""
    written: list[Path] = []
    warnings: list[str] = []
    dot = find_dot()
    out_dir.mkdir(parents=True, exist_ok=True)
    for lang in langs:
        source = out_dir / f"overview.{lang}.generated.dot"
        source.write_text(build_dot(process, systems, model, lang), encoding="utf-8", newline="\n")
        written.append(source)
        if not dot:
            warnings.append(f"no png for {source.name}: Graphviz (dot) was not found")
            continue
        image = source.with_suffix(".png")
        run = subprocess.run([dot, "-Tpng", "-Gdpi=150", str(source), "-o", str(image)], capture_output=True, check=False)
        if run.returncode == 0 and image.exists():
            written.append(image)
        else:
            warnings.append(f"no png for {source.name}: {run.stderr.decode(errors='replace').strip()[:200]}")
    return written, warnings
