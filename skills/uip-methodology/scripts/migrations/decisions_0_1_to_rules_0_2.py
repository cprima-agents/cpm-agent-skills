"""decisions 0.1 -> rules 0.2: the kind decisions becomes rules.

    decisions:            ->  rulesets:
      - id: MEASURES            - id: MEASURES
        outcomes:        ->       rules:

A decision is a rule set, and its rows are rules. The rest of the file (`actions`, question, inputs, match, notes, the
fields of a row) is unchanged. The ids of the rows are data and stay as they are.

Every step has two functions that do the same thing: `migrate(data)` on the loaded data (the definition, and what the
tests check) and `rewrite(text)` on the text of the file (what the command writes: the formatting and the comments of
the file stay exactly as they are). `migrations.migrate_text` checks that both agree.
"""

from __future__ import annotations

import re
from typing import Any

KIND_AFTER, VERSION_AFTER = "rules", "0.2"
NOTE = "decisions 0.1 -> rules 0.2: `decisions` -> `rulesets`, `outcomes` -> `rules`"


def rename_key(mapping: Any, old: str, new: str) -> None:
    """Rename a key and keep its place in the mapping."""
    if old not in mapping:
        return
    if hasattr(mapping, "insert"):  # a ruamel mapping keeps the order and its comments
        position = list(mapping).index(old)
        mapping.insert(position, new, mapping.pop(old))
    else:  # a plain dict: rebuild it in the same order
        items = list(mapping.items())
        mapping.clear()
        for key, value in items:
            mapping[new if key == old else key] = value


def migrate(data: Any) -> None:
    rename_key(data, "decisions", "rulesets")
    for ruleset in data.get("rulesets") or []:
        rename_key(ruleset, "outcomes", "rules")
    data["version"] = VERSION_AFTER


def rewrite(text: str) -> str:
    text = re.sub(r"^decisions:", "rulesets:", text, flags=re.MULTILINE)  # the top-level key
    text = re.sub(r"^(\s+)outcomes:", r"\1rules:", text, flags=re.MULTILINE)  # the rows of a rule set
    return re.sub(r'^version:\s*"?0\.1"?', f'version: "{VERSION_AFTER}"', text, count=1, flags=re.MULTILINE)
