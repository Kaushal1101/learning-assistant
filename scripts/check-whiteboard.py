#!/usr/bin/env python3
"""
Validates WHITEBOARD.md structure and enforces the round cap.

Exit codes:
  0 — fields valid, round < 3, follow-up permitted
  1 — round == 3, must proceed (hard cap hit)
  2 — missing/unfilled fields, or invalid header
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
ROUND_CAP = 3


def parse_header(line):
    """Parse type header on line 1.

    Returns (type_str, round_int) or (None, None) if unrecognised.
    Profile forms have no round: returns (type_str, None).
    """
    m = re.match(r"<!--\s*type:\s*([\w-]+)\s+round:\s*(\d+)/\d+\s*-->", line)
    if m:
        return m.group(1), int(m.group(2))
    m = re.match(r"<!--\s*type:\s*([\w-]+)\s*-->", line)
    if m:
        return m.group(1), None
    return None, None


def parse_sections(lines):
    """Return dict of {header_text: [content_lines]} for every ## section."""
    sections = {}
    current = None
    for line in lines[1:]:
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
        elif current is not None:
            sections[current].append(line)
    return sections


def has_content(content_lines):
    """True if at least one non-empty, non-placeholder line exists."""
    skip_prefixes = ("e.g.", "<!--", "---", "Delete")
    for line in content_lines:
        stripped = line.strip()
        if not stripped:
            continue
        if any(stripped.startswith(p) for p in skip_prefixes):
            continue
        return True
    return False


def check_lesson_intro(sections):
    errors = []
    required = {
        "What tool or concept do you want to learn?": "topic",
        "What specifically about it?": "scope",
        "What should you be able to do after this lesson?": "goal",
        "Your experience with this specific tool": "tool_experience",
    }
    for header, field in required.items():
        if not has_content(sections.get(header, [])):
            errors.append(f"missing: {field}")
    return errors


def check_lesson_diagnostic(sections):
    errors = []
    for header, content in sections.items():
        if any(kw in header.lower() for kw in ("do not edit", "context")):
            continue
        if not has_content(content):
            errors.append(f"missing answer for: '{header}'")
    return errors


def check_lesson_constraints(sections):
    errors = []
    time_lines = sections.get("Time budget", [])
    if not any(re.search(r"\d+", line) for line in time_lines):
        errors.append("missing: time_budget_hours (section 'Time budget' needs a number)")
    return errors


CHECKERS = {
    "lesson-intro": check_lesson_intro,
    "lesson-diagnostic": check_lesson_diagnostic,
    "lesson-constraints": check_lesson_constraints,
}


def main(root=ROOT):
    path = root / "WHITEBOARD.md"

    if not path.exists():
        print("WHITEBOARD.md not found.")
        sys.exit(2)

    lines = path.read_text().splitlines()
    if not lines:
        print("WHITEBOARD.md is empty.")
        sys.exit(2)

    wb_type, round_num = parse_header(lines[0])

    if wb_type is None:
        print("WHITEBOARD.md has no valid type header on line 1.")
        sys.exit(2)

    if wb_type == "profile":
        sys.exit(0)

    if wb_type not in CHECKERS:
        print(f"Unknown whiteboard type: '{wb_type}'")
        sys.exit(2)

    if round_num == ROUND_CAP:
        print(f"Round cap reached ({ROUND_CAP}/{ROUND_CAP}). Must proceed.")
        sys.exit(1)

    errors = CHECKERS[wb_type](parse_sections(lines))

    if errors:
        print("WHITEBOARD.md has unfilled fields:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(2)

    print(f"Whiteboard valid. Round {round_num}/{ROUND_CAP}.")
    sys.exit(0)


if __name__ == "__main__":
    main()
