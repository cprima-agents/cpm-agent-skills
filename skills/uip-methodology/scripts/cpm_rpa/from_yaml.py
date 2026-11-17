"""Build project data from the process, systems and decisions yaml files.

The yaml files are the source of truth for the process: steps and edges (a network), the systems,
the decisions. This module turns them into the flat keys the document templates read
(`process_steps`, `applications`, `business_exceptions`, `observations`, ...), so a PDD can be
rendered from them with `render pdd --lang de|en`.

Rules:
- Texts stay text pairs {de, en}; the renderer picks the language.
- Step numbers are derived from the edges (see yaml_graph.number); they are never read from or written to the yaml.
- Only what the yaml files state is written. Everything else is left out, so the template shows [TBD].
"""

from __future__ import annotations

import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

_SCRIPTS = Path(__file__).resolve().parent.parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from cpm_rpa.diagrams import canonical_name, file_stem  # noqa: E402
from cpm_rpa.renderer import resolve_text  # noqa: E402
from yaml_graph import enum_entries, models_of, number, parent_of, reading_order, stage_of, sub_graph  # noqa: E402

FINISHED = ("Approved", "Rejected", "Complete")


def _t(value: Any, lang: str) -> str:
    """Text of a pair (or a plain string) in one language."""
    return "" if value is None else str(resolve_text(value, lang))


def _pair(fn) -> dict[str, str]:
    """Build a text pair from a function of the language."""
    return {"de": fn("de"), "en": fn("en")}


def _is_open_question(item: dict[str, Any]) -> bool:
    return "open-question" in (item.get("tags") or []) and item.get("status") not in FINISHED


# Display words of the SDD tables. Values are (de, en).
_ROLE = {
    "source": ("Quelle", "Source"),
    "target": ("Ziel", "Target"),
    "enrichment": ("Anreicherung", "Enrichment"),
    "orchestration": ("Orchestrierung", "Orchestration"),
}
_DIRECTION = {"read": ("Lesen", "Read"), "write": ("Schreiben", "Write"), "both": ("Beides", "Both")}
_READ_STAGES, _WRITE_STAGES = ("ingest", "enrich"), ("execute", "complete")


def _word(table: dict[str, tuple[str, str]], key: str | None) -> dict[str, str] | str:
    """A display word as a text pair; empty when the key is unknown."""
    de_en = table.get(key or "")
    return {"de": de_en[0], "en": de_en[1]} if de_en else ""


def _known(value: Any) -> Any:
    """A value the yaml states; "tbd" means not stated, so the template shows [TBD]."""
    return None if value in (None, "", "tbd") else value


def _directions(process: dict[str, Any]) -> dict[str, str]:
    """Per system id: read, write or both, from the pipeline stages of the to-be steps that use the system."""
    seen: dict[str, set[str]] = defaultdict(set)
    for s in sub_graph(process, ["to-be"])["steps"]:
        stage, system = stage_of(process, s, "to-be"), s.get("system")
        if not (stage and system):
            continue
        if stage in _READ_STAGES:
            seen[system].add("read")
        if stage in _WRITE_STAGES:
            seen[system].add("write")
    return {system: "both" if len(kinds) == 2 else next(iter(kinds)) for system, kinds in seen.items()}


def _input_type(type_id: str | None) -> dict[str, str] | str:
    """The input format as a text pair, from the labels of enums.input_type."""
    entry = next((e for e in enum_entries("input_type") if e["id"] == type_id), None)
    if not entry:
        return type_id or ""
    return {"de": entry.get("label_de") or entry["label"], "en": entry["label"]}


def _read_steps(process: dict[str, Any], system_id: str) -> set[str]:
    """Numbers (as-is model) of the steps that read from a system: its steps in the ingest or enrich stage.

    A step whose parent also reads from the system is left out, so an activity stands for its sub-steps.
    """
    graph = sub_graph(process, ["as-is"])
    numbers = number(process, "as-is")
    reading = {
        s["id"]
        for s in graph["steps"]
        if s.get("system") == system_id and stage_of(process, s, "as-is") in _READ_STAGES and s["id"] in numbers
    }
    by_id = {s["id"]: s for s in graph["steps"]}
    return {numbers[i] for i in reading if by_id[i].get("parent") not in reading}  # resolved by sub_graph


