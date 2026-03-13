# Week 2 – Action Item Extractor (FastAPI + SQLite + Ollama)

> Note: This `README.md` was generated from the Week 2 codebase by an AI assistant.

## Project overview

This project is a minimal FastAPI + SQLite web app that:

- Lets you **paste free-form notes** into a small frontend.
- Extracts **action items** from those notes using:
  - A **heuristic** extractor (`extract_action_items`)
  - An **LLM-backed** extractor via **Ollama** (`extract_action_items_llm`, model `llama3.1:8b`)
- Optionally **saves the input as a note** and persists extracted action items in SQLite.
- Lets you **mark action items done**.
- Lets you **list saved notes**.

Code lives primarily in:

- **Backend**: `week2/app/`
  - `main.py` (FastAPI app + lifespan + error handlers)
  - `routers/` (`notes.py`, `action_items.py`)
  - `services/extract.py` (heuristic + LLM extraction)
  - `db.py` (SQLite access)
  - `schemas.py` (Pydantic request/response models)
- **Frontend**: `week2/frontend/index.html`
- **Tests**: `week2/tests/`

## Setup

### Prerequisites

- **Python**: 3.10+
- A dependency manager:
  - Recommended: **uv** (because this repo has a `pyproject.toml`)
  - Alternatives: any environment where you can install the dependencies from `pyproject.toml`

### Install dependencies (recommended: uv)

From the repository root:

```bash
uv sync --all-groups
```

If you only want runtime deps (no tests/dev tools):

```bash
uv sync
```

### Ollama (for LLM extraction)

The `/action-items/extract-llm` endpoint requires:

- Ollama installed and running
- The model pulled locally:

```bash
ollama pull llama3.1:8b
```

If Ollama isn’t running or the model isn’t available, the LLM extractor may fail (the service has a small fallback, but you should run Ollama for intended behavior).

## Run the app

From the repository root:

```bash
uv run uvicorn week2.app.main:app --reload
```

Then open:

- `http://127.0.0.1:8000/`

Notes:

- The app serves the minimal frontend from `week2/frontend/index.html`.
- SQLite DB file is stored at `week2/data/app.db` (created automatically on startup).

## API endpoints

Base URL (local): `http://127.0.0.1:8000`

### UI + static

- **GET /**: Serves the HTML frontend.
- **GET /static/**: Static assets mounted from `week2/frontend/` (if referenced).

### Notes (`/notes`)

- **POST `/notes`**
  - **Purpose**: Create a saved note.
  - **Body** (`application/json`):

```json
{ "content": "meeting notes..." }
```

  - **Response**: `{ id, content, created_at }`

- **GET `/notes`**
  - **Purpose**: List all saved notes (newest first).
  - **Response**: `[{ id, content, created_at }, ...]`

- **GET `/notes/{note_id}`**
  - **Purpose**: Fetch a single note by id.
  - **Response**: `{ id, content, created_at }`

### Action items (`/action-items`)

- **POST `/action-items/extract`**
  - **Purpose**: Extract action items using the heuristic extractor.
  - **Body**:

```json
{ "text": "notes...", "save_note": true }
```

  - **Response**:
    - `note_id` is set if `save_note` is true
    - `items` are persisted action items with ids

```json
{
  "note_id": 123,
  "items": [{ "id": 1, "text": "Set up database" }]
}
```

- **POST `/action-items/extract-llm`**
  - **Purpose**: Extract action items using Ollama (`llama3.1:8b`).
  - **Body/Response**: Same shape as `/action-items/extract`.

- **GET `/action-items`**
  - **Purpose**: List action items, optionally filtered by note.
  - **Query params**:
    - `note_id` (optional): only action items for that note
  - **Response**:

```json
[
  { "id": 1, "note_id": 123, "text": "Set up database", "done": false, "created_at": "..." }
]
```

- **POST `/action-items/{action_item_id}/done`**
  - **Purpose**: Mark an action item done/undone.
  - **Body**:

```json
{ "done": true }
```

  - **Response**:

```json
{ "id": 1, "done": true }
```

## Error handling

- Database-layer errors are raised as `db.DatabaseError` / `db.NotFoundError`.
- The app installs global exception handlers in `week2/app/main.py` so common DB errors become consistent JSON responses:
  - **404**: `{ "detail": "..." }` for not found
  - **500**: `{ "detail": "database error" }` for DB failures

## Running the test suite

### With uv (recommended)

```bash
uv run pytest -q
```

### Without uv

Install dev dependencies (must include `pytest`), then:

```bash
python -m pytest -q
```

Notes:

- `week2/tests/test_extract.py` uses monkeypatching to mock the Ollama call, so tests run without requiring Ollama.

