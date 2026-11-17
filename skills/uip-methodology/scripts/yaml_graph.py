"""Graph checks, models and diagrams for a process yaml: steps are nodes, `edges` are the links.

Used by lint_yaml_text.py and cpm_rpa/from_yaml.py. Also meant for the view-layer renderers, which derive
numbers and diagrams from the graph; the yaml itself never holds a sequence number or a tool-specific shape id.

Shape (see assets/templates/process.template.yml):
    models:    as-is | to-be      the two process models: as-is describes what exists, to-be specifies what shall exist
    diagrams:  [{id, title, models, detail}]   a diagram renders one or both models at a level of detail
    steps:     [{id, type, parent?, models?, diagrams?, kind?, role?, closes?, ...}]
    edges:     [{from, to, models?, condition?, exception?, tags?}]   edges point forward, from a step to the next

`models` missing on a step or edge = it belongs to both models.
Levels: a step with `parent: <step id>` is a sub-step of that task. Edges connect steps of the same level only.
The top level has one start_event; every sub-level has exactly one entry step (no incoming edge) and at least
one exit step (no outgoing edge). Each model is checked as a graph of its own, and so is each diagram.
"""

import sys
from collections import defaultdict, deque
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from cpm_rpa import schema as _schema  # noqa: E402

KINDS = ("exclusive", "inclusive", "parallel")
ROLES = ("split", "join")
MODELS = ("as-is", "to-be")
DETAILS = ("high-level", "detailed")
_SCHEMA = _schema.load()


def enum_ids(name):
    """The ids of an enumeration of rpa-methodology.yaml, in order. The schema is the single source of every list."""
    return tuple(_schema.enum_labels(_SCHEMA, name))


def enum_entries(name):
    """The entries (id, label, ...) of an enumeration of rpa-methodology.yaml."""
    return list((_SCHEMA.get("enums") or {}).get(name) or [])


STAGES = enum_ids("pipeline_stage")


def parent_of(step, model=None):
    """The step a step sits in, for one model. `parent` is an id (the same in both models) or a mapping
    {as-is: id, to-be: id}; a model missing from the mapping has the step on the top level.
    Without a model, a mapping gives the first parent it names."""
    p = step.get("parent")
    if isinstance(p, dict):
        if model is not None:
            return p.get(model)
        return next((p[m] for m in MODELS if p.get(m)), None)
    return p


def stage_of(g, step, model=None):
    """The pipeline stage of a step: its own `stage`, else its parent's (in `model`), else None."""
    by_id = {s["id"]: s for s in g["steps"]}
    seen = set()
    while step is not None and step["id"] not in seen:
        if step.get("stage"):
            return step["stage"]
        seen.add(step["id"])
        step = by_id.get(parent_of(step, model))
    return None


# ── models ────────────────────────────────────────────────────────────────

def models_of(item):
    """The models an item belongs to. Missing `models` = both."""
    m = item.get("models")
    return list(m) if m else list(MODELS)


def sub_graph(g, models):
    """Steps and edges that belong to at least one of the given models.

    Every step carries the one parent it has in these models (see parent_of). A view of two models takes a step's
    parent from the first model it belongs to, as-is before to-be.
    """
    wanted = set(models)

    def resolved(s):
        own = [m for m in MODELS if m in wanted and m in models_of(s)]
        return {**s, "parent": parent_of(s, own[0])} if isinstance(s.get("parent"), dict) else s

    steps = [resolved(s) for s in g["steps"] if set(models_of(s)) & wanted]
    ids = {s["id"] for s in steps}
    edges = [
        e for e in g.get("edges") or []
        if set(models_of(e)) & wanted and e.get("from") in ids and e.get("to") in ids
    ]
    return {"steps": steps, "edges": edges}


# ── one graph ─────────────────────────────────────────────────────────────

def _loop(edge):
    return "loop" in (edge.get("tags") or [])


def _scope_graph(group, edges):
    ids = {s["id"] for s in group}
    out, inc = defaultdict(list), defaultdict(list)
    for e in edges:
        if e.get("from") in ids and e.get("to") in ids:
            out[e["from"]].append(e)
            inc[e["to"]].append(e)
    return out, inc


def _cycles(out, entry):
    """Edges that close a cycle, found depth-first from the entry in declaration order."""
    state, back = {}, []

    def dfs(n):
        state[n] = 1
        for e in out[n]:
            m = e["to"]
            if state.get(m) == 1:
                back.append(e)
            elif m not in state:
                dfs(m)
        state[n] = 2

    dfs(entry)
    return back


