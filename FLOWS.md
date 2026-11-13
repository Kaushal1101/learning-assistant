# Deterministic Flows and Dependencies

Every command has explicit gate conditions. If a gate fails, the command prints a clear error and exits — it never tries to recover inline. Scripts are the gatekeepers; commands are callers.

---

## System state

Two files determine what phase the system is in. Commands read these before acting; nothing is inferred from conversation context.

| File | Meaning |
|------|---------|
| `user.json` absent | Profile not set up — `/new-lesson` cannot proceed |
| `user.json` present | Profile ready |
| `WHITEBOARD.md` absent | No pending intake |
| `WHITEBOARD.md` present | Waiting for user to fill in and run `/whiteboard-ready` |
| `lessons/<name>/lesson.json` absent | No active lesson |
| `lessons/<name>/lesson.json` `status: in-progress` | Lesson active |
| `lessons/<name>/lesson.json` `status: complete` | Lesson graded |

---

## Whiteboard type header

Every form the agent writes to `WHITEBOARD.md` begins with a machine-readable comment on line 1. `/whiteboard-ready` reads this to know its phase — no inference from other state.

```
<!-- type: profile -->
<!-- type: lesson-intro round: 1/3 -->
<!-- type: lesson-diagnostic round: 1/3 -->
<!-- type: lesson-constraints round: 1/3 -->
```

Each form after phase 1 includes a "Context from previous phases (do not edit)" section written by the agent. This carries forward all accumulated data so `/whiteboard-ready` has full context from the file alone — no external state is needed during intake.

---

## Commands

### `/setup-profile`
```
requires:  nothing
writes:    WHITEBOARD.md  (type: profile)
exits:     "Fill in WHITEBOARD.md and run /whiteboard-ready when done."
```

### `/whiteboard-ready`
```
requires:  WHITEBOARD.md exists
           exit 1 if absent: "No whiteboard found. Nothing to submit."

reads:     line 1 of WHITEBOARD.md for type

if type == profile:
  → validate all required fields present
    exit 1 if any missing: list missing fields, leave WHITEBOARD.md intact
  → write user.json  (overwrites if already exists)
  → delete WHITEBOARD.md
  → exit 0: "Profile saved. Run /new-lesson to start a lesson."  (or "Profile updated." if user.json existed)

if type == lesson-intro:
  → parse: topic, scope, goal, tool_experience
  → validate all four fields present; scope must not just repeat the tool name
    if invalid and round < 3: list problems, leave WHITEBOARD.md intact, stop
    if invalid and round == 3: use best available values and proceed
  → write WHITEBOARD.md (type: lesson-diagnostic round: 1/3):
      section 1: "Context from phase 1 (do not edit)" — parsed intro values
      section 2: 2–3 diagnostic questions targeting prerequisite concepts
        chosen from user.json languages/frameworks that the lesson will actually require
        focus on depth, not breadth — e.g. decorators, type hints for a FastAPI lesson
        do NOT ask about the target tool if tool_experience is "none"
  → exit 0: "Fill in WHITEBOARD.md and run /whiteboard-ready when done."

if type == lesson-diagnostic:
  → read "Context from phase 1" section
  → read user's answers to diagnostic questions
  → assess whether answers are specific enough to calibrate lesson difficulty
    if vague and round < 3:
      overwrite WHITEBOARD.md (type: lesson-diagnostic round: N+1/3)
        preserve "Context from phase 1" section
        write 1–2 sharper follow-up questions
      exit 0: "Updated whiteboard. Fill it in and run /whiteboard-ready again."
  → if satisfied or round == 3:
      write diagnostic_notes: one-paragraph summary of user's actual knowledge level
      write WHITEBOARD.md (type: lesson-constraints round: 1/3):
        section 1: "Context (do not edit)" — phase 1 values + diagnostic_notes
        section 2: user-fillable fields: time_budget_hours, language (if ambiguous), hard constraints
        section 3: "Agent's plan" — one paragraph the user can correct:
          what will be built, what level it will be pitched at, which concepts it will focus on
  → exit 0: "Review the agent's plan and fill in constraints. Run /whiteboard-ready when done."

if type == lesson-constraints:
  → read "Context" section (phases 1 + 2 data)
  → parse: time_budget_hours, language, constraints
  → check if user has corrected the agent's plan significantly
    if significant corrections and round < 3:
      overwrite WHITEBOARD.md (type: lesson-constraints round: N+1/3)
        update "Agent's plan" to reflect corrections, ask user to confirm
      exit 0: "Updated plan. Confirm it and run /whiteboard-ready again."
  → if confirmed or round == 3:
      write lessons/<name>/lesson.json  (name = <date>-<topic-slug>, all intake fields, status: in-progress)
      run check-prereqs   (exit 1 → stop, print what to install)
      run scaffold        (exit 1 → stop)
      run install         (exit 1 → stop)
      run validate-lesson (exit 1 → stop)
      delete WHITEBOARD.md
      exit 0: "Lesson ready. Edit src/, run check to self-verify."
```

### `/update-profile`
```
requires:  user.json
           runs check-profile
           exit 1 if fails: "No profile found. Run /setup-profile first."

writes:    WHITEBOARD.md  (type: profile, fields pre-filled from user.json)
exits:     "Edit any fields in WHITEBOARD.md and run /whiteboard-ready when done."
```

