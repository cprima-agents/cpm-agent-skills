# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6", "ruamel.yaml>=0.18"]
# ///
"""Lint process, decisions, systems and data-model yaml files.

1. Every field marked `Text` in assets/templates/*.template.yml must be a pair
   { de: <text>, en: <text> } with both keys filled. A plain string is an error.
2. `status`, where an item has the key, must be one of:
   New, InProgress, UnderReview, Approved, Rejected, Complete.
   The key may be missing; a missing status is not an error. An empty status is.
3. `tags`, where an item has the key, must be a list of unique kebab-case words.
   The key may be missing. The tag `open-question` marks an open question.
4. process files: the steps and `edges` must form a sound graph (see yaml_graph.py), checked once for
   the as-is model, once for the to-be model and once for every diagram: one start, no dangling or
   unreachable step, splits and joins paired, every branch of an inclusive or parallel split reaching
   its join, cycles only on edges tagged `loop`, `models` and `diagrams` consistent. No tool-specific
   shape id (`drawio_id`) is allowed in the file.

Usage:
    uv run scripts/lint_yaml_text.py docs/solution-design/process.yaml docs/solution-design/decisions.yaml

The kind of file is taken from its name: process*, decisions*, systems*, data-model*.
Exit code 1 when an error is found.
"""

import re
import sys
from pathlib import Path

import yaml

from yaml_graph import STAGES, enum_ids, lint_graph

# Paths of the Text fields per kind. "*" stands for every item of a list.
TEXT_PATHS: dict[str, list[str]] = {
    "process": [
        "description",
        "volume.unit",
        "diagrams.*.title",
        "lanes.*.note",
        "steps.*.label",
        "steps.*.notes.*",
        "steps.*.scope_reason",
        "steps.*.scope_impact",
        "steps.*.scope_path",
        "edges.*.condition",
        "terminal_states.*.label",
        "terminal_states.*.note",
        "exceptions.*.label",
        "exceptions.*.message",
        "exceptions.*.note",
        "exceptions.*.notes.*",
        "test_cases.*.description",
        "test_cases.*.note",
        "open_questions.*.text",
    ],
    "decisions": [
        "decisions.*.question",
        "decisions.*.match",
        "decisions.*.no_match",
        "decisions.*.notes.*",
        "actions.*.business_text",
        "decisions.*.outcomes.*.reasons.*",
        "decisions.*.outcomes.*.remark",
        "decisions.*.outcomes.*.result",
        "decisions.*.outcomes.*.action",
        "decisions.*.outcomes.*.note",
        "decisions.*.outcomes.*.observation",
    ],
    "systems": [
        "systems.*.description",
        "systems.*.restrictions",
        "systems.*.notes",
        "systems.*.scope_reason",
        "systems.*.scope_impact",
        "systems.*.scope_path",
        "systems.*.operations.*.purpose",
    ],
    "manifest": [
        "artefacts.*.status",
        "artefacts.*.history.*.changes",
    ],
    "stakeholders": [
        "contacts_business.*.notes",
        "contacts_technical.*.notes",
    ],
    "data-model": [
        "entities.*.description",
        "entities.*.source.container",
        "entities.*.source.location",
        "entities.*.fields.*.description",
        "entities.*.fields.*.scope_reason",
        "entities.*.fields.*.scope_impact",
        "entities.*.fields.*.scope_path",
    ],
}

STATUSES = ("New", "InProgress", "UnderReview", "Approved", "Rejected", "Complete")

# A system id is an entity id like a step id: UPPER_SNAKE_CASE, for example MEINSERVICE.
SYSTEM_ID = re.compile(r"^[A-Z][A-Z0-9]*(_[A-Z0-9]+)*$")

# A tag is a kebab-case word, for example "open-question" or "enrich".
TAG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# Paths of the items that may carry a `status`.
STATUS_PATHS: dict[str, list[str]] = {
    "process": [
        "steps.*",
        "edges.*",
        "terminal_states.*",
        "exceptions.*",
        "open_questions.*",
    ],
    "decisions": [
        "decisions.*",
        "decisions.*.outcomes.*",
    ],
    "systems": [
        "systems.*",
        "systems.*.operations.*",
    ],
    "data-model": [
        "entities.*",
        "entities.*.fields.*",
    ],
}

