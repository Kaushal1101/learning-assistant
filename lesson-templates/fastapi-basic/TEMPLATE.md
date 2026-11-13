# fastapi-basic

Purpose:
Minimal FastAPI scaffold. General-purpose starting point for HTTP APIs, request/response validation, and web service lessons.

Use when:
- User wants to learn FastAPI, REST API design, or request validation
- Task involves routing, path/query params, Pydantic models, or status codes
- Lesson needs an HTTP surface but no database or UI

Avoid when:
- Task requires a database as a learning focus (use a persistence template)
- Task is CLI or scripting (use python-cli-basic)
- Task is primarily data analysis or background jobs

Structure:
- src/app/main.py: FastAPI app, Pydantic models, and route handlers in one place
- tests/test_main.py: pytest tests using FastAPI's TestClient (httpx under the hood)
- pyproject.toml: project metadata, runtime deps (fastapi, uvicorn), dev deps (pytest, httpx)

Already included:
- Three example endpoints:
  - GET /health → {"status": "ok"} (liveness probe pattern)
  - GET /hello?name=... → greeting with query param
  - POST /echo → Pydantic-validated request/response
- Pydantic v2 request/response models with field validation
- TestClient tests covering happy paths and 422 validation failures

Task patterns this template supports:
- fix-bug: wrong status code, broken validation, missing field in response, incorrect path
- add-feature: new endpoint, new query param, new Pydantic field, custom exception handler
- write-tests: untested endpoint, missing validation coverage, auth/headers

Scaffolding notes:
- main.py keeps models and routes together for simplicity; split into routers/schemas modules only if the generated task specifically targets that structure
- No database — add in-memory state only if the task needs it
- Example endpoints are illustrative and can be removed or replaced entirely by generated tasks
- Do not copy this TEMPLATE.md into the scaffolded lesson — it is agent context only
- Do copy template.yaml into the scaffolded lesson — install/check scripts read it