def _containers(process: dict[str, Any], systems: dict[str, Any], data_model: dict[str, Any]) -> list[dict[str, Any]]:
    """The data containers for the PDD input data table (2.6), one row per container, not per field.

    Entities of the domain model that come from a system (not `automation`) are grouped by their
    `source.container`; an entity without one is its own container.
    """
    label = {s["id"]: s.get("label") or s["id"] for s in systems.get("systems") or []}
    groups: dict[str, list[dict[str, Any]]] = {}
    for e in data_model.get("entities") or []:
        source = e.get("source") or {}
        if not source.get("application") or source["application"] == "automation":
            continue
        name = source.get("container") or {"de": e["name"], "en": e["name"]}
        groups.setdefault(_t(name, "en"), []).append({**e, "_name": name})
    rows = []
    for members in groups.values():
        apps = list(dict.fromkeys(m["source"]["application"] for m in members))
        types = list(dict.fromkeys(m["source"].get("input_type") for m in members if m["source"].get("input_type")))
        steps = {n for app in apps for n in _read_steps(process, app)}
        flags = [m["structured"] for m in members if "structured" in m]
        row: dict[str, Any] = {
            "name": members[0]["_name"],
            "steps": sorted(steps, key=lambda n: [int(p) for p in n.split(".")]),
            "source": {
                "application": ", ".join(label.get(a, a) for a in apps),
                "input_type": _pair(lambda lang: ", ".join(_t(_input_type(t), lang) for t in types)),
                "location": _pair(
                    lambda lang: "; ".join(
                        dict.fromkeys(_t(m["source"]["location"], lang) for m in members if m["source"].get("location"))
                    )
                ),
            },
        }
        if flags:
            row["structured"] = all(flags)
        rows.append(row)
    return rows


def _relative(path: Path, base_dir: Path) -> str | None:
    """A path relative to a folder, with forward slashes; None when there is no relative path (other drive)."""
    try:
        return os.path.relpath(path, base_dir).replace("\\", "/")
    except ValueError:
        return None


def _pipeline(process: dict[str, Any], systems: dict[str, Any], data_model: dict[str, Any]) -> list[dict[str, Any]]:
    """The pipeline stages of the robot run and what happens in each, from the stage containers of the to-be model.

    A stage container is a top-level to-be step with a `stage`. Its steps are the steps directly inside it (a join
    gateway is not shown); its systems are those of all steps inside it. A stage without a container is not listed.
    """
    graph = sub_graph(process, ["to-be"])
    containers = {s["stage"]: s for s in graph["steps"] if s.get("stage") and s.get("parent") is None}
    if not containers:
        return []
    nums = number(process, "to-be")
    label = {s["id"]: s.get("label") or s["id"] for s in systems.get("systems") or []}
    position = {sid: i for i, sid in enumerate(reading_order(process, "to-be"))}

    def inside(container_id: str) -> list[dict[str, Any]]:
        found, todo = [], [container_id]
        while todo:
            holder = todo.pop()
            kids = [s for s in graph["steps"] if s.get("parent") == holder]
            found.extend(kids)
            todo.extend(k["id"] for k in kids)
        return sorted(found, key=lambda s: position[s["id"]])

    rows = []
    for stage in enum_entries("pipeline_stage"):
        container = containers.get(stage["id"])
        if not container:
            continue
        everything = inside(container["id"])
        data: dict[str, Any] = {}
        for e in data_model.get("entities") or []:
            source = e.get("source") or {}
            if e.get("stage") == stage["id"] and source.get("application") not in (None, "automation") and source.get("container"):
                data.setdefault(_t(source["container"], "en"), source["container"])
        rows.append(
            {
                "id": stage["id"],
                "number": nums.get(container["id"], ""),
                "name": stage["label"],
                "purpose": stage.get("purpose") or "",
                "steps": [
                    {"number": nums.get(s["id"], ""), "label": s.get("label")}
                    for s in everything
                    if s.get("parent") == container["id"] and s.get("role") != "join"
                ],
                "systems": list(dict.fromkeys(label[s["system"]] for s in everything if s.get("system") in label)),
                "data": list(data.values()),
            }
        )
    return rows


