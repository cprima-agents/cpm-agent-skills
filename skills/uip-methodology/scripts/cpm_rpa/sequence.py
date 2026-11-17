"""The to-be run as a sequence diagram: the robot, the systems and the clerk as vertical lanes, the steps in time order.

Built from the yaml files like every other diagram: the participants are the robot, the systems that the to-be steps
use (in the order of systems.yaml) and the clerk; the messages are the to-be tasks in reading order, grouped by the
seven pipeline stages; the handover is the escalation end state of process.yaml. A step of a system is an arrow from
the robot to that system; a step without a system is a note beside the robot.

File names: `sequence.<lang>.generated.mmd` and `.png`. The image is rendered with Mermaid (`mmdc`) and a browser
(Chrome or Edge); without them only the `.mmd` file is written and the caller gets a warning.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

_SCRIPTS = Path(__file__).resolve().parent.parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from yaml_graph import models_of, parent_of, reading_order  # noqa: E402

RED, YELLOW, INK = "#D40511", "#FFCC00", "#1A1A1A"
FONT = "Calibri"

# Display words of the picture. Values are (de, en).
_WORDS = {
    "robot": ("RPA-Roboter", "RPA robot"),
    "human": ("Mitarbeiter", "Clerk"),
    "handover": ("Übergabe", "Handover"),
}


def _t(value: Any, lang: str) -> str:
    """A text pair in one language, safe inside a Mermaid message (no semicolon, no hash)."""
    text = (value.get(lang) or value.get("en") or "") if isinstance(value, dict) else str(value)
    return text.replace(";", ",").replace("#", "").strip()


def build_sequence(process: dict[str, Any], systems: dict[str, Any], lang: str) -> str:
    """The Mermaid source of the sequence diagram in one language."""
    word = lambda key: _WORDS[key][0 if lang == "de" else 1]  # noqa: E731
    order = {sid: i for i, sid in enumerate(reading_order(process, "to-be"))}
    stages = sorted(
        (s for s in process["steps"] if s.get("stage") and parent_of(s, "to-be") is None and "to-be" in models_of(s)),
        key=lambda s: order.get(s["id"], 0),
    )
    groups: list[tuple[dict[str, Any], list[dict[str, Any]]]] = []
    for stage in stages:
        tasks = [
            s
            for s in process["steps"]
            if parent_of(s, "to-be") == stage["id"] and "to-be" in models_of(s) and s.get("type") == "task"
        ]
        tasks.sort(key=lambda s: order.get(s["id"], 0))
        if tasks:
            groups.append((stage, tasks))
    used = {s.get("system") for _stage, tasks in groups for s in tasks if s.get("system")}
    lanes = [s for s in systems.get("systems") or [] if s["id"] in used]  # only systems the robot touches
    alias = {s["id"]: f"S{i}" for i, s in enumerate(lanes)}
    first, last = (alias[lanes[0]["id"]], "H") if lanes else ("R", "H")

    lines = [
        "%%{init: {'theme':'base','themeVariables':{"
        f"'fontFamily':'{FONT}','fontSize':'15px','primaryColor':'#FFF9DB','primaryBorderColor':'{INK}','primaryTextColor':'{INK}',"
        f"'lineColor':'{RED}','actorBkg':'#FFF9DB','actorBorder':'{INK}','actorTextColor':'{INK}','signalColor':'{RED}',"
        f"'signalTextColor':'{INK}','noteBkgColor':'{YELLOW}','noteBorderColor':'{INK}','noteTextColor':'{INK}',"
        "'sequenceNumberColor':'#FFFFFF'}}}%%",
        "sequenceDiagram",
        "  autonumber",
        f"  participant R as {word('robot')}",
    ]
    lines += [f"  participant {alias[s['id']]} as {_t(s.get('label') or s['id'], lang)}" for s in lanes]
    lines.append(f"  participant H as {word('human')}")
    for n, (stage, tasks) in enumerate(groups):
        lines.append(f"  rect {'rgb(255,249,219)' if n % 2 == 0 else 'rgb(255,255,255)'}")
        lines.append(f"  Note over R,H: {n + 1} {_t(stage.get('label') or stage['id'], lang)}")
        for step in tasks:
            text = _t(step.get("label") or step["id"], lang)
            if step.get("system") in alias:
                lines.append(f"  R->>{alias[step['system']]}: {text}")
            else:
                lines.append(f"  Note right of R: {text}")
        lines.append("  end")
    ending = next(
        (t for t in process.get("terminal_states") or [] if t.get("type") == "escalation" and "to-be" in models_of(t)),
        None,
    )
    if ending:  # the handover: the robot gives the case to a clerk
        lines += ["  rect rgb(255,230,230)", f"  R-->>H: {_t(ending.get('label') or word('handover'), lang)}", "  end"]
    return "\n".join(lines) + "\n"


def find_mmdc() -> str | None:
    """The Mermaid command line program: $MMDC, then the PATH."""
    return os.environ.get("MMDC") or shutil.which("mmdc")


def find_browser() -> str | None:
    """A browser Mermaid can draw with: $PUPPETEER_EXECUTABLE_PATH, then Chrome or Edge in the usual places."""
    candidates = [
        os.environ.get("PUPPETEER_EXECUTABLE_PATH"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ]
    return next((c for c in candidates if c and Path(c).exists()), None)


def write_sequence(
    process: dict[str, Any], systems: dict[str, Any], out_dir: Path, langs: list[str], timeout: float = 180.0
) -> tuple[list[Path], list[str]]:
    """Write `sequence.<lang>.generated.mmd` and `.png` for every language. Returns the paths and the warnings."""
    written: list[Path] = []
    warnings: list[str] = []
    out_dir.mkdir(parents=True, exist_ok=True)
    mmdc, browser = find_mmdc(), find_browser()
    with tempfile.TemporaryDirectory() as tmp:
        config = Path(tmp) / "puppeteer.json"
        config.write_text(json.dumps({"executablePath": browser, "args": ["--no-sandbox", "--disable-gpu"]}), encoding="utf-8")
        for lang in langs:
            source = out_dir / f"sequence.{lang}.generated.mmd"
            source.write_text(build_sequence(process, systems, lang), encoding="utf-8", newline="\n")
            written.append(source)
            if not (mmdc and browser):
                warnings.append(f"no png for {source.name}: Mermaid (mmdc) or a browser (Chrome, Edge) was not found")
                continue
            image = source.with_suffix(".png")
            try:
                run = subprocess.run(
                    [mmdc, "-p", str(config), "-i", str(source), "-o", str(image), "-s", "2", "-b", "white"],
                    capture_output=True,
                    timeout=timeout,
                    check=False,
                )
            except (OSError, subprocess.TimeoutExpired) as error:
                warnings.append(f"no png for {source.name}: {error}")
                continue
            if run.returncode == 0 and image.exists():
                written.append(image)
            else:
                warnings.append(f"no png for {source.name}: {run.stderr.decode(errors='replace').strip()[:200]}")
    return written, warnings
