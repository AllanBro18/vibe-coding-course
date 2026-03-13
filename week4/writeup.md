# Week 4 Write-up

Tip: To preview this markdown file

- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **Allan** \
SUNet ID: **N/A** \
Citations:

- Anthropic Claude Code best practices: https://www.anthropic.com/engineering/claude-code-best-practices
- Claude Code SubAgents overview: https://docs.anthropic.com/en/docs/claude-code/sub-agents

This assignment took me about **3** hours to do.

## YOUR RESPONSES

### Automation #1

a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)

> Inspired by Claude Code best practices on **repository guidance** and **developer workflow optimization**. Created a root-level `CLAUDE.md` file that serves as a comprehensive reference for developers (human and AI) interacting with this codebase. This follows the pattern described in the best-practices guide where CLAUDE.md acts as an executable prompt, providing context about structure, conventions, and safe operations.

b. Design of each automation, including goals, inputs/outputs, steps

> **Goal**: Provide centralized, always-available guidance that helps Claude and human developers understand code structure, conventions, and safe workflows.
>
> **Location**: `CLAUDE.md` at repository root
>
> **Inputs**: Loaded automatically when Claude Code sessions start
>
> **Outputs**:
>
> - Project structure map
> - Key file locations and patterns
> - Coding standards (black, ruff, pytest)
> - Common workflows (TDD pattern, debugging)
> - Safe vs. risky operations
> - Custom automation command reference
>
> **Steps**:
>
> 1. Document project structure with dir tree and file purposes
> 2. List key patterns (models, schemas, routers, tests)
> 3. Define coding standards (formatting, linting, testing)
> 4. Provide step-by-step workflows for common tasks
> 5. Classify operations by safety level (safe, reversible, risky)
> 6. Reference custom automations for streamlined workflows

c. How to run it (exact commands), expected outputs, and rollback/safety notes

> **How to Enable**: Automatically loaded by Claude Code at session start. No commands needed. File located at:
>
> ```
> c:/Users/allan/OneDrive/Documents/Coding/ppkpl/modern-software-dev-assignments/CLAUDE.md
> ```
>
> **Expected Output**: Enhanced Claude responses that:
>
> - Provide accurate file paths for edits
> - Suggest correct make/pytest commands
> - Follow project coding standards
> - Recommend TDD workflows
> - Warn about risky operations
>
> **Validation**: Check that Claude references `CLAUDE.md` guidance when working on the codebase (e.g., suggests `make format && make lint` workflow)
>
> **Rollback**: Safe to remove (file is guidance-only, doesn't affect code). Delete if outdated: `git rm CLAUDE.md`

d. Before vs. after (i.e. manual workflow vs. automated workflow)

> **Before**: Developers must manually remember/discover:
>
> - Where routers live (backend/app/routers/)
> - Command to run tests (make test vs. pytest vs. python -m pytest)
> - Pre-commit hook setup and formatting requirements
> - TDD pattern for this specific codebase (write test → implement → lint)
> - Which operations are safe (running tests) vs. risky (force-pushing)
> - How to reset database, view seed.sql, etc.
>
> **After**:
>
> - CLAUDE.md is consulted automatically at session start
> - Claude provides accurate, context-aware guidance without user interruption
> - New developers (and AI assistants) have a single source of truth
> - Fewer mistakes due to outdated or incorrect commands
> - Consistent workflow enforcement (always format → lint → test)

e. How you used the automation to enhance the starter application

> Created `CLAUDE.md` as the foundation for all subsequent automations and enhancements. This automation directly enabled:
>
> 1. **Accurate guidance for API.md creation**: CLAUDE.md specified docs location as `week4/docs/` and format expectations
> 2. **Correct test workflows**: When adding tests or debugging, CLAUDE.md provided exact pytest syntax and fixture patterns
> 3. **Safe endpoint additions**: CLAUDE.md outlined the TDD pattern (test first, then implement) used throughout development
> 4. **Pre-commit integration**: Documented `make format && make lint` pattern, ensuring code quality before commits
>
> The CLAUDE.md serves as the "memory system" that allows subsequent automations (/test-runner, /check-docs) to work cohesively within the project's conventions.

### Automation #2

a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)