def _branch_problem(types, out, start, join_id):
    """Follow a branch forward, stopping at the join. Return a text if it can end without the join."""
    seen, stack = set(), [start]
    while stack:
        n = stack.pop()
        if n == join_id or n in seen:
            continue
        seen.add(n)
        if types.get(n) == "end_event":
            return f"ends at {n}"
        nxt = [e["to"] for e in out[n] if not _loop(e)]
        if not nxt:
            return f"dead-ends at {n}"
        stack.extend(nxt)
    return None


def _lint_scope(parent, group, out, inc):
    errs = []
    where = f"level of {parent}" if parent else "top level"
    types = {s["id"]: s.get("type") for s in group}
    ids = set(types)
    starts = [s["id"] for s in group if s.get("type") == "start_event"]
    if parent is None:
        if len(starts) != 1:
            errs.append(f"{where}: need exactly one start_event, found {len(starts)}")
        entry = starts[0] if starts else None
    else:
        for s in group:
            if s.get("type") in ("start_event", "end_event"):
                errs.append(f"{s['id']}: a sub-step level has no start or end event")
        entries = [s["id"] for s in group if not inc[s["id"]]]
        if len(entries) != 1:
            errs.append(f"{where}: need exactly one entry step without incoming edge, found {len(entries)}")
        entry = entries[0] if len(entries) == 1 else None
        if not [s for s in group if not out[s["id"]]]:
            errs.append(f"{where}: no exit step without outgoing edge")

    cause = False
    for s in group:
        sid, kind, role = s["id"], s.get("kind"), s.get("role")
        if parent is None:
            if s.get("type") != "end_event" and not out[sid]:
                errs.append(f"{sid}: no outgoing edge"); cause = True
            if s.get("type") != "start_event" and not inc[sid]:
                errs.append(f"{sid}: no incoming edge"); cause = True
        if (kind or role) and s.get("type") != "gateway":
            errs.append(f"{sid}: kind and role belong to gateways only")
        if s.get("type") == "gateway":
            if kind not in KINDS:
                errs.append(f"{sid}: gateway kind must be one of {', '.join(KINDS)}")
            if role not in ROLES:
                errs.append(f"{sid}: gateway role must be one of {', '.join(ROLES)}")
        if role == "split":
            joins = [j for j in group if j.get("role") == "join" and j.get("closes") == sid]
            # a join is required only for inclusive and parallel splits;
            # an exclusive split may converge by plain edges into the same step
            need_join = kind in ("inclusive", "parallel")
            if len(joins) > 1 or (need_join and len(joins) != 1):
                errs.append(f"{sid}: {kind} split needs exactly one join, found {len(joins)}")
            elif joins and joins[0].get("kind") != kind:
                errs.append(f"{sid}: its join {joins[0]['id']} has a different kind")
            elif joins:
                for e in out[sid]:
                    problem = _branch_problem(types, out, e["to"], joins[0]["id"])
                    if problem:
                        errs.append(f"{sid} -> {e['to']}: branch {problem} before reaching {joins[0]['id']}")
            if kind in ("exclusive", "inclusive"):
                for e in out[sid]:
                    if not e.get("condition"):
                        errs.append(f"{sid} -> {e['to']}: a branch of an {kind} split needs a condition")
        if role == "join":
            if s.get("closes") not in ids:
                errs.append(f"{sid}: 'closes' must name a split on the same level")
            if len(inc[sid]) < 2:
                errs.append(f"{sid}: a join needs at least two incoming edges")

    if entry and not cause:
        seen, dq = {entry}, deque([entry])
        while dq:
            for e in out[dq.popleft()]:
                if e["to"] not in seen:
                    seen.add(e["to"]); dq.append(e["to"])
        for s in group:
            if s["id"] not in seen:
                errs.append(f"{s['id']}: not reachable from the {'start' if parent is None else 'entry'} step")
    if entry:
        for e in _cycles(out, entry):
            if not _loop(e):
                errs.append(f"edge {e['from']} -> {e['to']} closes a cycle (tag the edge 'loop' if intended)")
    return errs


def _lint_flow(g):
    """The flow checks of one graph (one model, or one diagram)."""
    steps = g.get("steps") or []
    ids = {s["id"] for s in steps}
    groups = defaultdict(list)
    for s in steps:
        if s.get("parent") in ids or s.get("parent") is None:
            groups[s.get("parent")].append(s)
    errs = []
    for parent, group in groups.items():
        out, inc = _scope_graph(group, g.get("edges") or [])
        errs.extend(_lint_scope(parent, group, out, inc))
    return errs


# ── diagrams ──────────────────────────────────────────────────────────────

