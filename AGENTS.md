# AGENTS.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Overview

Course assignments repo for CS146S: The Modern Software Developer (Stanford). Each `weekN/` directory is an independent assignment. Python 3.10+, managed with **uv**.

## Environment Setup

```powershell
uv sync          # install all dependencies (runtime + dev)
```

The virtual environment lives in `.venv/` at the repo root. Use `uv run` to execute commands within it.

## Common Commands

### Weeks 4–7 (FastAPI apps with Makefiles)

These weeks share identical Makefile targets. **Must run from inside the week directory** (e.g. `cd week4`):

```
make run       # Start FastAPI dev server (uvicorn, --reload, port 8000)
make test      # Run pytest (PYTHONPATH=. pytest -q backend/tests)
make format    # Black + ruff --fix
make lint      # ruff check
make seed      # Apply DB seed if needed
```

To run a single test file: `PYTHONPATH=. pytest -q backend/tests/test_notes.py` (from the week directory).

To run a single test function: `PYTHONPATH=. pytest -q backend/tests/test_notes.py::test_function_name`.

### Week 2 (FastAPI app, no Makefile)

```
uv run uvicorn week2.app.main:app --reload     # run app
uv run pytest -q week2/tests/                   # run tests
```

### Week 3 (MCP server)

Requires `OMDB_API_KEY` env var.

```
uv run python -m week3.server.main              # run MCP STDIO server
uv run pytest week3/server/test_movie_api.py     # run tests
```

### Week 1 (standalone scripts)

Each `.py` file is a self-contained prompting exercise. Run individually with `uv run python week1/<script>.py`.

### Formatting & Linting (repo-wide)

```
uv run black .
uv run ruff check . --fix    # auto-fix
uv run ruff check .          # check only
```

Config in `pyproject.toml`: Black line-length 100, Ruff rules `E, F, I, UP, B` (ignores `E501`, `B008`).

Always run format then lint before committing.

## Architecture

### Shared Pattern (Weeks 2, 4–7)

These weeks follow the same FastAPI + SQLite architecture:

- **`backend/app/main.py`** — FastAPI app entry point, mounts routers and static files
- **`backend/app/models.py`** — SQLAlchemy ORM models (Note, ActionItem)
- **`backend/app/schemas.py`** — Pydantic request/response validation
- **`backend/app/db.py`** — Database engine, session management, seed logic
- **`backend/app/routers/`** — Route handlers (notes.py, action_items.py)
- **`backend/app/services/`** — Business logic (e.g. text extraction)
- **`backend/tests/`** — pytest tests with fixtures in `conftest.py`
- **`frontend/`** — Static HTML/JS served by FastAPI (no build step)
- **`data/seed.sql`** — Initial DB schema; applied once on startup
- **`data/app.db`** — SQLite DB (auto-created, gitignored). Delete and restart to reset.

Week 2 differs slightly: uses `week2/app/` instead of `backend/app/`, and includes an Ollama-based LLM extractor (`services/extract.py`) alongside the heuristic one.

Week 7 extends the base pattern with timestamps, pagination/sorting, and PATCH endpoints.

### Week 3 (MCP Server)

Standalone MCP STDIO server wrapping the OMDb movie API. Uses `FastMCP` from the `mcp` SDK. Key files:
- `server/movie_api.py` — async OMDb HTTP client
- `server/main.py` — MCP tool/resource definitions and server entrypoint

Logs to stderr only (stdout reserved for MCP protocol).

## Testing

- Framework: **pytest**
- Week 2 tests mock Ollama calls via monkeypatching (no Ollama needed to run tests)
- Weeks 4–7 use a test client fixture from `conftest.py` (`client`, `db_session`)
- Test markers available: `@pytest.mark.unit`, `@pytest.mark.integration`

## Key Dependencies

Runtime: FastAPI, uvicorn, SQLAlchemy, Pydantic, httpx, openai, ollama, mcp, hypercorn
Dev: pytest, black, ruff, pre-commit

## Adding a New Endpoint (Weeks 4–7)

1. Define schema in `schemas.py`
2. Write test in `backend/tests/test_*.py`
3. Implement route in `backend/app/routers/*.py`
4. Run: `make test && make format && make lint`
