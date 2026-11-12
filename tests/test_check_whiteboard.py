import importlib.util
import sys
from pathlib import Path

import pytest

_spec = importlib.util.spec_from_file_location(
    "check_whiteboard",
    Path(__file__).parent.parent / "scripts" / "check-whiteboard.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
main = _mod.main
parse_header = _mod.parse_header
has_content = _mod.has_content


# --- unit tests ---

def test_parse_header_profile():
    assert parse_header("<!-- type: profile -->") == ("profile", None)


def test_parse_header_lesson_intro():
    assert parse_header("<!-- type: lesson-intro round: 1/3 -->") == ("lesson-intro", 1)


def test_parse_header_round_cap():
    assert parse_header("<!-- type: lesson-diagnostic round: 3/3 -->") == ("lesson-diagnostic", 3)


def test_parse_header_invalid():
    assert parse_header("# Not a header") == (None, None)


def test_has_content_real_text():
    assert has_content(["FastAPI"]) is True


def test_has_content_empty():
    assert has_content([]) is False
    assert has_content(["", "  "]) is False


def test_has_content_placeholder_only():
    assert has_content(["e.g. FastAPI, pandas"]) is False
    assert has_content(["Delete two, leave one"]) is False


def test_has_content_mixed():
    assert has_content(["e.g. FastAPI", "FastAPI"]) is True


# --- CLI integration tests ---

def run_main(tmp_path, content, capsys):
    if content is not None:
        (tmp_path / "WHITEBOARD.md").write_text(content)
    with pytest.raises(SystemExit) as exc:
        main(root=tmp_path)
    return exc.value.code, capsys.readouterr().out


INTRO_FILLED = """\
<!-- type: lesson-intro round: 1/3 -->

## What tool or concept do you want to learn?
FastAPI

## What specifically about it?
Routing and dependency injection

## What should you be able to do after this lesson?
Build a small REST API from scratch

## Your experience with this specific tool
none
"""

INTRO_MISSING_SCOPE = """\
<!-- type: lesson-intro round: 1/3 -->

## What tool or concept do you want to learn?
FastAPI

## What specifically about it?
e.g. routing and dependency injection

## What should you be able to do after this lesson?
Build a small REST API from scratch

## Your experience with this specific tool
none
"""

DIAGNOSTIC_FILLED = """\
<!-- type: lesson-diagnostic round: 1/3 -->

## Context from phase 1 (do not edit)
Topic: FastAPI

## Have you used Python type hints?
Yes, I use them regularly in function signatures.

## Have you worked with decorators?
I know the basics — I've used @property and @staticmethod.
"""

DIAGNOSTIC_MISSING_ANSWER = """\
<!-- type: lesson-diagnostic round: 1/3 -->

## Context from phase 1 (do not edit)
Topic: FastAPI

## Have you used Python type hints?

## Have you worked with decorators?
I know the basics.
"""

CONSTRAINTS_FILLED = """\
<!-- type: lesson-constraints round: 1/3 -->

## Context (do not edit)
Topic: FastAPI

## Time budget
2

## Language preference

## Hard constraints
"""

CONSTRAINTS_MISSING_TIME = """\
<!-- type: lesson-constraints round: 1/3 -->

## Context (do not edit)
Topic: FastAPI

## Time budget

## Language preference

## Hard constraints
"""


def test_missing_whiteboard(tmp_path, capsys):
    code, out = run_main(tmp_path, None, capsys)
    assert code == 2
    assert "not found" in out


def test_empty_whiteboard(tmp_path, capsys):
    code, out = run_main(tmp_path, "", capsys)
    assert code == 2


def test_invalid_header(tmp_path, capsys):
    code, out = run_main(tmp_path, "# No header here\n\nSome content", capsys)
    assert code == 2
    assert "valid type header" in out


def test_profile_exits_0(tmp_path, capsys):
    code, _ = run_main(tmp_path, "<!-- type: profile -->\n\n## Experience level\njunior", capsys)
    assert code == 0


def test_round_cap_exits_1(tmp_path, capsys):
    content = INTRO_FILLED.replace("round: 1/3", "round: 3/3")
    code, out = run_main(tmp_path, content, capsys)
    assert code == 1
    assert "Round cap reached" in out


def test_lesson_intro_valid(tmp_path, capsys):
    code, out = run_main(tmp_path, INTRO_FILLED, capsys)
    assert code == 0
    assert "valid" in out.lower()


def test_lesson_intro_missing_field(tmp_path, capsys):
    code, out = run_main(tmp_path, INTRO_MISSING_SCOPE, capsys)
    assert code == 2
    assert "scope" in out


def test_lesson_diagnostic_valid(tmp_path, capsys):
    code, out = run_main(tmp_path, DIAGNOSTIC_FILLED, capsys)
    assert code == 0


def test_lesson_diagnostic_missing_answer(tmp_path, capsys):
    code, out = run_main(tmp_path, DIAGNOSTIC_MISSING_ANSWER, capsys)
    assert code == 2
    assert "type hints" in out


def test_lesson_constraints_valid(tmp_path, capsys):
    code, out = run_main(tmp_path, CONSTRAINTS_FILLED, capsys)
    assert code == 0


def test_lesson_constraints_missing_time(tmp_path, capsys):
    code, out = run_main(tmp_path, CONSTRAINTS_MISSING_TIME, capsys)
    assert code == 2
    assert "time_budget_hours" in out


def test_unknown_type(tmp_path, capsys):
    code, out = run_main(tmp_path, "<!-- type: unknown-type round: 1/3 -->", capsys)
    assert code == 2
    assert "Unknown" in out
