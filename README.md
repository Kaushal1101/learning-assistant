# AI Sandbox Learning

A forkable repo that turns Claude Code into a hands-on trainer. Name a tool or concept, get a generated sandbox codebase with focused tasks, complete them yourself, and get graded.

## Prerequisites

- [Claude Code](https://claude.ai/code)
- Python 3.11+

## Getting started

**1. Fork and clone this repo**

**2. Open the repo in Claude Code and set up your profile**

```
/setup-profile
```

Fill in `WHITEBOARD.md` with your experience level, languages, and frameworks, then run:

```
/whiteboard-ready
```

Your profile is saved to `user.json`. Run `/update-profile` any time to update it.

**3. Start a lesson**

```
/new-lesson
```

Fill in the lesson intake form and run `/whiteboard-ready` again. The agent will scaffold a sandbox codebase with 3–6 tasks of rising difficulty.

**4. Work through the tasks**

Edit files in `lessons/<name>/src/`. Run the check script any time to self-verify:

```
python scripts/check.py
```

**5. Grade your work**

```
/grade
```

Results are written to `lessons/<name>/REPORT.md`.

## Commands

| Command | What it does |
|---|---|
| `/setup-profile` | First-time profile setup |
| `/update-profile` | Update your existing profile |
| `/whiteboard-ready` | Submit a filled whiteboard form |
| `/new-lesson` | Start a new lesson |
| `/grade` | Grade your current lesson |

## Repo layout

```
.claude/skills/     # Claude Code commands
scripts/            # Deterministic helper scripts
templates/          # Whiteboard forms and stack scaffolds
lessons/            # Your lessons (created at runtime, not committed upstream)
```

## Docs

- [`FLOWS.md`](FLOWS.md) — command prerequisites, script contracts, end-to-end flows
- [`SCHEMAS.md`](SCHEMAS.md) — JSON schemas for `user.json` and `lesson.json`

## Running tests

```
python -m pytest tests/
```
