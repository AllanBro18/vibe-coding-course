# Check Docs Command

## Purpose

Verify that API documentation stays in sync with actual FastAPI routes, detecting drift early.

## Syntax

```
/check-docs [OPTIONS]
```

### Options

- `--generate` - Generate/update `week4/docs/API.md` from OpenAPI schema
- `--compare` - Compare existing docs against live schema and report differences
- `--fix` - Automatically fix documentation to match OpenAPI spec

## Workflow

1. **Fetch OpenAPI Schema**: Get live schema from running app or read from file

   ```bash
   cd week4
   curl -s http://localhost:8000/openapi.json > /tmp/openapi.json
   ```

   Or read cached schema if app isn't running

2. **Parse OpenAPI**: Extract routes, methods, query parameters, request/response schemas

3. **Compare Against Docs**: Check if `week4/docs/API.md` matches the parsed schema
   - Missing endpoints
   - Incorrect parameter types
   - Removed endpoints
   - Schema mismatches

4. **Generate Report**:

   ```
   ✓ GET /notes - Documented correctly
   ✓ GET /notes/{id} - Documented correctly
   ✗ GET /notes/search - MISSING from docs
   ✗ PUT /notes/{id} - Added but not yet documented
   ⚠ POST /action-items - Parameters differ (schema update needed)
   ```

5. **Optional Auto-Fix**: Update `API.md` with correct endpoints and parameters

## Example Usage

**Check current docs vs. actual API:**

```
/check-docs --compare
```

**Generate fresh API docs from schema:**

```
/check-docs --generate
```

**Fix docs automatically:**

```
/check-docs --fix
```

## Expected Output

```
=== API Documentation Check ===

Found 8 endpoints in OpenAPI schema
Found 6 endpoints in docs/API.md

Drift Report:
✓ GET /notes (200 response)
✓ POST /notes (201 response)
✓ GET /notes/{id} (200 response)
✗ GET /notes/search - MISSING from docs
✓ PUT /action-items/{id}/complete (200 response)
⚠ DELETE /notes/{id} - Schema differs from docs

Total: 1 missing, 1 differs

Action Items:
1. Add GET /notes/search endpoint to docs/API.md
2. Review DELETE /notes/{id} schema in docs
3. Run: /check-docs --fix to auto-correct

Last checked: 2026-03-12T10:30:00Z
```

## Safety & Rollback

- **Idempotent**: Multiple runs produce same analysis
- **Comparison mode** (`--compare`): Read-only, no changes
- **Generation mode** (`--generate`): Creates/overwrites `docs/API.md`, can be reverted via git
- **Rollback**: `git checkout week4/docs/API.md` if unwanted changes

## Implementation Notes

- Reads `/openapi.json` endpoint from running FastAPI app
- Parses JSON schema into structured endpoint list
- Compares against hand-written `docs/API.md`
- Can work offline if OpenAPI file is cached
- Suggests specific sections that need updating

## Integration with Workflows

Common pattern after adding new endpoints:

1. Implement endpoint in backend router
2. Run tests to verify: `/test-runner`
3. Check documentation drift: `/check-docs --compare`
4. Auto-update docs: `/check-docs --fix` (or manually edit)
5. Commit changes
