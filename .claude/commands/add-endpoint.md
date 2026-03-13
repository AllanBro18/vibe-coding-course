# Add Endpoint Command

## Purpose

Scaffold a new API endpoint following TDD best practices: test → implement → validate.

## Syntax

```
/add-endpoint [OPTIONS]
```

### Options

- `--method METHOD` - HTTP method (GET, POST, PUT, DELETE; default: GET)
- `--path PATH` - URL path (e.g., `/notes/search`, `/action-items/{id}/complete`)
- `--router ROUTER` - Router file (notes or action_items; auto-detected from path)
- `--scaffold` - Generate skeleton code files (test + router implementation)

## Workflow

1. **Gather Requirements**
   - Method & path from user
   - What data is required (query params, request body, path params)
   - What the response should look like

2. **Scaffold Test File** (in `backend/tests/`)

   ```python
   # Example: test_get_notes_search
   def test_search_notes_case_insensitive(client):
       # Create test note
       # Query with search term
       # Assert correct results returned
   ```

3. **Scaffold Router Implementation** (in `backend/app/routers/`)

   ```python
   @router.get("/search")
   def search_notes(q: str):
       """Search notes by content (case-insensitive)."""
       # Implementation placeholder
       pass
   ```

4. **Scaffold Schema Updates** (if needed in `backend/app/schemas.py`)
   - Check if new request/response types needed
   - Auto-add to schemas file with TODO

5. **Verification Steps**
   ```bash
   cd week4
   make test                    # Run new test (will fail initially)
   # ... implement endpoint ...
   make test                    # Verify test passes
   make format && make lint     # Code quality
   /check-docs --compare        # Ensure docs will need update
   ```

## Example Usage

**Add search endpoint for notes:**

```
/add-endpoint --method GET --path "/notes/search" --router notes --scaffold
```

**Add complete endpoint for action items:**

```
/add-endpoint --method PUT --path "/action-items/{id}/complete" --router action_items --scaffold
```

**Add delete endpoint:**

```
/add-endpoint --method DELETE --path "/notes/{id}" --router notes --scaffold
```

## Expected Output

```
=== Adding Endpoint: GET /notes/search ===

Created files:
✓ backend/tests/test_notes.py - Added test_search_notes() function
✓ backend/app/routers/notes.py - Added search_notes() function

Next steps:
1. Review the test in backend/tests/test_notes.py (marked with TODO)
2. Implement the endpoint logic in backend/app/routers/notes.py
3. Run: make test (expect failure initially)
4. Implement until test passes
5. Run: make format && make lint
6. Run: /check-docs --compare to sync documentation

Test code to complete:
def test_search_notes_case_insensitive(client):
    # TODO: Implement test logic
    pass

Router code to complete:
@router.get("/search")
def search_notes(q: str):
    """Search notes by content (case-insensitive)."""
    # TODO: Implement query logic
    pass

Tips:
- Use SQLAlchemy filters: db.query(Note).filter(Note.content.ilike(f"%{q}%"))
- Return list of NoteResponse objects
- Add model to response schemas if needed
```

## Safety & Rollback

- **Non-destructive**: Creates new functions/tests (never overwrites existing code)
- **Marked with TODO**: All scaffold code clearly marked for implementation
- **Rollback**: If scaffold is wrong, `git checkout` the files and try again
- **No Breaking Changes**: New endpoints don't affect existing ones

## Implementation Notes

- Automatically detects router from path (e.g., `/notes/*` → `notes.py`)
- Generates type-safe Pydantic schemas from specifications
- Ensures test function names follow pytest conventions
- Scaffolded code includes docstrings and TODO comments
- All scaffolded paths include path parameters where applicable

## Integration with Workflows

Typical flow when adding features:

```
1. /add-endpoint --method GET --path "/notes/search" --scaffold
2. Implement test logic (make test - should fail)
3. Implement endpoint (make backend/app/routers/notes.py)
4. make test (should pass now)
5. make format && make lint
6. /check-docs --fix (auto-update documentation)
7. git commit -m "Add notes search endpoint"
```

This ensures:

- ✅ Test-first development
- ✅ Consistent code style
- ✅ Up-to-date documentation
- ✅ All tests passing before commit
