"""process 0.1 -> 0.2: the pointer of a step to its rule set is `ruleset` (was `decision`).

See decisions_0_1_to_rules_0_2.py for the two functions of a step.
"""

from __future__ import annotations

import re
from typing import Any

from .decisions_0_1_to_rules_0_2 import rename_key

KIND_AFTER, VERSION_AFTER = "process", "0.2"
NOTE = "process 0.1 -> 0.2: the step pointer `decision` -> `ruleset`"


def migrate(data: Any) -> None:
    for step in data.get("steps") or []:
        rename_key(step, "decision", "ruleset")
    data["version"] = VERSION_AFTER


def rewrite(text: str) -> str:
    text = re.sub(r"^(\s+(?:- )?)decision:", r"\1ruleset:", text, flags=re.MULTILINE)  # the key of a step
    return re.sub(r'^version:\s*"?0\.1"?', f'version: "{VERSION_AFTER}"', text, count=1, flags=re.MULTILINE)