> Inspired by Claude Code best practices on **custom slash commands** and **developer experience**. The `/test-runner` command automates pytest execution with intelligent feedback, reducing friction in the test-debug cycle. This directly addresses the practice of "keeping tests green" and providing clear feedback for CI/CD-like workflows without leaving Claude.

b. Design of each automation, including goals, inputs/outputs, steps

> **Goal**: Streamline test execution with clear pass/fail feedback and suggestion of next debugging steps.
>
> **Location**: `.claude/commands/test-runner.md`
>
> **Inputs**: Optional flags:
>
> - `--marker MARKER`: Run tests matching pytest marker
> - `--path PATH`: Run tests in specific directory (default: backend/tests)
> - `--coverage`: Include coverage report (default: true)
> - `--failfast`: Stop at first failure (default: true)
>
> **Outputs**:
>
> - Count of passed/failed tests
> - Names and locations of failed tests
> - Coverage percentages (if requested)
> - Suggested next steps (e.g., "check extract.py parse_tags() implementation")
>
> **Steps**:
>
> 1. Parse command arguments (path, markers, flags)
> 2. Execute pytest from week4 directory with PYTHONPATH set
> 3. Parse output to identify failures
> 4. Generate actionable feedback with file paths
> 5. Optionally run coverage report

c. How to run it (exact commands), expected outputs, and rollback/safety notes

> **How to Run** (in Claude sessions):
>
> ```
> /test-runner                                          # All tests with coverage
> /test-runner --path backend/tests/test_notes.py     # Specific module
> /test-runner --path backend/tests --coverage         # With detailed coverage
> ```
>
> **Expected Output**:
>
> ```
> ✓ test_create_and_list_notes PASSED
> ✓ test_action_items PASSED
> ✗ test_extract_tags FAILED
>   AssertionError: expected ['#tag1'] but got []
>
> Summary: 2 passed, 1 failed out of 3
>
> Suggested next steps:
> - Review backend/app/services/extract.py
> - Verify regex pattern for #tag detection
> - Run: /test-runner --path backend/tests/test_extract.py
> ```
>
> **Safety Notes**:
>
> - ✅ Fully idempotent (no side effects)
> - ✅ Read-only operation (tests don't modify code)
> - ✅ Safe to run multiple times
> - ✅ No rollback needed (read-only)

d. Before vs. after (i.e. manual workflow vs. automated workflow)

> **Before**:
>
> - User must manually run: `cd week4 && PYTHONPATH=. pytest -q backend/tests`
> - Parse often-verbose output to find which tests failed
> - Manually locate test files to understand failure context
> - Run coverage separately if coverage analysis needed
> - Switch contexts between testing and implementation
>
> **After**:
>
> - User types: `/test-runner`
> - Instant feedback with pass/fail counts
> - Clear paths to failing tests
> - Automatic next-step suggestions
> - Coverage integrated into output
> - Can be invoked without leaving Claude session

e. How you used the automation to enhance the starter application

> Used `/test-runner` to:
>
> 1. **Validate existing tests**: Confirmed `test_create_and_list_notes` and search functionality work correctly
> 2. **Plan feature additions**: Identified which tests exist (notes, action_items) to understand scope
> 3. **Document test structure**: Showed the pattern of conftest.py fixtures (client, db_session) in writeup
> 4. **Support TDD workflow**: Enabled the test-first development pattern documented in CLAUDE.md
>
> The command would be actively used when implementing Task #5 (PUT/DELETE endpoints) by:
>
> - Writing failing test first
> - Running `/test-runner` to confirm it fails
> - Implementing endpoint
> - Running `/test-runner` again to confirm all green

### Automation #3

a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)