def diagram_view(g, diagram):
    """The graph a diagram shows: the steps of its models at its level of detail.

    A step is shown when it belongs to one of the diagram's models, the diagram's detail reaches it
    (high-level = top level only), and the step does not restrict itself to other diagrams with `diagrams`.
    Hidden steps are removed and the edges are joined through them.
    """
    wanted = set(diagram.get("models") or MODELS)
    expand = set(diagram.get("expand") or [])
    g = {**g, **sub_graph(g, wanted)}  # the steps with the one parent they have in these models
    by_id = {s["id"]: s for s in g["steps"]}
    visible = []
    for s in g["steps"]:
        if not set(models_of(s)) & wanted:
            continue
        if s["id"] in expand:
            continue  # shown through its sub-steps instead
        opened = s.get("parent") in expand
        if diagram.get("detail") == "high-level" and s.get("parent") is not None and not opened:
            continue
        if s.get("diagrams") and diagram.get("id") not in s["diagrams"]:
            continue
        if opened:  # a sub-step of an expanded activity sits on the top level, in the lane of the activity
            outer = s["parent"]  # the outermost expanded step it came from: its band, if the diagram draws bands
            while by_id[outer].get("parent") in expand:
                outer = by_id[outer]["parent"]
            s = {**s, "parent": None, "lane": s.get("lane") or by_id[s["parent"]].get("lane"), "band": outer}
        visible.append(s)
    vis = {s["id"] for s in visible}
    links = [e for e in g.get("edges") or [] if set(models_of(e)) & wanted]
    for x in expand:  # an expanded activity is entered at its entry step and left from its exit steps
        kids = {s["id"] for s in g["steps"] if s.get("parent") == x and set(models_of(s)) & wanted}
        inner = [e for e in links if e["from"] in kids and e["to"] in kids]
        entries = kids - {e["to"] for e in inner}
        exits = kids - {e["from"] for e in inner}
        rewired = []
        for e in links:
            if e["to"] == x:
                rewired.extend({**e, "to": k} for k in sorted(entries))
            elif e["from"] == x:
                rewired.extend({**e, "from": k} for k in sorted(exits))
            else:
                rewired.append(e)
        links = rewired
    out = defaultdict(list)
    for e in links:
        out[e["from"]].append(e)
    edges, pairs = [], set()
    for s in visible:
        for e in out[s["id"]]:
            stack, seen = [e], set()
            while stack:
                cur = stack.pop()
                tgt = cur["to"]
                if tgt in vis:
                    if (s["id"], tgt) not in pairs:
                        pairs.add((s["id"], tgt))
                        new = {"from": s["id"], "to": tgt}
                        if cur is e:  # a direct edge keeps its condition and its tags (for example `loop`)
                            if e.get("condition"):
                                new["condition"] = e["condition"]
                            if e.get("tags"):
                                new["tags"] = list(e["tags"])
                        edges.append(new)
                elif tgt not in seen:
                    seen.add(tgt)
                    stack.extend(out[tgt])
    return {"steps": visible, "edges": edges}


# ── the whole file ────────────────────────────────────────────────────────

