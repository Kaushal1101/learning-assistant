import importlib.util
import json
import sys
from pathlib import Path

import pytest

_spec = importlib.util.spec_from_file_location(
    "check_profile",
    Path(__file__).parent.parent / "scripts" / "check-profile.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
validate = _mod.validate
main = _mod.main

VALID = {
    "experience_level": "junior",
    "languages": ["python"],
    "frameworks": ["fastapi"],
    "updated_at": "2026-11-12",
}


# --- validate() unit tests ---

def test_valid_profile():
    assert validate(VALID) == []


def test_all_experience_levels():
    for level in ("junior", "mid", "senior"):
        assert validate({**VALID, "experience_level": level}) == []


def test_invalid_experience_level():
    errors = validate({**VALID, "experience_level": "expert"})
    assert any("experience_level" in e for e in errors)


def test_missing_experience_level():
    data = {k: v for k, v in VALID.items() if k != "experience_level"}
    errors = validate(data)
    assert any("experience_level" in e for e in errors)


def test_missing_languages():
    data = {k: v for k, v in VALID.items() if k != "languages"}
    errors = validate(data)
    assert any("languages" in e for e in errors)


def test_empty_languages():
    errors = validate({**VALID, "languages": []})
    assert any("languages" in e for e in errors)


def test_languages_not_a_list():
    errors = validate({**VALID, "languages": "python"})
    assert any("languages" in e for e in errors)


def test_missing_frameworks():
    data = {k: v for k, v in VALID.items() if k != "frameworks"}
    errors = validate(data)
    assert any("frameworks" in e for e in errors)


def test_frameworks_empty_list_is_valid():
    assert validate({**VALID, "frameworks": []}) == []


def test_frameworks_not_a_list():
    errors = validate({**VALID, "frameworks": "fastapi"})
    assert any("frameworks" in e for e in errors)


def test_missing_updated_at():
    data = {k: v for k, v in VALID.items() if k != "updated_at"}
    errors = validate(data)
    assert any("updated_at" in e for e in errors)


def test_multiple_errors_reported():
    errors = validate({})
    assert len(errors) == 4


# --- CLI integration tests ---

def run_main(tmp_path, content, capsys):
    if content is not None:
        (tmp_path / "user.json").write_text(content)
    with pytest.raises(SystemExit) as exc:
        main(root=tmp_path)
    return exc.value.code, capsys.readouterr().out


def test_cli_valid_profile(tmp_path, capsys):
    code, out = run_main(tmp_path, json.dumps(VALID), capsys)
    assert code == 0
    assert "Profile valid." in out


def test_cli_missing_file(tmp_path, capsys):
    code, out = run_main(tmp_path, None, capsys)
    assert code == 1
    assert "user.json not found" in out


def test_cli_invalid_json(tmp_path, capsys):
    code, out = run_main(tmp_path, "not json {", capsys)
    assert code == 1
    assert "invalid JSON" in out


def test_cli_invalid_profile(tmp_path, capsys):
    bad = {**VALID, "experience_level": "wizard"}
    code, out = run_main(tmp_path, json.dumps(bad), capsys)
    assert code == 1
    assert "user.json is invalid" in out