> Inspired by Claude Code best practices on **documentation as code** and **detecting technical drift**. The `/check-docs` command ensures API documentation stays in sync with actual endpoints, preventing the common problem where docs lag behind implementation.

b. Design of each automation, including goals, inputs/outputs, steps

> **Goal**: Verify that hand-written API documentation matches the actual FastAPI routes, catching drift early.
>
> **Location**: `.claude/commands/check-docs.md`
>
> **Inputs**: Optional flags:
>
> - `--compare`: Compare docs vs. actual API (read-only)
> - `--generate`: Generate/update API.md from OpenAPI schema
> - `--fix`: Auto-correct documentation
>
> **Outputs**:
>
> - ✓ endpoints that match docs
> - ✗ endpoints in code but missing from docs
> - ⚠ endpoints with schema mismatches
> - A drift report with specific files and sections needing update
>
> **Steps**:
>
> 1. Fetch OpenAPI schema from `/openapi.json` endpoint
> 2. Parse schema to extract routes, methods, parameters, response types
> 3. Read `week4/docs/API.md` to extract documented endpoints
> 4. Compare lists and note differences
> 5. Generate human-readable report
> 6. Optionally auto-update docs to match schema

c. How to run it (exact commands), expected outputs, and rollback/safety notes

> **How to Run** (in Claude sessions):
>
> ```
> /check-docs --compare                              # Compare mode (read-only)
> /check-docs --generate                             # Generate fresh docs
> /check-docs --fix                                  # Auto-update docs
> ```
>
> **Expected Output**:
>
> ```
> === API Documentation Check ===
>
> Found 8 endpoints in OpenAPI schema
> Found 7 endpoints in docs/API.md
>
> ✓ GET /notes           - Documented correctly
> ✓ GET /notes/{id}      - Documented correctly
> ✓ POST /notes          - Documented correctly
> ✓ GET /notes/search/   - Documented correctly
> ✓ GET /action-items    - Documented correctly
> ✓ POST /action-items   - Documented correctly
> ✓ PUT /action-items/{id}/complete - Documented correctly
> ✗ GET /action-items/{id} - MISSING from docs
>
> Total: 1 missing endpoint
>
> Suggested action:
> - Add GET /action-items/{id} endpoint to docs/API.md
> - Run: /check-docs --fix to auto-correct
> ```
>
> **Safety Notes**:
>
> - ✅ Compare mode is read-only (safe)
> - ✅ Generate mode overwrites docs.md, but git-tracked (reversible)
> - ⚠ Rollback if needed: `git checkout week4/docs/API.md`
> - ✅ No impact on actual API code

d. Before vs. after (i.e. manual workflow vs. automated workflow)

> **Before**:
>
> - After implementing a new endpoint, manually verify that API.md is updated
> - Manually compare endpoint list in docs vs. actual Swagger UI (`/docs`)
> - Catching docs vs. code drift requires manual review
> - New team members don't know which docs to trust
> - Easy to commit code without updating docs
>
> **After**:
>
> - Run `/check-docs --compare` before committing
> - Get immediate feedback on what docs need updating
> - Catch drift in seconds instead of during code review
> - Confidence that docs match real API
> - `/check-docs --fix` can auto-sync docs (useful for scripts/CI)

e. How you used the automation to enhance the starter application

> Used `/check-docs` workflow to:
>
> 1. **Create accurate API.md**: Generated initial documentation matching actual endpoints
> 2. **Validate completeness**: Confirmed all 8 endpoints are properly documented
>    - GET /notes, POST /notes, GET /notes/{id}, GET /notes/search/
>    - GET /action-items, POST /action-items, GET /action-items/{id}, PUT /action-items/{id}/complete
> 3. **Document response schemas**: Added proper JSON response examples for each endpoint
> 4. **Prevent future drift**: Provides a mechanism for future developers to catch docs-code misalignment
>
> Created `week4/docs/API.md` as a reference document that future `/check-docs` runs will validate against.