def lint_graph(g):
    """Return a list of problems with the process file. Empty when it is sound."""
    errs = []
    steps = g.get("steps") or []
    edges = g.get("edges") or []
    ids = [s.get("id") for s in steps]
    idset = set(ids)
    if len(ids) != len(idset):
        errs.append("steps: duplicate step id")
    by_id = {s["id"]: s for s in steps if "id" in s}

    for item in steps + edges + (g.get("exceptions") or []) + (g.get("terminal_states") or []):
        for m in item.get("models") or []:
            if m not in MODELS:
                errs.append(f"{item.get('id') or (item.get('from'), item.get('to'))}: model '{m}' is not one of {', '.join(MODELS)}")

    for s in steps:
        if s.get("stage") and s["stage"] not in STAGES:
            errs.append(f"{s['id']}: stage '{s['stage']}' is not one of {', '.join(STAGES)}")
        if isinstance(s.get("parent"), dict):
            for m in s["parent"]:
                if m not in MODELS:
                    errs.append(f"{s['id']}: parent names the model '{m}', which is not one of {', '.join(MODELS)}")
        for m in models_of(s):  # the parent is checked in each model the step belongs to
            p = parent_of(s, m)
            if p is None:
                continue
            if p not in idset:
                errs.append(f"{s['id']}: parent '{p}' is not a step id")
            elif by_id[p].get("type") != "task":
                errs.append(f"{s['id']}: parent '{p}' must be a task")
            elif m not in models_of(by_id[p]):
                errs.append(f"{s['id']}: belongs to the model {m}, which its parent {p} does not belong to")
    for e in edges:
        bad = [end for end in ("from", "to") if e.get(end) not in idset]
        for end in bad:
            errs.append(f"edges: '{e.get(end)}' is not a step id")
        if bad:
            continue
        for m in models_of(e):
            if m in models_of(by_id[e["from"]]) and m in models_of(by_id[e["to"]]):
                if parent_of(by_id[e["from"]], m) != parent_of(by_id[e["to"]], m):
                    errs.append(f"edge {e['from']} -> {e['to']}: connects steps of different levels in the model {m}")
        for end in ("from", "to"):
            if not set(models_of(e)) <= set(models_of(by_id[e[end]])):
                errs.append(f"edge {e['from']} -> {e['to']}: belongs to a model that {e[end]} does not belong to")
    for x in (g.get("exceptions") or []) + (g.get("terminal_states") or []):
        trigger = by_id.get(x.get("trigger"))
        if x.get("trigger") and trigger and not set(models_of(x)) <= set(models_of(trigger)):
            errs.append(f"{x['id']}: belongs to a model its trigger step {x['trigger']} does not belong to")

    diagrams = g.get("diagrams") or []
    dids = [d.get("id") for d in diagrams]
    if len(dids) != len(set(dids)):
        errs.append("diagrams: duplicate diagram id")
    for d in diagrams:
        if not d.get("models") or any(m not in MODELS for m in d["models"]):
            errs.append(f"{d.get('id')}: models must be a non-empty list of {', '.join(MODELS)}")
        if d.get("detail") not in DETAILS:
            errs.append(f"{d.get('id')}: detail must be one of {', '.join(DETAILS)}")
        shown = [m for m in d.get("models") or [] if m in MODELS]
        if len(shown) > 1:  # one picture of two models needs every step in the same place in both
            moved = [
                s["id"] for s in steps
                if all(m in models_of(s) for m in shown) and len({parent_of(s, m) for m in shown}) > 1
            ]
            if moved:
                errs.append(
                    f"{d.get('id')}: cannot show {' and '.join(shown)} in one diagram, because these steps have a "
                    f"different parent in each model: {', '.join(moved)}"
                )
        for x in d.get("expand") or []:
            if x not in by_id or by_id[x].get("type") != "task" or not any(
                parent_of(s, m) == x for s in steps for m in models_of(s)
            ):
                errs.append(f"{d.get('id')}: expand '{x}' must be a task that has sub-steps")
    for s in steps:
        for ref in s.get("diagrams") or []:
            if ref not in dids:
                errs.append(f"{s['id']}: diagram '{ref}' is not defined under diagrams")
    if errs:
        return errs

    # each model is a graph of its own
    for m in MODELS:
        sub = sub_graph(g, [m])
        if sub["steps"]:
            errs.extend(f"[{m}] {line}" for line in _lint_flow(sub))
    if errs:
        return errs

    # each diagram must show a sound graph, too
    for d in diagrams:
        errs.extend(f"[diagram {d['id']}] {line}" for line in _lint_flow(diagram_view(g, d)))
    return errs


def number(g, model=None):
    """Labels for one model: top level 1, 2, 3; sub-steps 6.1, 6.2. Only tasks are numbered.
    Topological order per level, ties broken by declaration order, edges tagged 'loop' ignored.
    Never stored in the yaml. Without a model, the whole graph is numbered."""
    graph = sub_graph(g, [model]) if model else g
    labels = {}
    kind = {s["id"]: s.get("type") for s in graph["steps"]}

    def level(parent, prefix):
        count = 0
        for sid in _level_order(graph, parent):
            if kind[sid] != "task":
                continue  # only tasks are numbered; events and gateways have no number
            count += 1
            labels[sid] = f"{prefix}{count}"
            level(sid, f"{prefix}{count}.")

    level(None, "")
    return labels


def _level_order(graph, parent):
    """The steps of one level in flow order: topological, ties broken by declaration order, loop edges ignored."""
    decl = {s["id"]: i for i, s in enumerate(graph["steps"])}
    ids = {s["id"] for s in graph["steps"] if s.get("parent") == parent}
    indeg, out = defaultdict(int), defaultdict(list)
    for e in graph.get("edges") or []:
        if e["from"] in ids and e["to"] in ids and not _loop(e):
            indeg[e["to"]] += 1
            out[e["from"]].append(e["to"])
    ready = sorted([i for i in ids if indeg[i] == 0], key=decl.get)
    order = []
    while ready:
        n = ready.pop(0)
        order.append(n)
        for m in out[n]:
            indeg[m] -= 1
            if indeg[m] == 0:
                ready.append(m)
        ready.sort(key=decl.get)
    return order + sorted(ids - set(order), key=decl.get)  # the rest only if an untagged cycle exists


def reading_order(g, model=None):
    """All step ids in the order a reader goes through them: a step, then its sub-steps, then the next step."""
    graph = sub_graph(g, [model]) if model else g
    order = []

    def walk(parent):
        for sid in _level_order(graph, parent):
            order.append(sid)
            walk(sid)

    walk(None)
    return order
