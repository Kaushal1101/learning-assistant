---
name: update-profile
description: Update your existing user profile
---

1. Run `python scripts/check-profile.py`. If it exits 1, tell the user to run `/setup-profile` first and stop.

2. Read `user.json` and `templates/whiteboard/profile.md`.

3. Write `WHITEBOARD.md` using the profile template, pre-filling each field with the current value from `user.json`:
   - Experience level: replace the "junior / mid / senior" placeholder with the current value
   - Languages: fill in the current comma-separated values
   - Frameworks: fill in the current comma-separated values (or "none" if the array is empty)

4. Tell the user: "WHITEBOARD.md is ready with your current values. Edit what has changed and run /whiteboard-ready when done."

Do nothing else.
