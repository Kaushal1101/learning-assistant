# AI Sandbox Learning — Project Summary

## Vision and goals

A forkable repo that turns Claude Code into a hands-on trainer: name a tool or concept, get a generated sandbox codebase with focused tasks, complete them yourself, and get graded.

- **Learn by doing** in a real, runnable codebase rather than tutorials.
- **Any topic, generated on demand**, grounded by templates so output stays reliable.
- **No subscription:** users bring their own model and credits.
- **Cheap and transparent:** minimal token use, with cost per lesson visible to the user.
- **Just a repo:** no backend; users fork, learn, and push lessons to their own remote.

## How it works

The main agent generates and grades; the user does the learning.

1. User forks the repo and runs `/new-lesson` in Claude Code.
2. Agent writes an intake form to `WHITEBOARD.md`. User fills it in (topic, background, goals, constraints) and runs `/whiteboard-ready`. Agent reads the responses; if it needs more information it replaces the form with a follow-up and waits again. This repeats until the agent has enough context to proceed.
3. Agent checks prereqs and classifies the topic into a scope tier. Scripts scaffold the sandbox from a stack template; the agent writes topic-specific code and 3–6 tasks of rising difficulty.
4. Agent verifies the sandbox runs and tests fail before any work.
5. User completes tasks, running `check` to self-verify. Optional scoped tutors later.
6. `/grade` runs the grading tests, reviews the diff, and writes a scored report.
7. User tags and pushes their lesson.

## Repo and lesson structure

Upstream ships tooling and one sample lesson; each user's fork holds their own lessons.

```
.claude/
  skills/            # new-lesson, grade, whiteboard-ready (tutors later)
  settings.json      # shared permissions
CLAUDE.md            # repo map, global rules, scope tiers
FLOWS.md             # skill prerequisites, script contracts, full end-to-end flows
SCHEMAS.md           # annotated JSON schemas for user.json and lesson.json
WHITEBOARD.md        # transient intake form; gitignored, overwritten each round
scripts/             # core Python scripts (cross-platform)
templates/
  stacks/            # base scaffolds, each with stack.json (install/test/run commands)
  tasks/             # task patterns: fix-bug, add-feature, write-tests
  files/             # lesson README, TASKS.md, lesson.json schema
  rubric.md          # grading criteria
lessons/
  example-<topic>/   # one sample lesson
evals/               # maintainer-only eval harness
.gitignore           # deps, venvs, build output, WHITEBOARD.md
README.md            # fork, set upstream, start a lesson
```

Each lesson:

```
lessons/2026-11-fastapi-basics/
  lesson.json   # topic, level, tier, tasks + status, scores, usage, tags
  README.md     # setup + how to run checks
  TASKS.md      # goal, scope, done-criteria, doc links per task
  src/          # sandbox codebase
  tests/        # checks (visible to user)
  grading/      # grading tests and rubric (visible to user)
  REPORT.md     # written by grader
```

## Whiteboard

`WHITEBOARD.md` is a transient file at the repo root used as a structured intake form between the agent and user. It is gitignored and has no persistent state.

**Flow:**
1. Agent writes a form to `WHITEBOARD.md` with clearly labelled fields (e.g. tool name, prior experience, goals, constraints, time available).
2. User fills in the fields in their editor.
3. User runs `/whiteboard-ready` to signal completion.
4. Agent reads the file. If a blocking gap remains (scope too broad to pick a stack, language ambiguous and not inferable from profile), it may open a follow-up round. "Would be nice to know" does not qualify.
5. Hard cap of 3 rounds. On round 3, the agent proceeds with whatever it has.
6. Once satisfied (or at round 3), the agent clears `WHITEBOARD.md` and proceeds.

Each round replaces the previous form entirely. The agent stores extracted context in memory or `lesson.json`, not in the whiteboard itself.

## Skills and scripts

Skills handle judgment; shipped scripts handle everything deterministic, so no tokens are spent regenerating infrastructure.