def _scope(
    process: dict[str, Any],
    systems: dict[str, Any],
    data_model: dict[str, Any],
    decisions: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """PDD 3.3 from the property `in_scope` of the items. Nothing is guessed: an item without `in_scope` is not listed.

    Any system, step, data field or rule (outcome of a decision) may say `in_scope: true|false`, with the optional
    texts `scope_reason`, `scope_impact` and `scope_path`. A system reads as "Automation in <system>"; its notes are
    the reason when it gives no `scope_reason`. A data field reads as "Data field <its name in the source>". A rule
    reads as "Rule <its id>: <its result>".
    """
    items: list[tuple[Any, Any, dict[str, Any], Any]] = []  # name, description, the item, fallback reason
    for s in systems.get("systems") or []:
        label = s.get("label") or s["id"]
        name = {"de": f"Automatisierung in {label}", "en": f"Automation in {label}"}
        items.append((name, s.get("description") or "", s, s.get("notes")))
    for s in process.get("steps") or []:
        items.append((s.get("label"), "", s, None))
    for e in data_model.get("entities") or []:
        for f in e.get("fields") or []:
            shown = f.get("source_key") or f.get("name")
            name = {"de": f"Datenfeld {shown}", "en": f"Data field {shown}"}
            items.append((name, f.get("description") or "", f, None))
    for d in (decisions or {}).get("decisions") or []:
        for o in d.get("outcomes") or []:
            result = o.get("result")
            name = _pair(lambda lang, o=o, result=result: f"{'Regel' if lang == 'de' else 'Rule'} {o.get('id', '')}: {_t(result, lang)}")
            items.append((name, "", o, None))
    in_scope, out_of_scope = [], []
    for name, description, item, fallback in items:
        if item.get("in_scope") is True:
            in_scope.append({"step": name, "description": description})
        elif item.get("in_scope") is False:
            out_of_scope.append(
                {
                    "activity": name,
                    "reason": item.get("scope_reason") or fallback or "",
                    "impact_on_to_be": item.get("scope_impact") or "",
                    "future_automation_path": item.get("scope_path") or "",
                }
            )
    return in_scope, out_of_scope


def _process_map(process: dict[str, Any], diagrams_dir: Path | None, base_dir: Path) -> dict[str, Any] | None:
    """The AS-IS high-level map for the PDD (section 2.4), per language.

    Fault tolerant: the image (png before svg) when it was exported, else the Mermaid text, else only the title,
    which makes the template print [TBD]. Paths are relative to `base_dir`, the folder of the data file.
    """
    pick = next(
        (d for d in process.get("diagrams") or [] if list(d.get("models") or []) == ["as-is"] and d.get("detail") == "high-level"),
        None,
    )
    if not pick or not diagrams_dir:
        return None
    result: dict[str, Any] = {}
    for lang in ("de", "en"):
        stem = diagrams_dir / file_stem(pick["id"], lang)
        entry: dict[str, Any] = {"title": _t(pick.get("title"), lang), "name": canonical_name(pick["id"])}
        image = next((p for p in (Path(f"{stem}.png"), Path(f"{stem}.svg")) if p.is_file() and p.stat().st_size > 0), None)
        if image and (rel := _relative(image, base_dir)):
            entry["image"] = rel
        mermaid = Path(f"{stem}.mmd")
        if "image" not in entry and mermaid.is_file():
            entry["mermaid"] = mermaid.read_text(encoding="utf-8").strip()
        result[lang] = entry
    return result


_SYMBOL = {"gateway": "◇", "start_event": "○", "end_event": "○", "event": "○"}
_OPEN = {"de": "Noch nicht entschieden", "en": "Not decided yet"}


def _target_order(target: Any) -> tuple:
    """Sort key of a next step: step numbers in numeric order, then labels."""
    text = _t(target, "en")
    if re.fullmatch(r"\d+(\.\d+)*", text):
        return (0, tuple(int(p) for p in text.split(".")))
    return (1, text)


def _process_steps(
    process: dict[str, Any],
    systems: dict[str, Any],
    decisions: dict[str, Any] | None,
    process_dir: Path | None,
    base_dir: Path,
) -> list[dict[str, Any]]:
    """The rows of PDD 2.5, one per step of the as-is model, as data. The layout belongs to the snippet.

    A row says what a step is, not where it is shown: number, description, where (the system), screenshots,
    the next steps with their conditions, rules and exceptions. A join gateway is not shown: the flow lands where
    the join leads. A step that ends a level continues where its activity continues.
    """
    graph = sub_graph(process, ["as-is"])
    nums = number(process, "as-is")
    steps = {s["id"]: s for s in graph["steps"]}
    system_label = {s["id"]: s.get("label") or s["id"] for s in systems.get("systems") or []}
    # decision id -> (its position in the decisions chapter, the decision)
    decided = {d["id"]: (i, d) for i, d in enumerate((decisions or {}).get("decisions") or [], start=1)}
    exceptions = process.get("exceptions") or []

    def leaving(sid: str) -> list[dict[str, Any]]:
        return [e for e in graph["edges"] if e["from"] == sid]

    def lands(sid: str, seen: tuple[str, ...]) -> list[str]:
        return [t for _c, t in follow(sid, seen)] if steps[sid].get("role") == "join" else [sid]

    def follow(sid: str, seen: tuple[str, ...] = ()) -> list[tuple[Any, str]]:
        """(condition, step) pairs the flow goes to after a step."""
        if sid in seen:
            return []
        edges = leaving(sid)
        if edges:
            return [(e.get("condition") or "", t) for e in edges for t in lands(e["to"], seen + (sid,))]
        parent = steps[sid].get("parent")
        return follow(parent, seen + (sid,)) if parent else []

    ordered: list[dict[str, Any]] = []
    for s in graph["steps"]:
        if s.get("parent") is None:
            ordered.append(s)
            ordered.extend(c for c in graph["steps"] if c.get("parent") == s["id"])

    rows = []
    for s in ordered:
        sid = s["id"]
        if s.get("role") == "join":
            continue
        following = {
            (_t(cond, "en"), _t(nums.get(t) or steps[t].get("label"), "en")): {
                "condition": cond,
                "target": nums.get(t) or steps[t].get("label"),
            }
            for cond, t in follow(sid)
        }
        shots = []
        for p in s.get("screenshots") or []:
            rel = _relative(process_dir / p["file"], base_dir) if process_dir else None
            if rel:
                shots.append({"caption": p.get("screen", ""), "file": rel})
        rows.append(
            {
                "number": nums.get(sid) or _SYMBOL.get(s.get("type"), ""),
                "description": s.get("label"),
                "where": system_label.get(s.get("system"), ""),
                "screenshots": shots,
                "next": sorted(following.values(), key=lambda n: _target_order(n["target"])),
                # the decision made at this step: its position in the decisions chapter and its question
                "decision": {
                    "index": decided[s["decision"]][0],
                    "question": decided[s["decision"]][1].get("question"),
                }
                if s.get("decision") in decided
                else None,
                "rules": [],
                "exceptions": [
                    x.get("label") for x in exceptions if x.get("trigger") == sid and "as-is" in models_of(x)
                ],
            }
        )
    return rows


_STATUS = {True: {"de": "Offen", "en": "Open"}, False: {"de": "Entschieden", "en": "Decided"}}


def _field_of(data_model: dict[str, Any], ref: str) -> dict[str, Any]:
    """What a decision input reads: `ENTITY.Field` of the data model, as its name in the source and its container.

    A reference that the data model does not know is shown as it is written.
    """
    entity_id, _, name = ref.partition(".")
    for e in data_model.get("entities") or []:
        if e.get("id") == entity_id:
            for f in e.get("fields") or []:
                if f.get("name") == name:
                    return {"name": f.get("source_key") or name, "container": (e.get("source") or {}).get("container") or ""}
    return {"name": ref, "container": ""}


def _decisions(
    process: dict[str, Any], decisions: dict[str, Any] | None, data_model: dict[str, Any]
) -> list[dict[str, Any]]:
    """The decisions chapter of the PDD: one entry per decision of decisions.yaml, in the order of the file.

    A decision is a thing of its own, not a part of a step. A step points at it with `decision: <id>`: a task makes
    the decision, a gateway branches on its result. The entry holds the question, those steps, the data the decision
    reads (fields of the data model), how its rules match, what happens when none matches, and its rules. A rule says
    when it applies, what follows, and whether the business has decided it. A rule without a measure is open.
    """
    actions = (decisions or {}).get("actions") or {}
    steps = process.get("steps") or []
    out = []
    for d in (decisions or {}).get("decisions") or []:
        d_open = _is_open_question(d)
        rules = []
        for o in d.get("outcomes") or []:
            codes = o.get("actions") or []
            if "reasons" in o:
                reasons, remark = o["reasons"], o.get("remark")
                result = o.get("result")
                when = _pair(  # the reasons; a rule without reasons shows its result text instead
                    lambda lang, reasons=reasons, remark=remark, result=result: (
                        " + ".join(_t(r, lang) for r in reasons) or _t(result, lang)
                    )
                    + (f" ({_t(remark, lang)})" if remark else "")
                )
                then = _pair(
                    lambda lang, codes=codes: " + ".join(_t(actions[c]["business_text"], lang) for c in codes)
                    or _OPEN[lang]
                )
                is_open = not codes or _is_open_question(o)
            else:
                when, then, is_open = o.get("result"), o.get("action") or "", d_open or _is_open_question(o)
            rules.append({"id": o.get("id", ""), "when": when, "then": then, "status": _STATUS[is_open]})
        out.append(
            {
                "id": d["id"],
                "question": d.get("question"),
                "made_in": [s.get("label") for s in steps if s.get("decision") == d["id"] and s.get("type") != "gateway"],
                "used_at": [s.get("label") for s in steps if s.get("decision") == d["id"] and s.get("type") == "gateway"],
                "reads": [_field_of(data_model, i["field"]) for i in d.get("inputs") or [] if i.get("field")],
                "match": d.get("match") or "",
                "no_match": d.get("no_match") or "",
                "notes": list(d.get("notes") or []),
                "rules": rules,
            }
        )
    return out


def build_project_data(
    process: dict[str, Any],
    systems: dict[str, Any],
    decisions: dict[str, Any] | None = None,
    diagrams_dir: Path | None = None,
    base_dir: Path = Path("."),
    data_model: dict[str, Any] | None = None,
    process_dir: Path | None = None,
    manifest: dict[str, Any] | None = None,
    stakeholders: dict[str, Any] | None = None,
    objectives: dict[str, Any] | None = None,
    reporting: dict[str, Any] | None = None,
    exception_handling: dict[str, Any] | None = None,
) -> dict[str, Any]:
    # The PDD describes the as-is model in section 2 (process steps) and the to-be model in section 3
    # (business exceptions).
    by_id = {s["id"]: s for s in process.get("steps") or []}
    numbers_to_be = number(process, "to-be")
    exceptions = process.get("exceptions") or []

    def ref(step_id: str, lang: str) -> str:
        """How a to-be step is named in a cell: its number if it has one, else its label."""
        return numbers_to_be.get(step_id) or _t(by_id[step_id].get("label"), lang)

    data: dict[str, Any] = {
        "process_name": process.get("process"),
        "short_description": " ".join(_t(process.get("description"), "en").split())
        and _pair(lambda lang: " ".join(_t(process.get("description"), lang).split())),
    }

    process_map = _process_map(process, diagrams_dir, base_dir)
    if process_map:
        data["process_map"] = process_map
    in_scope, out_of_scope = _scope(process, systems, data_model or {}, decisions)
    if in_scope:
        data["in_scope"] = in_scope
    if out_of_scope:
        data["out_of_scope"] = out_of_scope
    pipeline = _pipeline(process, systems, data_model or {})
    if pipeline:
        data["pipeline"] = pipeline
    if data_model:
        data["entities"] = _containers(process, systems, data_model)  # PDD 2.6: the data containers

    # volume (PDD 2.2): only what the yaml states; the other rows stay [TBD]
    daily = (process.get("volume") or {}).get("daily")
    if daily:
        unit = (process.get("volume") or {}).get("unit")
        data["daily_volume"] = {
            "de": f"{daily['min']} bis {daily['max']} {_t(unit, 'de')} pro Tag".replace("  ", " "),
            "en": f"{daily['min']} to {daily['max']} {_t(unit, 'en')} per day".replace("  ", " "),
        }

    # applications, from systems.yaml
    apps = []
    for s in systems.get("systems") or []:
        app = {
            "name": s.get("label") or s["id"],
            "category": "platform" if s.get("role") == "orchestration" else "application",
            "automation_surface": s.get("interface"),
            "access_method": s.get("accesstype"),
        }
        for key in ("in_scope", "previously_automated", "dev_test_access"):
            if key in s:  # stated in the yaml; a missing key stays missing and renders as [TBD]
                app[key] = s[key]
        if s.get("in_scope") is False:  # out of scope: how to reach the system is of no interest, the cells stay blank
            app["automation_surface"] = None
            app["access_method"] = None
        apps.append(app)
    data["applications"] = apps

    # SDD: the systems in context and their integrations. The direction comes from the pipeline stages of the steps
    # that use a system: ingest and enrich read, execute and complete write.
    directions = _directions(process)
    data["system_context"] = [
        {
            "name": s.get("label") or s["id"],
            "role": _word(_ROLE, s.get("role")),
            "direction": _word(_DIRECTION, directions.get(s["id"])),
            "in_scope": s.get("in_scope"),
            "notes": s.get("notes"),
        }
        for s in systems.get("systems") or []
    ]
    data["integrations"] = [
        {
            "system": s.get("label") or s["id"],
            "integration_method": _known(s.get("interface")),
            "direction": _word(_DIRECTION, directions.get(s["id"])) or None,
            "auth_method": _known(s.get("accesstype")),
        }
        for s in systems.get("systems") or []
        if s.get("in_scope")
    ]
    data["exception_handling"] = [
        {
            "exception_type": x.get("label"),
            "trigger": x.get("message"),
            "robot_action": x.get("note"),
            "max_retries": "",
            "escalation": x.get("resolution"),
        }
        for x in exceptions
        if "to-be" in models_of(x)
    ]

    data["process_steps"] = _process_steps(process, systems, decisions, process_dir, base_dir)
    data["decisions"] = _decisions(process, decisions, data_model or {})

    # business exceptions, from the exceptions of process.yaml
    be = []
    for x in exceptions:
        if x.get("type") != "BusinessRuleException" or "to-be" not in models_of(x):
            continue
        trigger = x.get("trigger")
        be.append(
            {
                "name": x.get("label"),
                "step": (
                    _pair(lambda lang, trigger=trigger: ref(trigger, lang))
                    if trigger in by_id
                    else trigger
                ),
                "trigger": x.get("message"),
                "robot_action": _pair(
                    lambda lang, x=x: f"{_t(x.get('note'), lang)} ({x.get('resolution')})".strip()
                ),
            }
        )
    data["business_exceptions"] = be
    data.update(_from_manifest(manifest or {}))
    data.update(_contacts(stakeholders or {}, systems))
    if (objectives or {}).get("objectives"):  # region `objectives`: PDD 1.1, SDD 1.1; an empty list stays [TBD]
        data["objectives"] = list(objectives["objectives"])
    if (reporting or {}).get("reporting_requirements"):  # region `reporting_requirements`; the number is the position
        data["reporting_requirements"] = [
            {**r, "no": i} for i, r in enumerate(reporting["reporting_requirements"], start=1)
        ]
    if (exception_handling or {}).get("default_be_handling"):  # region `default_be_handling`
        data["default_be_handling"] = list(exception_handling["default_be_handling"])
    return data


def _contacts(stakeholders: dict[str, Any], systems: dict[str, Any]) -> dict[str, Any]:
    """The stakeholder tables of the PDD (1.2) and the SDD (2.1), from stakeholders.yaml.

    In `contacts_business` the `role` is an id of the enum stakeholder_role; the table shows its German or
    English label. In `contacts_technical` the `system` is a system id; the table
    shows the label of that system.
    """
    labels = {s["id"]: s.get("label") or s["id"] for s in systems.get("systems") or []}
    out: dict[str, Any] = {}
    if stakeholders.get("contacts_business"):
        roles = {
            e["id"]: {"de": e.get("label_de") or e["label"], "en": e["label"]} for e in enum_entries("stakeholder_role")
        }
        out["contacts_business"] = [{**c, "role": roles.get(c.get("role"), c.get("role"))} for c in stakeholders["contacts_business"]]
    if stakeholders.get("contacts_technical"):
        out["contacts_technical"] = [
            {**c, "system": labels.get(c.get("system"), c.get("system"))} for c in stakeholders["contacts_technical"]
        ]
    return out


def _from_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    """Version, date, status, history and approvals of every document, from the manifest of the output repository.

    For an artefact `pdd` the keys are `pdd_version`, `pdd_date`, `pdd_status`, `pdd_history`, `pdd_approvals`.
    The version and the date shown in the header are those of the last history row, so they are stated once.
    """
    out: dict[str, Any] = {}
    for a in manifest.get("artefacts") or []:
        key, history = a["id"], list(a.get("history") or [])
        if history:
            out[f"{key}_history"] = history
            out[f"{key}_version"] = history[-1].get("version")
            out[f"{key}_date"] = history[-1].get("date")
        if a.get("status"):
            out[f"{key}_status"] = a["status"]
        if a.get("approvals"):
            out[f"{key}_approvals"] = list(a["approvals"])
    return out
