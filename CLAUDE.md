# CLAUDE.md - Repository & Coding Guide

This document provides guidance for Claude (and developers) working with this codebase.

## Quick Start

1. **Activate environment**: `conda activate cs146s`
2. **Navigate to week4**: `cd week4`
3. **Install pre-commit hooks**: `pre-commit install`
4. **Run the app**: `make run` → http://localhost:8000
5. **Run tests**: `make test`
6. **Format/lint**: `make format` then `make lint`

## Project Structure

```
week4/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── models.py            # SQLAlchemy ORM models
│   │   ├── schemas.py           # Pydantic request/response schemas
│   │   ├── db.py                # Database connection & seeding
│   │   ├── routers/
│   │   │   ├── notes.py         # Notes CRUD endpoints
│   │   │   └── action_items.py  # Action items endpoints
│   │   └── services/
│   │       └── extract.py       # Text extraction logic (tags, etc.)
│   └── tests/
│       ├── conftest.py          # pytest fixtures
│       ├── test_notes.py
│       ├── test_action_items.py
│       └── test_extract.py
├── frontend/
│   ├── index.html               # Static HTML UI
│   └── app.js                   # Frontend JavaScript
├── data/
│   └── seed.sql                 # Initial database seed
├── docs/
│   ├── TASKS.md                 # Development tasks
│   └── API.md                   # API documentation (hand-maintained)
├── Makefile                     # Build/run commands
└── writeup.md                   # Assignment writeup

```

## Key Files & Patterns

### Models (backend/app/models.py)

- **Note**: Title, content, created/updated timestamps, tags extracted from content
- **ActionItem**: Description, priority, completed status, created/updated timestamps
- Both use SQLAlchemy ORM

### Schemas (backend/app/schemas.py)

- **NoteCreate/NoteUpdate**: Input validation for notes
- **NoteResponse**: Output format (includes extracted tags)
- **ActionItemCreate/ActionItemResponse**: Similar pattern for action items

### API Routes

- **Notes**: `GET /notes`, `POST /notes`, `GET /notes/{id}`, `GET /notes/search?q=...`, `PUT /notes/{id}`, `DELETE /notes/{id}`
- **Action Items**: `GET /action-items`, `POST /action-items`, `GET /action-items/{id}`, `PUT /action-items/{id}/complete`

### Database

- **Location**: `data/app.db` (SQLite, auto-created on startup)
- **Seeding**: `data/seed.sql` defines initial schema; applied once on app startup
- **Reset**: Delete `data/app.db` and restart app to re-seed

## Coding Standards

### Formatting & Linting

- **Formatter**: Black (line length: 88 chars)
- **Linter**: Ruff (replaces flake8, isort, etc.)
- **Pre-commit**: Install hooks with `pre-commit install`
- **Manual**: `make format` (black + ruff fix), `make lint` (ruff check)

**Golden Rule**: Always run `make format` → `make lint` before committing

### Testing

- **Framework**: pytest
- **Run**: `make test` or `PYTHONPATH=. pytest -q backend/tests`
- **Markers**: Can tag tests with `@pytest.mark.unit` or `@pytest.mark.integration`
- **Fixtures**: Defined in `backend/tests/conftest.py` (e.g., `client`, `db_session`)

### Test-Driven Development (TDD)

When adding new features:

1. Write failing test first (in appropriate test file)
2. Implement code to pass test
3. Run `make format && make lint && make test`
4. Commit with message explaining the feature

Example:

```python
# Test first (test_notes.py)
def test_notes_search_case_insensitive(client):
    # POST a note, then search with different case
    # Verify it's found

# Then implement
def search_notes(q: str):
    return db.query(Note).filter(Note.content.ilike(f"%{q}%")).all()
```

## Automation Commands

Use Claude's custom slash commands to streamline workflow:

### `/test-runner` - Run tests with better feedback

```
/test-runner                           # All tests with coverage
/test-runner --path backend/tests/test_notes.py  # Specific module
```

Gives: Pass/fail counts, failure names, suggested next steps

### `/check-docs` - Verify API docs match actual routes

```
/check-docs --compare                  # Compare docs vs. live API
/check-docs --generate                 # Update docs from OpenAPI
```

Gives: Drift report, missing endpoints, schema differences

## Common Tasks

### Adding a New Endpoint

1. **Define schema** in `backend/app/schemas.py`
2. **Write test** in appropriate `backend/tests/test_*.py`
3. **Implement** in appropriate `backend/app/routers/*.py`
4. **Run workflow**:
   ```bash
   make test
   make format && make lint
   /check-docs --compare  # Verify docs are up to date
   ```

### Debugging a Failing Test

1. **Run the specific test**: `/test-runner --path backend/tests/test_foo.py`
2. **Read error output** - see which assertion failed
3. **Check models/schemas** - ensure data types match
4. **Add print statements** or use pytest `-vv` flag for verbose output
5. **Re-run** to verify fix

### Understanding Extraction Logic

- Lives in `backend/app/services/extract.py`
- Currently extracts tags like `#tag` from note content
- Used when creating/updating notes to populate the `tags` field
- Tests in `backend/tests/test_extract.py`

## Safety & Rollback

### Safe Operations (Read-Only)

- ✅ Running tests: `make test`
- ✅ Reading schemas, routes, docs
- ✅ Using `/test-runner` or `/check-docs --compare`

### Reversible Operations (w/ Git)

- ⚠️ Editing routers, models, schemas (commit before testing major changes)
- ⚠️ Running `make format` (changes formatting, easily reverted: `git checkout .`)
- ⚠️ Updating `docs/API.md` (revert: `git checkout week4/docs/API.md`)

### Risky Operations (Confirm First)

- ❌ Deleting `data/app.db` (loses test data, but auto-recreates on restart)
- ❌ Modifying `data/seed.sql` without backing up
- ❌ Force-pushing branches (don't do this)

**Golden Rule**: Commit before trying anything experimental. Can always revert with `git reset --hard HEAD`.

## Git Workflow

```bash
# Before starting work
git pull origin main

# As you work
git add specific_files.py
git commit -m "Clear commit message"

# Before pushing
make test && make format && make lint

# Then push
git push origin feature-branch
```

Never use `--force` on shared branches.

## Debugging Commands

```bash
# Run app in debug mode
make run

# Check database (sqlite3)
sqlite3 data/app.db ".schema"

# View logs
PYTHONPATH=. python -c "from backend.app.db import engine; print(engine.url)"

# Reload seed
PYTHONPATH=. python -c "from backend.app.db import apply_seed_if_needed; apply_seed_if_needed()"
```

## Asking for Help

If you encounter issues:

1. **Check recent test output** - what test failed?
2. **Review error message** - what specifically went wrong?
3. **Check git status** - what files have changed?
4. **Ask me clearly** - include error traceback, which test/feature, what you tried

## Assignment Context

This week (Week 4) focuses on building automations that improve developer workflow. The automations in `.claude/commands/` and `CLAUDE.md` guidance are examples of how to streamline:

- ✅ Test execution and feedback
- ✅ Documentation maintenance
- ✅ Code quality checks
- ✅ Common refactoring tasks

See `week4/writeup.md` for details on all automations built.

---

**Last Updated**: 2026-03-12
**Environment**: conda cs146s, Python 3.9+, FastAPI, SQLAlchemy, pytest
