"""Tests of the migrations of the source files to the current version of the data model."""

from __future__ import annotations

import sys
from io import StringIO
from pathlib import Path

import pytest
from ruamel.yaml import YAML

sys.path.insert(0, str(Path(__file__).parent / "scripts"))
import migrations  # noqa: E402


def load(text: str):
    yaml = YAML()
    yaml.preserve_quotes = True
    return yaml.load(text)


def dump(data) -> str:
    yaml = YAML()
    yaml.width = 4096
    yaml.indent(mapping=2, sequence=4, offset=2)
    out = StringIO()
    yaml.dump(data, out)
    return out.getvalue()


DECISIONS_0_1 = """\
version: "0.1"

# a comment that stays
actions:
  D14:
    business_text: { de: "D14", en: "D14" }

decisions:
  - id: MEASURES
    question: { de: "Frage", en: "Question" }
    inputs: []
    outcomes:
      - id: DEC-001
        reasons: [{ de: "a", en: "a" }]
        actions: [D14]
        result: { de: "r", en: "r" }
        action: { de: "a", en: "a" }
        observation: { de: "o", en: "o" }
"""

PROCESS_0_1 = """\
version: "0.1"
process: demo
steps:
  - id: A
    type: task
    decision: MEASURES
  - id: B
    type: gateway
"""


def test_current_versions_are_known():
    assert migrations.current("rules") == "0.2"
    assert migrations.current("process") == "0.2"
    assert migrations.current("systems") == "0.1"
    assert migrations.current("nonsense") is None


def test_kind_of_name_knows_the_old_name():
    assert migrations.kind_of_name("rules.yaml") == "rules"
    assert migrations.kind_of_name("decisions.yaml") == "decisions"  # renamed: the old name is still recognised
    assert migrations.legacy_kinds() == {"decisions": "rules"}
    assert migrations.kind_of_name("data-model.yaml") == "data-model"
    assert migrations.kind_of_name("readme.md") is None


def test_decisions_become_rules():
    data = load(DECISIONS_0_1)
    kind, data, notes = migrations.migrate("decisions", data)
    assert kind == "rules" and data["version"] == "0.2"
    assert "decisions" not in data and "rulesets" in data
    ruleset = data["rulesets"][0]
    assert "outcomes" not in ruleset and ruleset["rules"][0]["id"] == "DEC-001"  # the ids are data and stay
    assert len(notes) == 1


def test_the_order_of_the_keys_and_the_comments_stay():
    data = load(DECISIONS_0_1)
    _kind, data, _notes = migrations.migrate("decisions", data)
    text = dump(data)
    assert "# a comment that stays" in text
    assert list(data) == ["version", "actions", "rulesets"]
    assert list(data["rulesets"][0]) == ["id", "question", "inputs", "rules"]


def test_the_step_pointer_is_renamed():
    data = load(PROCESS_0_1)
    kind, data, _notes = migrations.migrate("process", data)
    assert kind == "process" and data["version"] == "0.2"
    assert data["steps"][0]["ruleset"] == "MEASURES" and "decision" not in data["steps"][0]
    assert "ruleset" not in data["steps"][1]


def test_a_current_file_is_left_alone_and_a_second_run_changes_nothing():
    kind, data, notes = migrations.migrate("decisions", load(DECISIONS_0_1))
    again_kind, again, again_notes = migrations.migrate(kind, data)
    assert again_notes == [] and again_kind == "rules" and dump(again) == dump(data)


def test_the_text_is_rewritten_and_the_formatting_stays():
    text = DECISIONS_0_1.replace('{ de: "Frage", en: "Question" }', '{ de: "Frage", en: "Question" }  # kept')
    kind, new_text, notes = migrations.migrate_text("decisions", text)
    assert kind == "rules" and len(notes) == 1
    assert 'version: "0.2"' in new_text and "rulesets:" in new_text and "outcomes:" not in new_text
    assert '{ de: "Frage", en: "Question" }  # kept' in new_text  # not a character of the formatting changed
    assert new_text.count("\n") == text.count("\n")


def test_the_text_of_a_process_is_rewritten_too():
    kind, new_text, _notes = migrations.migrate_text("process", PROCESS_0_1)
    assert kind == "process" and "    ruleset: MEASURES" in new_text and "decision:" not in new_text
    again_kind, again_text, again_notes = migrations.migrate_text(kind, new_text)
    assert again_notes == [] and again_text == new_text


def test_an_unknown_version_fails_clearly():
    with pytest.raises(migrations.MigrationError, match="9.9"):
        migrations.migrate("process", load('version: "9.9"\nsteps: []\n'))


def test_an_unknown_kind_fails_clearly():
    with pytest.raises(migrations.MigrationError, match="nonsense"):
        migrations.migrate("nonsense", load('version: "0.1"\n'))