| Skill | Does | Default model (to confirm via evals) |
| --- | --- | --- |
| setup-profile | Write profile whiteboard form | Haiku |
| update-profile | Re-write profile whiteboard pre-filled with existing values | Haiku |
| whiteboard-ready | Read `WHITEBOARD.md`, decide if more info is needed (write another form) or proceed (clear whiteboard, continue) | Sonnet |
| new-lesson | Kick off lesson intake: write first whiteboard form, then scaffold and generate tasks once intake is complete | Sonnet (Opus when no template fits) |
| grade | Run grading tests, review diff vs rubric, write REPORT.md | Sonnet |

Core scripts: `check-prereqs`, `scaffold`, `install`, `check`, `grade-tests`, `validate-lesson`. They read each stack's `stack.json`, so adding a stack means adding a folder.

When no stack fits, `new-lesson` builds one, validates it, and saves it to `templates/stacks/` for reuse. Good ones get PR'd upstream.

## Learning scope tiers

Scope is set by what a lesson needs from the user's machine, not by topic. v1 supports Tier 1 only.

| Tier | Needs | Examples | v1 |
| --- | --- | --- | --- |
| 1. Project-local | Supported runtime (Python 3.11+, Node 20+) + local packages; no sudo, daemons, accounts or cost; headless, deterministic tests | FastAPI, Express, React + Vitest, SQL on SQLite/DuckDB, pandas, TypeScript, Git | Yes |
| 2. System-level | Installed services or daemons, sensitive to local config | Docker, Postgres/Redis servers, Kubernetes, Playwright | Later (dev containers, PGlite) |
| 3. External | Cloud accounts, API keys, real cost, GUIs, hardware | AWS, Vercel, Stripe, mobile apps | Out |

`new-lesson` classifies each request first. Tier 2/3 requests get the nearest Tier 1 alternative, such as SQL on SQLite instead of Postgres, or Stripe logic against a local mock, clearly labeled as a mock.

## Git and lesson lifecycle

Users fork and keep all lessons committed in their fork.

- **Fork model:** upstream has no user lessons; users pull tooling updates with `git pull upstream`. Lessons live in their own folder, so there are no conflicts.
- **Commits per task:** the grader diffs exactly what changed for each task.
- **Naming:** date-prefixed folders, such as `2026-11-fastapi-basics`.
- **Hygiene:** strict `.gitignore` for dependencies and build output to keep forks small.

## Credits, models and eval harness

Spend tokens only on what is new, show users what each lesson cost, and pick models from measured results.

**Saving credits**

- Scripts for anything deterministic; the model only writes tasks and topic-specific code.
- Adapt templates instead of writing from scratch.
- Short skill files; load reference material on demand.
- Agents read `lesson.json` state instead of rereading code.

**Transparency:** each skill appends its token and cost usage to `lesson.json`. Users can also check `/cost`, `/context` and the status line in Claude Code.

**Model choice:** skills set a default model in frontmatter, which users can override. Defaults come from the eval harness.

**Eval harness (maintainer-only):** `evals/cases.json` holds 10–15 representative requests. `run_evals.py` runs each skill headless per model (`claude -p ... --model <m> --output-format json`), scores the result with `validate-lesson` and a reference solution, and logs pass rate, cost and time. Pick the cheapest model that clears the quality bar; re-run when skills change or new models ship.

## v1 scope and open decisions

v1 ships five core skills (`setup-profile`, `update-profile`, `whiteboard-ready`, `new-lesson`, `grade`), core scripts, 2–3 Tier 1 stack templates, one sample lesson and the eval harness.

**Out of scope for v1:** tutor skills, Tier 2/3 topics, dev containers, extending a lesson with new tasks, non-Claude agents.

**Open decisions**

- [ ] Rubric weighting, e.g. 60% tests / 40% AI code review, reported separately
- [ ] Which 2–3 stack templates ship first
- [x] `lesson.json` schema  (see SCHEMAS.md)
- [ ] Tutor scope rules, when tutors come in