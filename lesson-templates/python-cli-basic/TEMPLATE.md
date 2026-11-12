# python-cli-basic

Purpose:
Minimal Python CLI application scaffold. General-purpose starting point for scripts, text processing, file utilities, and command-line tools.

Use when:
- User wants to learn Python scripting fundamentals
- Task involves argparse, subcommands, file I/O, or standard I/O
- Lesson doesn't need a web server, database, or UI

Avoid when:
- Task requires HTTP endpoints (use a web template instead)
- Task is primarily data analysis (use a pandas template instead)
- Task requires async concurrency as a learning focus

Structure:
- src/app/main.py: argparse entrypoint + business logic in one place
- tests/test_main.py: pytest tests for both CLI and logic
- pyproject.toml: project metadata, dev dependencies (pytest), and pytest path config

Already included:
- argparse CLI with one example subcommand (`hello <name> [--loud]`)
- Pytest configured with src/ on the path
- Minimal README for the sandbox user

Task patterns this template supports:
- fix-bug: broken parser, wrong exit code, missing validation, off-by-one in logic
- add-feature: new subcommand, new flag, new output format, read from stdin, write to file
- write-tests: untested command, edge cases in parsing, error paths

Scaffolding notes:
- main.py keeps parsing and logic together for simplicity; split into separate files only if the generated task specifically targets that separation
- Use explicit exit codes (0 for success, 1 for business errors, 2 for parsing errors — argparse handles 2 by default)
- The `hello` command is illustrative and can be removed or replaced entirely by generated tasks
- Do not copy this TEMPLATE.md into the scaffolded lesson — it is agent context only
- Do copy template.yaml into the scaffolded lesson — install/check scripts read it
