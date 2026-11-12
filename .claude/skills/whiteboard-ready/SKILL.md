---
name: whiteboard-ready
description: Submit your filled whiteboard
---

1. Check that `WHITEBOARD.md` exists at the repo root. If not, say "No whiteboard found. Nothing to submit." and stop.

2. Read line 1 of `WHITEBOARD.md` to get the type:
   - `<!-- type: profile -->`
   - `<!-- type: lesson-intake round: N/3 -->`

3. If type is `lesson-intake`: say "Lesson intake is not yet implemented." and stop.

4. If type is `profile`:

   a. Parse the three fields from the form:
      - `experience_level`: the single word the user left after deleting the other two from "junior / mid / senior"
      - `languages`: the comma-separated values written under "Languages you use regularly"
      - `frameworks`: the comma-separated values written under "Frameworks you're comfortable with"

   b. Validate:
      - `experience_level` must be exactly one of: junior, mid, senior
      - `languages` must be a non-empty list
      - `frameworks` must be a list (empty is allowed if user wrote "none")
      If validation fails: list each problem, tell the user to fix them and run /whiteboard-ready again, leave WHITEBOARD.md intact, stop.

   c. Write `user.json` to the repo root with this exact shape:
      ```json
      {
        "experience_level": "<value>",
        "languages": ["<value>", ...],
        "frameworks": ["<value>", ...],
        "updated_at": "<today YYYY-MM-DD>"
      }
      ```
      Normalise all string values to lowercase and trim whitespace. If frameworks was "none", write an empty array `[]`.

   d. Delete `WHITEBOARD.md`.

   e. If `user.json` already existed before this run: say "Profile updated."
      Otherwise: say "Profile saved. Run /new-lesson to start a lesson."
