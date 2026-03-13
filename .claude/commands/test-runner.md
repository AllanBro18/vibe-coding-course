# Test Runner Command

## Purpose

Automate running pytest with intelligent feedback, including coverage analysis and failure summaries.

## Syntax

```
/test-runner [OPTIONS]
```

### Options

- `--marker MARKER` - Run tests with a specific pytest marker
- `--path PATH` - Run tests in a specific path (default: backend/tests)
- `--coverage` - Include coverage report (default: true)
- `--failfast` - Stop on first failure (default: true)

## Workflow

1. **Run Tests**: Execute pytest with the specified options

   ```bash
   cd week4
   PYTHONPATH=. pytest -q ${{ paths }} --maxfail=1 -x ${{ marker }}
   ```

2. **Analyze Output**: Parse failures and provide actionable feedback
   - Summary of passed/failed tests
   - Names of failed tests with file paths
   - Suggested next steps

3. **Coverage Report** (if requested):
   ```bash
   PYTHONPATH=. pytest --cov=backend/app --cov-report=term-missing ${{ paths }}
   ```

## Example Usage

**Run all tests with coverage:**

```
/test-runner --coverage
```

**Run tests for a specific module:**

```
/test-runner --path backend/tests/test_notes.py
```

**Run action-item tests with coverage:**

```
/test-runner --path backend/tests/test_action_items.py --coverage
```

## Expected Output

```
✓ backend/tests/test_notes.py::test_get_notes PASSED
✓ backend/tests/test_action_items.py::test_create_action_item PASSED
✗ backend/tests/test_extract.py::test_extract_tags FAILED
  Error: AssertionError: expected ['tag1', 'tag2'] but got []

Failed Tests: 1 out of 10
Suggested next steps:
- Review extract.py parse_tags() implementation
- Ensure regex pattern matches #tag format
- Run: /test-runner --path backend/tests/test_extract.py for details
```

## Safety & Rollback

- **Idempotent**: Running tests multiple times yields same results
- **Read-only**: No code is modified
- **Rollback**: Not applicable (read-only operation)

## Implementation Notes

- Uses pytest `-x` flag to stop on first failure (quick feedback)
- Captures both stdout and stderr for completeness
- Suggests file locations and next debugging steps
- Works from `week4/` directory context
