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
<!-- type: lesson-intake round: 1/3 -->
<!-- type: lesson-intake round: 2/3 -->
<!-- type: lesson-intake round: 3/3 -->
```

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

if type == lesson-intake:
  → check round number from header
    if round == 3: must proceed regardless of remaining gaps
  → if more info needed AND round < 3:
      a gap qualifies only if it blocks scaffolding:
        - scope too broad to pick a stack
        - language ambiguous and not inferable from user.json
      "would be nice to know" does not qualify
      overwrite WHITEBOARD.md (type: lesson-intake round: N+1/3)
      exit 0: "Updated whiteboard. Fill it in and run /whiteboard-ready again."
  → if satisfied OR round == 3:
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

writes:    WHITEBOARD.md  (type: lesson-intake round: 1)
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

### `check-profile`
```
reads:    user.json
exit 0:   file exists and passes schema validation
exit 1:   missing file, or lists which required fields are absent/invalid
```

### `check-prereqs`
```
reads:    stack.json  (required runtime + minimum version)
exit 0:   all runtimes present and meet minimum version
exit 1:   lists each missing or outdated runtime with the required version
```

### `scaffold`
```
reads:    templates/stacks/<stack>/stack.json
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
          stack.json   (install command)
runs:     install command inside lesson directory
exit 0:   dependencies installed
exit 1:   install failed (prints raw output)
```

### `check`
```
reads:    lesson.json  (stack name, lesson path)
          stack.json   (test command)
runs:     test command against lessons/<name>/tests/
exit 0:   all checks pass
exit 1:   test failures listed  (expected before tasks are complete — not an error state)
```

### `grade-tests`
```
reads:    lesson.json
          stack.json   (test command)
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
  └─ check-profile          (exit 1 → "Run /setup-profile first." stop)
  └─ writes WHITEBOARD.md   (type: lesson-intake round: 1)
     └─ user fills form
        └─ /whiteboard-ready
              └─ [0–2 follow-up rounds max: only if a blocking gap exists; hard cap at round 3/3]
              └─ check-prereqs   (exit 1 → list what to install, stop)
              └─ scaffold        (exit 1 → stop)
              └─ install         (exit 1 → stop)
              └─ validate-lesson (exit 1 → stop)
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
  └─ writes WHITEBOARD.md  (type: lesson-intake round: 1)
  └─ ... same as above from lesson intake onward
```
