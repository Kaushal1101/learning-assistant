---
name: new-lesson
description: Start a new lesson
---

1. Run `python scripts/check-profile.py`. If it exits 1, say "Run /setup-profile first." and stop.

2. Check if `WHITEBOARD.md` already exists at the repo root. If it does, say "A whiteboard is already open. Run /whiteboard-ready to continue." and stop.

3. Copy `templates/whiteboard/lesson-intro.md` exactly as-is to `WHITEBOARD.md`.

4. Tell the user: "WHITEBOARD.md is ready. Fill in what you want to learn and run /whiteboard-ready when done."

Do nothing else.
