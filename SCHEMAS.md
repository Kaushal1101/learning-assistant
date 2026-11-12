# JSON Schemas

Annotated examples for every persisted JSON file. Fields are grouped by which stage writes them.

---

## `user.json`

Written by `/whiteboard-ready` after profile intake. Stored at repo root.

```json
{
  "experience_level": "junior",        // "junior" | "mid" | "senior"
  "languages": ["python", "typescript"],
  "frameworks": ["fastapi", "react"],
  "updated_at": "2026-11-12"           // ISO date, set on every write
}
```

**Required fields:** all. `check-profile` exits 1 if any are missing or invalid.

---

## `lesson.json`

Stored at `lessons/<name>/lesson.json`. Built up in stages.

### Stage 1a — written by `/whiteboard-ready` after phase 1 (lesson-intro)

```json
{
  "topic": "FastAPI",
  "scope": "routing and dependency injection",
  "goal": "build a small REST API from scratch",
  "tool_experience": "none",           // "none" | "heard-of" | "used-a-little" | "comfortable"
  "intake_phase": "diagnostic"         // tracks which intake phase comes next
}
```

### Stage 1b — updated by `/whiteboard-ready` after phase 2 (lesson-diagnostic)

```json
{
  "intake_phase": "constraints",
  "diagnostic_notes": "User knows Python well but hasn't used type hints or decorators extensively. No prior FastAPI or Starlette experience."
}
```

### Stage 1c — updated by `/whiteboard-ready` after phase 3 (lesson-constraints)

```json
{
  "intake_phase": "complete",
  "time_budget_hours": 2,
  "language": "python",                // only set when explicitly provided or ambiguous
  "constraints": ["no async", "keep examples simple"]
}
```

### Stage 2 — added by `scaffold`

```json
{
  "name": "2026-11-fastapi-basics",
  "tier": 1,
  "stack": "fastapi-python",
  "status": "in-progress",            // "in-progress" | "complete"
  "created_at": "2026-11-12",
  "tasks": [
    {
      "id": "task-1",
      "title": "Add a GET /items endpoint",
      "status": "not-started",         // "not-started" | "complete"
      "score": null                    // null until graded
    },
    {
      "id": "task-2",
      "title": "Add path parameters",
      "status": "not-started",
      "score": null
    }
  ]
}
```

### Stage 3 — added by `/grade`

```json
{
  "status": "complete",
  "scores": {
    "tests": 80,                       // % of grading tests passing
    "review": 70,                      // AI code review score
    "total": 76                        // weighted aggregate
  },
  "graded_at": "2026-11-12"
}
```

### Stage 4 — appended by each command run (usage tracking)

```json
{
  "usage": [
    {
      "command": "new-lesson",
      "model": "claude-sonnet-4-6",
      "input_tokens": 1200,
      "output_tokens": 800,
      "cost_usd": 0.012,
      "timestamp": "2026-11-12T10:00:00Z"
    },
    {
      "command": "grade",
      "model": "claude-sonnet-4-6",
      "input_tokens": 2100,
      "output_tokens": 950,
      "cost_usd": 0.019,
      "timestamp": "2026-11-12T11:30:00Z"
    }
  ]
}
```

---

## Full `lesson.json` example (all stages merged)

```json
{
  "name": "2026-11-fastapi-basics",
  "topic": "FastAPI",
  "scope": "routing and dependency injection",
  "goal": "build a small REST API from scratch",
  "tool_experience": "none",
  "diagnostic_notes": "User knows Python well but hasn't used type hints or decorators extensively. No prior FastAPI or Starlette experience.",
  "time_budget_hours": 2,
  "language": "python",
  "constraints": ["no async", "keep examples simple"],
  "intake_phase": "complete",
  "tier": 1,
  "stack": "fastapi-python",
  "status": "complete",
  "created_at": "2026-11-12",
  "graded_at": "2026-11-12",
  "tasks": [
    { "id": "task-1", "title": "Add a GET /items endpoint", "status": "complete", "score": 100 },
    { "id": "task-2", "title": "Add path parameters",       "status": "complete", "score": 80  },
    { "id": "task-3", "title": "Add request body with Pydantic", "status": "complete", "score": 60 }
  ],
  "scores": {
    "tests": 80,
    "review": 70,
    "total": 76
  },
  "usage": [
    { "command": "new-lesson", "model": "claude-sonnet-4-6", "input_tokens": 1200, "output_tokens": 800,  "cost_usd": 0.012, "timestamp": "2026-11-12T10:00:00Z" },
    { "command": "grade",      "model": "claude-sonnet-4-6", "input_tokens": 2100, "output_tokens": 950,  "cost_usd": 0.019, "timestamp": "2026-11-12T11:30:00Z" }
  ]
}
```
