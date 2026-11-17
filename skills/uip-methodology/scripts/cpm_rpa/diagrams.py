"""Render the diagrams of a process yaml as draw.io and Mermaid files.

One neutral diagram (`Diagram`: nodes and edges, texts already in one language) is built per diagram and language
from process.yaml. Both renderers read that same object, so the draw.io and the Mermaid file always show the same
steps, the same numbers and the same links.

Steps that have a `lane` are drawn as a BPMN pool with one swimlane per lane; a diagram can open selected activities
inline (`expand`), as BPMN draws an expanded sub-process, and shows the rest as boxes or containers.

File names: `<diagram-id>.<lang>.generated.drawio` and `<diagram-id>.<lang>.generated.mmd`. The generator owns these
files and rewrites them without any volatile content, so a diff shows real changes only. A working copy is the same
name without `.generated`; the generator never touches it.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_SCRIPTS = Path(__file__).resolve().parent.parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from cpm_rpa.renderer import resolve_text  # noqa: E402
from yaml_graph import MODELS, diagram_view, models_of, number  # noqa: E402

NOTICE = "Generated from process.yaml. Do not edit; copy the file (drop '.generated') and work on the copy."

# ── the neutral diagram ───────────────────────────────────────────────────


@dataclass(frozen=True)
class Node:
    id: str
    label: str
    kind: str  # start | end | event | task | gateway
    gateway: str | None = None  # exclusive | inclusive | parallel
    parent: str | None = None
    lane: str | None = None  # top-level nodes only
    origin: str = "both"  # both | as-is | to-be; only a comparison diagram tells them apart
    band: str | None = None  # the expanded step it came from, when the diagram draws those as bands


@dataclass(frozen=True)
class Edge:
    src: str
    dst: str
    label: str = ""
    loop: bool = False


@dataclass
class Diagram:
    id: str
    title: str
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)
    lanes: list[tuple[str, str]] = field(default_factory=list)  # (id, label); empty = no swimlanes
    comparison: bool = False
    bands: list[tuple[str, str]] = field(default_factory=list)  # (id, label) of the expanded steps drawn as bands

    def children(self) -> dict[str | None, list[Node]]:
        out: dict[str | None, list[Node]] = defaultdict(list)
        for n in self.nodes:
            out[n.parent].append(n)
        return out


_KIND = {"start_event": "start", "end_event": "end", "event": "event", "gateway": "gateway"}


def build_diagram(process: dict[str, Any], diagram: dict[str, Any], lang: str) -> Diagram:
    """The graph a diagram shows, with its texts in one language.

    Tasks carry their derived number (1, 2, 6.1) when the diagram shows a single model; a comparison of both
    models has no number, because the two models number their steps differently.
    """
    view = diagram_view(process, diagram)
    models = list(diagram.get("models") or MODELS)
    numbers = number(process, models[0]) if len(models) == 1 else {}
    comparison = len(models) > 1
    with_bands = bool(diagram.get("bands"))
    named = {s["id"]: s for s in process["steps"]}
    bands: list[tuple[str, str]] = []
    nodes = []
    for s in view["steps"]:
        text = str(resolve_text(s.get("label"), lang) or s["id"])
        own = models_of(s)
        band = s.get("band") if with_bands else None
        if band and band not in [b for b, _ in bands]:
            title = str(resolve_text(named[band].get("label"), lang) or band)
            bands.append((band, f"{numbers[band]} {title}" if band in numbers else title))
        nodes.append(
            Node(
                id=s["id"],
                label=f"{numbers[s['id']]} {text}" if s["id"] in numbers else text,
                kind=_KIND.get(s.get("type"), "task"),
                gateway=s.get("kind") if s.get("type") == "gateway" else None,
                parent=s.get("parent"),
                lane=s.get("lane") if s.get("parent") is None else None,
                origin=("both" if len(own) > 1 else own[0]) if comparison else "both",
                band=band,
            )
        )
    edges = [
        Edge(
            e["from"],
            e["to"],
            str(resolve_text(e.get("condition"), lang) or ""),
            loop="loop" in (e.get("tags") or []),
        )
        for e in view["edges"]
    ]
    top = [n for n in nodes if n.parent is None]
    lanes: list[tuple[str, str]] = []
    if top and all(n.lane for n in top):  # swimlanes only when every top-level step has a lane
        lanes = [(x["id"], x.get("label") or x["id"]) for x in process.get("lanes") or [] if any(n.lane == x["id"] for n in top)]
    return Diagram(diagram["id"], str(resolve_text(diagram.get("title"), lang)), nodes, edges, lanes, comparison, bands)


# ── Mermaid ───────────────────────────────────────────────────────────────

_MERMAID_CLASS = {
    "as-is": ("asis", "fill:#f8cecc,stroke:#b85450,color:#000"),
    "to-be": ("tobe", "fill:#d5e8d4,stroke:#82b366,color:#000"),
}


def _q(text: str) -> str:
    return text.replace('"', "#quot;")


def to_mermaid(d: Diagram) -> str:
    kids = d.children()
    lines = ["---", f'title: "{_q(d.title)}"', "---", f"%% {NOTICE}", "flowchart LR"]

    def emit(parent: str | None, nodes: list[Node], depth: int) -> None:
        pad = "  " * depth
        for n in nodes:
            text = _q(n.label)
            if kids[n.id]:
                lines.extend([f'{pad}subgraph {n.id}["{text}"]', f"{pad}  direction LR"])
                emit(n.id, kids[n.id], depth + 1)
                lines.append(f"{pad}end")
            elif n.kind == "gateway":
                lines.append(f'{pad}{n.id}{{"{text}"}}')
            elif n.kind in ("start", "end", "event"):
                lines.append(f'{pad}{n.id}(["{text}"])')
            else:
                lines.append(f'{pad}{n.id}["{text}"]')

    if d.lanes:  # Mermaid has no swimlanes; every lane becomes a group
        for lane_id, label in d.lanes:
            lines.extend([f'  subgraph {lane_id}["{_q(label)}"]', "    direction LR"])
            emit(None, [n for n in kids[None] if n.lane == lane_id], 2)
            lines.append("  end")
    else:
        emit(None, kids[None], 1)
    for e in d.edges:
        arrow = "-.->" if e.loop else "-->"
        lines.append(f'  {e.src} {arrow}|"{_q(e.label)}"| {e.dst}' if e.label else f"  {e.src} {arrow} {e.dst}")
    if d.comparison:
        for origin, (cls, style) in _MERMAID_CLASS.items():
            lines.append(f"  classDef {cls} {style}")
            members = [n.id for n in d.nodes if n.origin == origin]
            if members:
                lines.append(f"  class {','.join(members)} {cls}")
    return "\n".join(lines) + "\n"


# ── draw.io: layout ───────────────────────────────────────────────────────

TASK, GATEWAY, EVENT, EVENT_BOX = (160, 60), (50, 50), (40, 40), (140, 76)
GAP_X, GAP_Y, PAD, HEADER, TITLE_H = 60, 30, 20, 30, 50
POOL_HEADER, LANE_HEADER, LANE_PAD, LANE_MIN = 30, 20, 25, 120
BAND_H, BAND_GAP = 30, 4  # the title strip of a band above the pool; the space between two bands

Box = tuple[int, int, int, int]  # x, y, width, height


@dataclass
class Layout:
    boxes: dict[str, Box] = field(default_factory=dict)  # relative to the parent container, lane or page
    columns: dict[str, int] = field(default_factory=dict)  # column of every node within its level
    lane_boxes: dict[str, Box] = field(default_factory=dict)  # inside the pool
    pool: tuple[int, int] = (0, 0)  # width, height
    band_spans: dict[str, tuple[int, int]] = field(default_factory=dict)  # band id -> x and width inside the pool


def _base(n: Node) -> tuple[int, int]:
    return {"gateway": GATEWAY, "task": TASK}.get(n.kind, EVENT_BOX)


def _columns(d: Diagram, nodes: list[Node]) -> dict[str, int]:
    """The column of every node: its longest path from the entry, over the forward edges of the level."""
    ids = {n.id for n in nodes}
    column = {i: 0 for i in ids}
    links = [e for e in d.edges if e.src in ids and e.dst in ids and not e.loop]
    for _ in range(len(ids)):
        moved = False
        for e in links:
            if column[e.dst] < column[e.src] + 1:
                column[e.dst] = column[e.src] + 1
                moved = True
        if not moved:
            break
    return column


def layout(d: Diagram) -> Layout:
    """Where every node goes, left to right.

    A step sits in the column of its longest path from the entry. Without lanes, the steps of one column are stacked
    and centred. With lanes, the steps of one column and lane are stacked and centred in their lane; the lane is as
    tall as its tallest stack. A task with sub-steps becomes a container around the layout of its sub-steps.
    """
    kids = d.children()
    out = Layout()

    def sizes_of(nodes: list[Node]) -> dict[str, tuple[int, int]]:
        sizes: dict[str, tuple[int, int]] = {}
        for n in nodes:
            if kids[n.id]:
                w, h = place(n.id)
                sizes[n.id] = (w + 2 * PAD, h + HEADER + 2 * PAD)
            else:
                sizes[n.id] = _base(n)
        return sizes

    def place(parent: str | None) -> tuple[int, int]:
        nodes = kids[parent]
        sizes = sizes_of(nodes)
        column = _columns(d, nodes)
        out.columns.update(column)
        cols = [[n.id for n in nodes if column[n.id] == c] for c in range(max(column.values(), default=-1) + 1)]
        col_w = [max(sizes[i][0] for i in col) for col in cols]
        col_h = [sum(sizes[i][1] for i in col) + GAP_Y * (len(col) - 1) for col in cols]
        height = max(col_h, default=0)
        x = 0
        for col, cw, ch in zip(cols, col_w, col_h):
            y = (height - ch) // 2
            for i in col:
                w, h = sizes[i]
                out.boxes[i] = (x + (cw - w) // 2, y, w, h)
                y += h + GAP_Y
            x += cw + GAP_X
        return sum(col_w) + GAP_X * max(len(cols) - 1, 0), height

    if not d.lanes:
        place(None)
        return out

    top = kids[None]
    sizes = sizes_of(top)
    column = _columns(d, top)
    out.columns.update(column)
    ncols = max(column.values(), default=-1) + 1
    col_w = [max((sizes[n.id][0] for n in top if column[n.id] == c), default=0) for c in range(ncols)]
    col_x = [LANE_HEADER + PAD + sum(col_w[:c]) + GAP_X * c for c in range(ncols)]
    stack: dict[tuple[str, int], list[Node]] = defaultdict(list)
    for n in top:
        stack[(n.lane or "", column[n.id])].append(n)

    def stack_h(nodes: list[Node]) -> int:
        return sum(sizes[n.id][1] for n in nodes) + GAP_Y * (len(nodes) - 1)

    pool_w = POOL_HEADER + LANE_HEADER + 2 * PAD + sum(col_w) + GAP_X * max(ncols - 1, 0)
    y_lane = 0
    for lane_id, _label in d.lanes:
        lane_h = max(LANE_MIN, max((stack_h(v) for (lane, _c), v in stack.items() if lane == lane_id), default=0) + 2 * LANE_PAD)
        out.lane_boxes[lane_id] = (POOL_HEADER, y_lane, pool_w - POOL_HEADER, lane_h)
        for c in range(ncols):
            nodes = stack.get((lane_id, c), [])
            y = (lane_h - stack_h(nodes)) // 2 if nodes else 0
            for n in nodes:
                w, h = sizes[n.id]
                out.boxes[n.id] = (col_x[c] + (col_w[c] - w) // 2, y, w, h)
                y += h + GAP_Y
        y_lane += lane_h
    out.pool = (pool_w, y_lane)
    for band_id, _label in d.bands:  # a band covers the columns of its steps, over all lanes
        cols = [column[n.id] for n in top if n.band == band_id]
        if cols:
            first, last = min(cols), max(cols)
            x = POOL_HEADER + col_x[first] - GAP_X // 2 + BAND_GAP
            out.band_spans[band_id] = (x, col_x[last] + col_w[last] - col_x[first] + GAP_X - 2 * BAND_GAP)
    return out


# ── draw.io: cells ────────────────────────────────────────────────────────

_STYLE_TASK = "shape=mxgraph.bpmn.task;whiteSpace=wrap;rectStyle=rounded;size=10;html=1;container=0;expand=0;collapsible=0;taskMarker=abstract;"
_STYLE_CONTAINER = "swimlane;html=1;startSize=30;container=1;collapsible=1;fontStyle=0;dashed=1;dashPattern=8 4;"
_STYLE_POOL = "swimlane;html=1;horizontal=0;startSize=30;collapsible=0;fontStyle=0;whiteSpace=wrap;"
_STYLE_LANE = "swimlane;html=1;startSize=20;horizontal=0;container=0;fontStyle=0;collapsible=0;"
_STYLE_GATEWAY = "shape=mxgraph.bpmn.gateway2;html=1;perimeter=rhombusPerimeter;outlineConnect=0;outline=none;symbol=none;gwType={kind};"
_STYLE_EVENT = "shape=mxgraph.bpmn.event;html=1;perimeter=ellipsePerimeter;outlineConnect=0;aspect=fixed;outline={outline};symbol={symbol};"
_STYLE_LABEL = "text;html=1;align=center;verticalAlign=top;whiteSpace=wrap;rounded=0;labelBackgroundColor=#ffffff;"
_STYLE_EDGE = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=block;endFill=1;"
_STYLE_TITLE = "text;html=1;align=left;verticalAlign=middle;whiteSpace=wrap;fontSize=16;fontStyle=1;"
_STYLE_BAND = "rounded=0;whiteSpace=wrap;html=1;fillColor=none;dashed=1;dashPattern=8 4;strokeColor=#666666;verticalAlign=top;fontStyle=1;pointerEvents=0;"
_EVENT_LOOK = {"start": ("standard", "general"), "end": ("end", "terminate2"), "event": ("catching", "general")}
_FILL = {"as-is": "fillColor=#f8cecc;strokeColor=#b85450;", "to-be": "fillColor=#d5e8d4;strokeColor=#82b366;"}

def _port(side: str, kind: str) -> str:
    """Exit or entry of an edge on one side of a shape."""
    x, y = {"bottom": (0.5, 1), "top": (0.5, 0), "left": (0, 0.5), "right": (1, 0.5)}[side]
    return f"{kind}X={x};{kind}Y={y};{kind}Dx=0;{kind}Dy=0;"


def _edge_ports(d: Diagram, e: Edge, columns: dict[str, int]) -> str:
    """Where an edge leaves and enters its shapes, so it runs between lanes and under the steps it skips."""
    by_id = {n.id: n for n in d.nodes}
    src, dst = by_id[e.src], by_id[e.dst]
    if src.parent != dst.parent:
        return ""
    gap = columns[e.dst] - columns[e.src]
    if d.lanes and src.parent is None and src.lane != dst.lane:
        order = [lane for lane, _ in d.lanes]
        below = order.index(dst.lane) > order.index(src.lane)
        if gap > 0:
            return _port("bottom" if below else "top", "exit") + _port("left", "entry")
        return _port("bottom" if below else "top", "exit") + _port("top" if below else "bottom", "entry")
    if gap > 1:
        return _port("bottom", "exit") + _port("bottom", "entry")
    if gap == 1:  # the next column: leave at the right and enter at the left, so branches do not cross
        return _port("right", "exit") + _port("left", "entry")
    return ""


def _cell(root: ET.Element, cid: str, value: str, style: str, parent: str, box: Box) -> None:
    c = ET.SubElement(root, "mxCell", id=cid, value=value, style=style, vertex="1", parent=parent)
    x, y, w, h = box
    ET.SubElement(c, "mxGeometry", x=str(x), y=str(y), width=str(w), height=str(h)).set("as", "geometry")


def to_drawio(d: Diagram) -> str:
    kids = d.children()
    lay = layout(d)
    root = ET.Element("root")
    ET.SubElement(root, "mxCell", id="0")
    ET.SubElement(root, "mxCell", id="1", parent="0")
    _cell(root, "diagram-title", d.title, _STYLE_TITLE, "1", (0, 0, 700, 30))

    if d.lanes:
        pool_w, pool_h = lay.pool
        pool_y = TITLE_H + (BAND_H if lay.band_spans else 0)
        _cell(root, "pool", "", _STYLE_POOL, "1", (40, pool_y, pool_w, pool_h))
        for lane_id, label in d.lanes:
            _cell(root, lane_id, label, _STYLE_LANE, "pool", lay.lane_boxes[lane_id])
        for band_id, label in d.bands:  # a band runs over all lanes, with its title above the pool
            if band_id in lay.band_spans:
                x, w = lay.band_spans[band_id]
                _cell(root, f"band-{band_id}", label, _STYLE_BAND, "1", (40 + x, TITLE_H, w, BAND_H + pool_h))

    ports = {(e.src, e.dst): _edge_ports(d, e, lay.columns) for e in d.edges}
    # steps with an edge on their bottom side: a gateway's name goes above it there, so the edge does not cross the name
    low = {e.src for e in d.edges if "exitX=0.5;exitY=1" in ports[(e.src, e.dst)]}
    low |= {e.dst for e in d.edges if "entryX=0.5;entryY=1" in ports[(e.src, e.dst)]}

    def emit(parent: str | None) -> None:
        for n in kids[parent]:
            x, y, w, h = lay.boxes[n.id]
            if parent is not None:
                owner, (x, y) = parent, (x + PAD, y + HEADER + PAD)
            elif d.lanes:
                owner = n.lane  # relative to the lane
            else:
                owner, y = "1", y + TITLE_H
            fill = _FILL.get(n.origin, "")
            if kids[n.id]:
                _cell(root, n.id, n.label, _STYLE_CONTAINER + fill, owner, (x, y, w, h))
                emit(n.id)
            elif n.kind == "gateway":
                _cell(root, n.id, "", _STYLE_GATEWAY.format(kind=n.gateway or "exclusive") + fill, owner, (x, y, w, h))
                if n.id in low:
                    _cell(root, f"{n.id}-label", n.label, _STYLE_LABEL + "verticalAlign=bottom;", owner, (x + w // 2 - 70, y - 36, 140, 34))
                else:
                    _cell(root, f"{n.id}-label", n.label, _STYLE_LABEL, owner, (x + w // 2 - 70, y + h + 2, 140, 34))
            elif n.kind in _EVENT_LOOK:
                outline, symbol = _EVENT_LOOK[n.kind]
                _cell(root, n.id, "", _STYLE_EVENT.format(outline=outline, symbol=symbol) + fill, owner, (x + (w - EVENT[0]) // 2, y, *EVENT))
                _cell(root, f"{n.id}-label", n.label, _STYLE_LABEL, owner, (x, y + EVENT[1] + 2, w, 34))
            else:
                _cell(root, n.id, n.label, _STYLE_TASK + fill, owner, (x, y, w, h))

    emit(None)
    owner_of = {n.id: n.parent or "1" for n in d.nodes}
    for e in d.edges:
        style = _STYLE_EDGE + ("dashed=1;" if e.loop else "") + ports[(e.src, e.dst)]
        c = ET.SubElement(
            root, "mxCell", id=f"edge-{e.src}-{e.dst}", value=e.label, style=style, edge="1",
            parent=owner_of[e.src], source=e.src, target=e.dst,
        )
        ET.SubElement(c, "mxGeometry", relative="1").set("as", "geometry")

    model = ET.Element(
        "mxGraphModel", dx="1000", dy="1000", grid="1", gridSize="10", guides="1", tooltips="1", connect="1",
        arrows="1", fold="1", page="1", pageScale="1", pageWidth="1169", pageHeight="827", math="0", shadow="0",
    )
    model.append(root)
    diagram = ET.Element("diagram", id=d.id, name=d.title)
    diagram.append(model)
    file = ET.Element("mxfile", host="generated")
    file.append(ET.Comment(f" {NOTICE} "))
    file.append(diagram)
    ET.indent(file)
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(file, encoding="unicode") + "\n"


# ── files ─────────────────────────────────────────────────────────────────

FORMATS = {"drawio": ("drawio", to_drawio), "mermaid": ("mmd", to_mermaid)}
IMAGE_FORMATS = ("png", "svg")  # exported from the .drawio file with the draw.io desktop app, when it is available


def canonical_name(diagram_id: str) -> str:
    """The canonical name of a diagram: its id in lower kebab-case, e.g. `high-level-as-is`.

    It has no language, no `.generated` and no file extension. Documents refer to a diagram by this name,
    and every file of the diagram starts with it.
    """
    return diagram_id.lower().replace("_", "-")


def file_stem(diagram_id: str, lang: str) -> str:
    return f"{canonical_name(diagram_id)}.{lang}.generated"


def find_drawio() -> str | None:
    """The draw.io desktop app: $DRAWIO, then the PATH, then the usual install places. None when it is not there."""
    candidates = [
        os.environ.get("DRAWIO"),
        shutil.which("drawio"),
        shutil.which("draw.io"),
        r"C:\Program Files\draw.io\draw.io.exe",
        r"C:\Program Files (x86)\draw.io\draw.io.exe",
        "/Applications/draw.io.app/Contents/MacOS/draw.io",
        "/usr/bin/drawio",
    ]
    return next((c for c in candidates if c and Path(c).exists()), None)


def _kill_tree(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True, check=False)
    else:
        proc.kill()


def export_image(drawio: Path, fmt: str, timeout: float = 90.0) -> Path | None:
    """Export a .drawio file to png or svg next to it. Returns the image, or None when that was not possible.

    Never raises: a missing app, a failing export or a hang only gives None. The app can stay alive after it wrote
    the file, so the export counts as done once the file has stopped growing, and the process we started is ended.
    """
    exe = find_drawio()
    target = drawio.with_suffix(f".{fmt}")
    if not exe or fmt not in IMAGE_FORMATS:
        return None
    try:
        target.unlink(missing_ok=True)
        cmd = [exe, "-x", "-f", fmt, "-b", "10", "-o", str(target), str(drawio)]
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError:
        return None
    size, deadline = -1, time.monotonic() + timeout
    try:
        while time.monotonic() < deadline:
            time.sleep(0.5)
            now = target.stat().st_size if target.exists() else 0
            if now > 0 and now == size:
                break
            if proc.poll() is not None and now == size:
                break
            size = now
    finally:
        _kill_tree(proc)
    return target if target.exists() and target.stat().st_size > 0 else None


def write_diagrams(
    process: dict[str, Any],
    out_dir: Path,
    langs: list[str],
    formats: list[str] | None = None,
    only: list[str] | None = None,
) -> tuple[list[Path], list[str]]:
    """Write every diagram of the process in every language and format. Only `.generated` files are written.

    Returns the written paths and the warnings. A png or svg that could not be exported is a warning, not an error.
    """
    wanted = formats or ["drawio", "mermaid"]
    written: list[Path] = []
    warnings: list[str] = []
    out_dir.mkdir(parents=True, exist_ok=True)
    for diagram in process.get("diagrams") or []:
        if only and diagram["id"] not in only:
            continue
        for lang in langs:
            built = build_diagram(process, diagram, lang)
            images = [f for f in wanted if f in IMAGE_FORMATS]
            for name in [f for f in FORMATS if f in wanted or (images and f == "drawio")]:
                extension, render = FORMATS[name]
                path = out_dir / f"{file_stem(diagram['id'], lang)}.{extension}"
                path.write_text(render(built), encoding="utf-8", newline="\n")
                written.append(path)
            drawio = out_dir / f"{file_stem(diagram['id'], lang)}.drawio"
            for fmt in images:
                image = export_image(drawio, fmt)
                if image:
                    written.append(image)
                else:
                    warnings.append(f"no {fmt} for {drawio.name}: the draw.io app was not found or the export failed")
    return written, warnings