### `/new-lesson`
```
requires:  user.json
           runs check-profile
           exit 1 if fails: "Run /setup-profile first."
           WHITEBOARD.md must not already exist
           exit 1 if present: "A whiteboard is already open. Run /whiteboard-ready to continue."

writes:    WHITEBOARD.md  (type: lesson-intro round: 1/3)  from templates/whiteboard/lesson-intro.md
exits:     "Fill in WHITEBOARD.md and run /whiteboard-ready when done."
```

### `/grade`
```
requires:  lesson.json with status=in-progress
           exit 1 if absent or wrong status: "No active lesson to grade."

runs:      grade-tests
writes:    REPORT.md
updates:   lesson.json  status → complete
exits:     "Grading complete. See REPORT.md."
```

---

## Scripts

All scripts print a human-readable reason on exit 1.

### `check-whiteboard`
```
reads:    WHITEBOARD.md  line 1 (type header) + section contents
exit 0:   fields valid, round < 3 — follow-up permitted
exit 1:   round == 3 — hard cap hit, must proceed regardless
exit 2:   missing/unfilled fields (listed), or invalid header — leave whiteboard intact

field checks by type:
  lesson-intro:       topic, scope, goal, tool_experience all non-empty
  lesson-diagnostic:  every non-context section has at least one answer line
  lesson-constraints: Time budget section contains a number
  profile:            exits 0 (validation delegated to check-profile)
```

### `check-profile`
```
reads:    user.json
exit 0:   file exists and passes schema validation
exit 1:   missing file, or lists which required fields are absent/invalid
```

### `check-prereqs`
```
reads:    template.yaml  (required runtime + minimum version)
exit 0:   all runtimes present and meet minimum version
exit 1:   lists each missing or outdated runtime with the required version
```

### `scaffold`
```
reads:    templates/stacks/<stack>/template.yaml
          user.json
          lesson intake data (passed as args or from temp file)
writes:   lessons/<name>/src/
          lessons/<name>/tests/
          lessons/<name>/grading/
          lessons/<name>/lesson.json   (status: in-progress)
          lessons/<name>/README.md
          lessons/<name>/TASKS.md
exit 0:   scaffold written and validate-lesson passes
exit 1:   stack not found, or validate-lesson fails (lists reason)
```

### `install`
```
reads:    lesson.json  (stack name, lesson path)
          template.yaml   (install command)
runs:     install command inside lesson directory
exit 0:   dependencies installed
exit 1:   install failed (prints raw output)
```

### `check`
```
reads:    lesson.json  (stack name, lesson path)
          template.yaml   (test command)
runs:     test command against lessons/<name>/tests/
exit 0:   all checks pass
exit 1:   test failures listed  (expected before tasks are complete — not an error state)
```

### `grade-tests`
```
reads:    lesson.json
          template.yaml   (test command)
runs:     test command against lessons/<name>/grading/
writes:   results to stdout  (caller /grade writes REPORT.md)
exit 0:   all grading tests pass
exit 1:   failures with details
```

### `validate-lesson`
```
reads:    lessons/<name>/  directory structure
checks:   required files exist (lesson.json, README.md, TASKS.md, src/, tests/, grading/)
          lesson.json passes schema
          tests/ and grading/ are non-empty
exit 0:   valid
exit 1:   lists each missing or invalid item
```

---

## Full flows

### First-time user

```
/setup-profile
  └─ writes WHITEBOARD.md  (type: profile)
     └─ user fills form
        └─ /whiteboard-ready
              └─ validate fields  (exit 1 → leave whiteboard, tell user what's missing)
              └─ write user.json
              └─ delete WHITEBOARD.md
              └─ "Run /new-lesson to start a lesson."

/new-lesson
  └─ check-profile                      (exit 1 → "Run /setup-profile first." stop)
  └─ writes WHITEBOARD.md               (type: lesson-intro round: 1/3)

  Phase 1 — Basic intro (max 3 rounds)
     └─ user fills form
        └─ /whiteboard-ready
              └─ [follow-up if fields missing; hard cap round 3/3]
              └─ writes WHITEBOARD.md   (type: lesson-diagnostic round: 1/3)
                                         with phase 1 context + 2–3 diagnostic questions

  Phase 2 — Tool diagnostic (max 3 rounds)
     └─ user fills form
        └─ /whiteboard-ready
              └─ [follow-up if answers vague; hard cap round 3/3]
              └─ writes WHITEBOARD.md   (type: lesson-constraints round: 1/3)
                                         with context + constraints fields + agent's plan

  Phase 3 — Constraints and review (max 3 rounds)
     └─ user fills form + confirms or corrects agent's plan
        └─ /whiteboard-ready
              └─ [follow-up if plan corrected significantly; hard cap round 3/3]
              └─ writes lessons/<name>/lesson.json
              └─ check-prereqs          (exit 1 → list what to install, stop)
              └─ scaffold               (exit 1 → stop)
              └─ install                (exit 1 → stop)
              └─ validate-lesson        (exit 1 → stop)
              └─ delete WHITEBOARD.md
              └─ "Lesson ready."

user works on lesson...
  └─ check  (run anytime; exit 1 = tasks not done yet, expected)

/grade
  └─ grade-tests
  └─ write REPORT.md
  └─ lesson.json status → complete
```

### Returning user (profile already exists)

```
/new-lesson
  └─ check-profile  (exit 0 → continue)
  └─ writes WHITEBOARD.md  (type: lesson-intro round: 1/3)
  └─ ... same three-phase intake as above
```
