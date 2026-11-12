---
name: whiteboard-ready
description: Submit your filled whiteboard
---

1. Check that `WHITEBOARD.md` exists at the repo root. If not, say "No whiteboard found. Nothing to submit." and stop.

2. Run `python scripts/check-whiteboard.py`:
   - exit 2 (missing/unfilled fields): print the errors exactly as reported, leave WHITEBOARD.md intact, stop.
   - exit 1 (round cap hit): skip all follow-up logic for this phase — proceed directly to the "satisfied" branch.
   - exit 0 (valid, round < 3): proceed normally, follow-up is permitted if judgment warrants it.

3. Read line 1 of `WHITEBOARD.md` to get the type and round:
   - `<!-- type: profile -->`
   - `<!-- type: lesson-intro round: N/3 -->`
   - `<!-- type: lesson-diagnostic round: N/3 -->`
   - `<!-- type: lesson-constraints round: N/3 -->`

---

### type: profile

a. Parse the three fields:
   - `experience_level`: the single word left after deleting the other two from "junior / mid / senior"
   - `languages`: comma-separated values under "Languages you use regularly"
   - `frameworks`: comma-separated values under "Frameworks you're comfortable with"

b. Validate:
   - `experience_level` must be exactly one of: junior, mid, senior
   - `languages` must be a non-empty list
   - `frameworks` must be a list (empty allowed if user wrote "none")
   If invalid: list each problem, leave WHITEBOARD.md intact, stop.

c. Write `user.json`:
   ```json
   {
     "experience_level": "<value>",
     "languages": ["<value>", ...],
     "frameworks": ["<value>", ...],
     "updated_at": "<today YYYY-MM-DD>"
   }
   ```
   Normalise to lowercase, trim whitespace. Frameworks "none" → empty array.

d. Delete `WHITEBOARD.md`.

e. If `user.json` already existed: say "Profile updated."
   Otherwise: say "Profile saved. Run /new-lesson to start a lesson."

---

### type: lesson-intro

a. Parse: topic, scope, goal, tool_experience.
   Validate tool_experience is one of: none, heard-of, used-a-little, comfortable.
   (Field presence already confirmed by check-whiteboard.py.)

b. Write `WHITEBOARD.md` (type: lesson-diagnostic round: 1/3):

   Line 1: `<!-- type: lesson-diagnostic round: 1/3 -->`

   Then a "Context from phase 1 (do not edit)" section with the parsed values.

   Then 2–3 diagnostic questions targeting prerequisite concepts that the lesson will
   actually require from the user's stated background (read user.json for languages/frameworks).
   Focus on depth: decorators and type hints for FastAPI, array operations for pandas, etc.
   Do NOT ask about the target tool itself if tool_experience is "none".

   Tell the user: "Fill in WHITEBOARD.md and run /whiteboard-ready when done."

---

### type: lesson-diagnostic

a. Read the "Context from phase 1" section.

b. Read the user's answers.

c. Are the answers specific enough to calibrate lesson difficulty?
   If vague (and check-whiteboard.py exited 0, meaning round < 3):
     Overwrite WHITEBOARD.md (type: lesson-diagnostic round: N+1/3).
     Preserve the "Context from phase 1" section.
     Write 1–2 sharper follow-up questions.
     Tell the user: "Fill in WHITEBOARD.md and run /whiteboard-ready when done."
     Stop.

d. If satisfied or check-whiteboard.py exited 1 (round cap):
   Write a diagnostic_notes paragraph summarising the user's actual knowledge level
   and any gaps that will affect lesson design.

   Write `WHITEBOARD.md` (type: lesson-constraints round: 1/3):

   Line 1: `<!-- type: lesson-constraints round: 1/3 -->`

   A "Context (do not edit)" section with phase 1 values + diagnostic_notes.

   User-fillable fields:
   - Time budget (hours)
   - Language preference (if ambiguous from topic and user.json)
   - Hard constraints

   An "Agent's plan" section: one paragraph describing what will be built, what level
   it will be pitched at, and which concepts it will focus on — based on phases 1 and 2.
   The user should correct anything wrong before confirming.

   Tell the user: "Review the agent's plan and fill in constraints. Run /whiteboard-ready when done."

---

### type: lesson-constraints

a. Read the "Context" section (phases 1 + 2 data).

b. Parse: time_budget_hours, language (if provided), constraints (list or empty).

c. Check if the user has written significant corrections to the agent's plan.
   If significant corrections and check-whiteboard.py exited 0 (round < 3):
     Overwrite WHITEBOARD.md (type: lesson-constraints round: N+1/3).
     Update the "Agent's plan" to reflect corrections.
     Tell the user: "Updated plan. Confirm it and run /whiteboard-ready when done."
     Stop.

d. If confirmed or check-whiteboard.py exited 1 (round cap):
   Determine lesson name: `<YYYY-MM>-<topic-slug>` (e.g. 2026-11-fastapi-basics).
   Create `lessons/<name>/` directory.
   Write `lessons/<name>/lesson.json` with all intake fields from phases 1–3,
   plus `status: in-progress` and `intake_phase: complete`.

   Run the scaffold sequence:
   - check-prereqs   (exit 1 → list what to install, stop)
   - scaffold        (exit 1 → stop)
   - install         (exit 1 → stop)
   - validate-lesson (exit 1 → stop)

   Delete `WHITEBOARD.md`.

   Say "Lesson ready. Edit src/, run check to self-verify."