# The roles of the business contacts (references/rpa-methodology.yaml, contacts_business.role).
BUSINESS_ROLES = ("process-owner", "sponsor", "ba", "pm", "works-council", "dpo", "other")

# Plain values that are allowed instead of a pair.
ALLOWED_PLAIN = {"systems.*.restrictions": {"tbd"}}


def kind_of(path: Path) -> str | None:
    name = path.name.lower()
    for kind in TEXT_PATHS:
        if name.startswith(kind):
            return kind
    return None


def walk(node, parts: list[str], where: str):
    """Yield (location, value) for every value reached by the path. Missing parts are skipped."""
    if not parts:
        yield where, node
        return
    head, rest = parts[0], parts[1:]
    if head == "*":
        if isinstance(node, list):
            for i, item in enumerate(node):
                yield from walk(item, rest, f"{where}[{i}]")
        elif isinstance(node, dict):  # every value of a mapping, e.g. the measures under `actions`
            for key, item in node.items():
                yield from walk(item, rest, f"{where}.{key}")
    elif isinstance(node, dict) and head in node:
        yield from walk(node[head], rest, f"{where}.{head}" if where else head)


def _find_key(node, key, where=""):
    """Every place a mapping has the given key (and its value)."""
    if isinstance(node, dict):
        for k, v in node.items():
            if k == key:
                yield where or "(top)", v
            yield from _find_key(v, key, f"{where}.{k}" if where else str(k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _find_key(v, key, f"{where}[{i}]")


def _one_of(value, allowed: tuple[str, ...]) -> bool:
    return value in allowed


def check_entities(data: dict) -> list[str]:
    """Entities of the domain model. The allowed values come from the enums of rpa-methodology.yaml."""
    field_types, cardinalities = enum_ids("field_type"), enum_ids("cardinality")
    input_types = enum_ids("input_type")
    errors: list[str] = []
    entities = data.get("entities") or []
    ids = [e.get("id") for e in entities]
    names = {e.get("name") for e in entities}
    for dup in sorted({i for i in ids if ids.count(i) > 1}):
        errors.append(f"entities: id '{dup}' appears twice")
    for e in entities:
        eid = e.get("id")
        if not isinstance(eid, str) or not SYSTEM_ID.match(eid):
            errors.append(f"entity '{eid}': id must be UPPER_SNAKE_CASE")
        if not e.get("name"):
            errors.append(f"entity {eid}: name missing")
        if e.get("stage") and e["stage"] not in STAGES:
            errors.append(f"entity {eid}: stage '{e['stage']}' is not one of {', '.join(STAGES)}")
        input_type = (e.get("source") or {}).get("input_type")
        if input_type and not _one_of(input_type, input_types):
            errors.append(f"entity {eid}: source.input_type '{input_type}' is not one of {', '.join(input_types)}")
        seen: set[str] = set()
        for f in e.get("fields") or []:
            fname = f.get("name")
            if fname in seen:
                errors.append(f"entity {eid}: field '{fname}' appears twice")
            seen.add(fname)
            if not _one_of(f.get("type"), field_types):
                errors.append(f"entity {eid}.{fname}: type '{f.get('type')}' is not one of {', '.join(field_types)}")
            if "required" not in f or not isinstance(f["required"], bool):
                errors.append(f"entity {eid}.{fname}: required must be true or false")
            if "pii" in f and not isinstance(f["pii"], bool):
                errors.append(f"entity {eid}.{fname}: pii must be true or false (or left out)")
            if f.get("item_type") and f["item_type"] not in names and f["item_type"] not in field_types:
                errors.append(f"entity {eid}.{fname}: item_type '{f['item_type']}' is neither an entity name nor a field type")
            if f.get("stage") and f["stage"] not in STAGES:
                errors.append(f"entity {eid}.{fname}: stage '{f['stage']}' is not one of {', '.join(STAGES)}")
        for r in e.get("relationships") or []:
            if r.get("target_entity") not in ids:
                errors.append(f"entity {eid}: relationship to '{r.get('target_entity')}', which is not an entity id")
            if not _one_of(r.get("cardinality"), cardinalities):
                errors.append(f"entity {eid}: cardinality '{r.get('cardinality')}' is not one of {', '.join(cardinalities)}")
    return errors


def check(path: Path) -> list[str]:
    kind = kind_of(path)
    if kind is None:
        return [f"{path}: cannot tell the kind from the file name (process, decisions, systems, data-model, manifest, stakeholders)"]
    data = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
    errors: list[str] = []
    for text_path in TEXT_PATHS[kind]:
        for where, value in walk(data, text_path.split("."), ""):
            if value is None:
                continue
            if isinstance(value, str) and value in ALLOWED_PLAIN.get(text_path, ()):
                continue
            if not isinstance(value, dict):
                errors.append(f"{path}: {where}: plain text, must be a pair with 'de' and 'en'")
                continue
            for key in ("de", "en"):
                if not isinstance(value.get(key), str) or not value[key].strip():
                    errors.append(f"{path}: {where}: '{key}' is missing or empty")
            extra = set(value) - {"de", "en"}
            if extra:
                errors.append(f"{path}: {where}: unexpected key(s) {sorted(extra)}")
    for item_path in STATUS_PATHS.get(kind, []):  # a manifest has no status tags: its `status` is a text
        for where, item in walk(data, item_path.split("."), ""):
            if not isinstance(item, dict):
                continue
            if "status" in item and item["status"] not in STATUSES:  # the key may be missing
                errors.append(
                    f"{path}: {where}.status: '{item['status']}' is not one of {', '.join(STATUSES)}"
                )
            if "tags" in item:  # the key may be missing
                tags = item["tags"]
                if not isinstance(tags, list):
                    errors.append(f"{path}: {where}.tags: must be a list")
                    continue
                for tag in tags:
                    if not isinstance(tag, str) or not TAG.match(tag):
                        errors.append(f"{path}: {where}.tags: '{tag}' is not a kebab-case word")
                if len(set(tags)) != len(tags):
                    errors.append(f"{path}: {where}.tags: a tag appears twice")
    if kind == "systems":
        seen_ids: set[str] = set()
        for i, system in enumerate(data.get("systems") or []):
            if "name" in system:
                errors.append(f"{path}: systems[{i}]: 'name' is not allowed; a system has an 'id' (entity) and a 'label' (display name)")
            sid = system.get("id")
            if not isinstance(sid, str) or not SYSTEM_ID.match(sid):
                errors.append(f"{path}: systems[{i}].id: must be an UPPER_SNAKE_CASE id, found '{sid}'")
            elif sid in seen_ids:
                errors.append(f"{path}: systems[{i}].id: '{sid}' appears twice")
            seen_ids.add(str(sid))
            if not system.get("label"):
                errors.append(f"{path}: systems[{i}].label: missing")
            if "in_scope" in system and not isinstance(system["in_scope"], bool):
                errors.append(f"{path}: systems[{i}].in_scope: must be true or false")
            if "previously_automated" in system and system["previously_automated"] not in (True, False, "not-applicable"):
                errors.append(f"{path}: systems[{i}].previously_automated: must be true, false or not-applicable")
    if kind == "stakeholders":
        for section in ("contacts_business", "contacts_technical"):
            for i, c in enumerate(data.get(section) or []):
                for key in ("name", "role", "email"):
                    if not c.get(key):
                        errors.append(f"{path}: {section}[{i}].{key}: missing")
                if section == "contacts_business" and c.get("role") not in BUSINESS_ROLES:
                    errors.append(
                        f"{path}: {section}[{i}].role: '{c.get('role')}' is not one of {', '.join(BUSINESS_ROLES)}"
                    )
                if section == "contacts_technical" and not c.get("system"):
                    errors.append(f"{path}: {section}[{i}].system: missing")
    if kind == "data-model":
        errors.extend(f"{path}: {line}" for line in check_entities(data))
    if kind == "process":
        daily = (data.get("volume") or {}).get("daily")
        if daily is not None:
            lo, hi = daily.get("min"), daily.get("max")
            if not (isinstance(lo, int) and isinstance(hi, int) and 0 <= lo <= hi):
                errors.append(f"{path}: volume.daily: min and max must be whole numbers with 0 <= min <= max")
        errors.extend(f"{path}: {line}" for line in lint_graph(data))
        for where, item in _find_key(data, "drawio_id"):
            errors.append(f"{path}: {where}: 'drawio_id' is tool-specific; keep shape ids out of the process file")
    return errors


def check_system_refs(paths: list[Path]) -> list[str]:
    """When a systems file and other files are linted together, every `system` they name must be a system id."""
    loaded = {p: (kind_of(p), yaml.safe_load(p.read_text(encoding="utf-8-sig"))) for p in paths if kind_of(p)}
    ids = {
        s.get("id")
        for kind, data in loaded.values()
        if kind == "systems"
        for s in (data.get("systems") or [])
    }
    if not ids:
        return []
    errors: list[str] = []
    for path, (kind, data) in loaded.items():
        if kind == "process":
            items = [("steps", s) for s in data.get("steps") or []] + [("exceptions", x) for x in data.get("exceptions") or []]
        elif kind == "decisions":
            items = [("decisions", d) for d in data.get("decisions") or []]
        elif kind == "stakeholders":
            items = [("contacts_technical", c) for c in data.get("contacts_technical") or []]
        else:
            continue
        for section, item in items:
            ref = item.get("system")
            if ref and ref not in ids and not str(ref).startswith("none"):
                errors.append(f"{path}: {section} {item.get('id')}: system '{ref}' is not a system id in the systems file")
    return errors


def check_decision_refs(paths: list[Path]) -> list[str]:
    """The links of the decisions, checked when the files they point at are linted together.

    A step's `decision` must be a decision id of the decisions file. A decision's input `field` must be
    `ENTITY.Field` of the data-model file. A decision that no step points at is reported, too.
    """
    loaded = {p: (kind_of(p), yaml.safe_load(p.read_text(encoding="utf-8-sig"))) for p in paths if kind_of(p)}
    by_kind = {kind: (path, data) for path, (kind, data) in loaded.items()}
    errors: list[str] = []
    if "decisions" in by_kind and "process" in by_kind:
        d_path, d_data = by_kind["decisions"]
        p_path, p_data = by_kind["process"]
        ids = {d.get("id") for d in d_data.get("decisions") or []}
        used = set()
        for s in p_data.get("steps") or []:
            ref = s.get("decision")
            if ref is None:
                continue
            used.add(ref)
            if ref not in ids:
                errors.append(f"{p_path}: steps {s.get('id')}: decision '{ref}' is not a decision id in the decisions file")
        for missing in sorted(i for i in ids - used if i):
            errors.append(f"{d_path}: decisions {missing}: no step of the process file points at it with `decision`")
    if "decisions" in by_kind and "data-model" in by_kind:
        d_path, d_data = by_kind["decisions"]
        _m_path, m_data = by_kind["data-model"]
        fields = {
            f"{e.get('id')}.{f.get('name')}" for e in m_data.get("entities") or [] for f in e.get("fields") or []
        }
        for d in d_data.get("decisions") or []:
            for i in d.get("inputs") or []:
                if i.get("field") not in fields:
                    errors.append(
                        f"{d_path}: decisions {d.get('id')}: input '{i.get('field')}' is not ENTITY.Field of the data-model file"
                    )
    return errors


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    errors: list[str] = []
    for arg in argv:
        errors.extend(check(Path(arg)))
    errors.extend(check_system_refs([Path(a) for a in argv]))
    errors.extend(check_decision_refs([Path(a) for a in argv]))
    for line in errors:
        print(f"[FAIL] {line}")
    print(f"{len(argv)} file(s), {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
