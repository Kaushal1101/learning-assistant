# FastAPI Sandbox

A minimal FastAPI scaffold. See `TASKS.md` for your lesson.

## Setup

```bash
pip install -e ".[dev]"
```

## Run

```bash
uvicorn src.app.main:app --reload
```

Then open http://127.0.0.1:8000/docs for the interactive API docs.

## Test

```bash
pytest
```
