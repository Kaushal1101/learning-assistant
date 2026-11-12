#!/usr/bin/env python3
import json
import sys
from pathlib import Path

VALID_EXPERIENCE_LEVELS = {"junior", "mid", "senior"}
ROOT = Path(__file__).parent.parent


def main():
    path = ROOT / "user.json"

    if not path.exists():
        print("user.json not found. Run /setup-profile first.")
        sys.exit(1)

    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        print(f"user.json is invalid JSON: {e}")
        sys.exit(1)

    errors = []

    if "experience_level" not in data:
        errors.append("missing: experience_level")
    elif data["experience_level"] not in VALID_EXPERIENCE_LEVELS:
        errors.append(
            f"experience_level must be 'junior', 'mid', or 'senior' (got '{data['experience_level']}')"
        )

    if "languages" not in data:
        errors.append("missing: languages")
    elif not isinstance(data["languages"], list) or len(data["languages"]) == 0:
        errors.append("languages must be a non-empty list")

    if "frameworks" not in data:
        errors.append("missing: frameworks")
    elif not isinstance(data["frameworks"], list):
        errors.append("frameworks must be a list")

    if "updated_at" not in data:
        errors.append("missing: updated_at")

    if errors:
        print("user.json is invalid:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print("Profile valid.")
    sys.exit(0)


if __name__ == "__main__":
    main()
