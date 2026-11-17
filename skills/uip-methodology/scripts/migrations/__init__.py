"""Migrations of the source files of a project to the current version of the data model.

The current versions are stated in `references/data-model-versions.yaml`. A migration step is a module: it says which
kind and version a file has after the step, changes loaded data (`migrate`) and rewrites the text of a file
(`rewrite`). `migrate` and `migrate_text` chain the steps until the file is current. Every step has a test
(`test_migrations.py`).

A step is registered under (kind, version): the kind and the version a file has BEFORE the step.
"""

from __future__ import annotations

import copy
from pathlib import Path
from types import ModuleType
from typing import Any

from ruamel.yaml import YAML

from . import decisions_0_1_to_rules_0_2, process_0_1_to_0_2

VERSIONS_FILE = Path(__file__).resolve().parent.parent.parent / "references" / "data-model-versions.yaml"

STEPS: dict[tuple[str, str], ModuleType] = {
    ("decisions", "0.1"): decisions_0_1_to_rules_0_2,
    ("process", "0.1"): process_0_1_to_0_2,
}


class MigrationError(Exception):
    """A file cannot be brought to the current version."""


def versions() -> dict[str, Any]:
    return (YAML(typ="safe").load(VERSIONS_FILE.read_text(encoding="utf-8")) or {}).get("kinds") or {}


def current(kind: str) -> str | None:
    """The current version of a kind of source file; None for a kind that is not known."""
    entry = versions().get(kind)
    return str(entry["current"]) if entry else None


def legacy_kinds() -> dict[str, str]:
    """Kind names that were renamed: old name -> new name."""
    return {str(v["renamed_from"]): k for k, v in versions().items() if v.get("renamed_from")}


def kind_of_name(file_name: str) -> str | None:
    """The kind of a source file from its name (process*, rules*, ...), also under an old name (decisions*)."""
    name = file_name.lower()
    for kind in (*versions(), *legacy_kinds()):
        if name.startswith(kind):
            return kind
    return None


def _check_current(kind: str, version: str) -> None:
    expected = current(kind)
    if expected is None:
        raise MigrationError(f"'{kind}' is not a kind of source file the skill knows")
    if version != expected:
        raise MigrationError(f"a {kind} file of version {version} cannot be migrated; the current version is {expected}")


def migrate(kind: str, data: Any) -> tuple[str, Any, list[str]]:
    """Bring loaded data to the current version, in place. Returns the new kind, the data and a note per step."""
    notes: list[str] = []
    version = str(data.get("version"))
    while (kind, version) in STEPS:
        step = STEPS[(kind, version)]
        step.migrate(data)
        kind, version = step.KIND_AFTER, step.VERSION_AFTER
        notes.append(step.NOTE)
    _check_current(kind, version)
    return kind, data, notes


def migrate_text(kind: str, text: str) -> tuple[str, str, list[str]]:
    """Bring the text of a file to the current version; the formatting and the comments of the file stay.

    The result is checked: the rewritten text must load to exactly what `migrate` makes of the loaded original.
    """
    safe = YAML(typ="safe")
    original = safe.load(text) or {}
    expected = copy.deepcopy(original)
    new_kind, expected, notes = migrate(kind, expected)
    version = str(original.get("version"))
    kind_now = kind
    while (kind_now, version) in STEPS:
        step = STEPS[(kind_now, version)]
        text = step.rewrite(text)
        kind_now, version = step.KIND_AFTER, step.VERSION_AFTER
    if safe.load(text) != expected:
        raise MigrationError("the rewritten file does not match the migrated data: the migration needs a fix")
    return new_kind, text, notes
