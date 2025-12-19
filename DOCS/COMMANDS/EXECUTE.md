# EXECUTE — Implement And Validate Current Task

**Version:** 1.0.0

## Purpose

Provide a thin, repeatable workflow wrapper for implementing a selected task in this repository:

1. Pre-flight checks (verify and setup tooling + git state)
2. Implement work (following a task PRD or PRD §5)
3. Validate like CI
4. Finalize documentation and optionally commit

EXECUTE does not "auto-implement" requirements; it only standardizes the loop around implementation.

## Inputs (Preferred)

- `DOCS/INPROGRESS/next.md` (optional) — the selected task
- `DOCS/INPROGRESS/{ID}_{Title}.md` (optional) — task PRD created by PLAN
- `DOCS/PRD.md` — canonical requirements, work plan, acceptance criteria
- `.github/workflows/ci.yml` (optional) — canonical validation commands

## Pre-Flight Checks

1. Confirm Python is available:
   - `python --version` or `python3 --version` (should be Python 3.10+)
1.1 If not available: download and install Python 3.10 or later
2. Confirm virtual environment is activated (recommended):
   - Check for `VIRTUAL_ENV` environment variable or `venv` directory
2.1 If not activated: create and activate virtual environment
   - `python3 -m venv venv`
   - `source venv/bin/activate` (on macOS/Linux) or `venv\Scripts\activate` (on Windows)
3. Confirm dependencies are installed:
   - `pip install -r requirements.txt` (if requirements.txt exists)
4. Confirm a clean working tree (recommended):
   - `git status --porcelain`
5. Confirm the selected task is known:
   - If using `DOCS/INPROGRESS/next.md`, ensure it names a task ID from PRD §5 or Workplan.

## Work Period

Implement the selected task by following (in order of preference):

1. The task PRD in `DOCS/INPROGRESS/{ID}_{Title}.md` (if it exists)
2. Otherwise, the corresponding task in PRD §5 or Workplan plus the acceptance criteria

Follow TDD practices: write tests first, then implement functionality.

## Post-Flight Validation (Match CI)

Run the same checks CI uses (if CI exists) or standard Python validation:

```bash
# Run tests
pytest -v
```

If you have code formatters/linters installed, run:

```bash
# Format check (if using black)
black --check .

# Type check (if using mypy)
mypy .

# Lint check (if using ruff or flake8)
ruff check .  # or: flake8 .
```

Optional Docker validation (if Dockerfile exists):

```bash
docker build -t docc2context-service .
docker run --rm docc2context-service pytest
```

## Finalization

1. Update documentation (optional but recommended):
   - Mark the task PRD checklist items complete.
   - Update `DOCS/INPROGRESS/next.md` status.
   - If you maintain `DOCS/Workplan.md`, mark the task `[x]`.
2. Commit and push as appropriate for your workflow.

## Exceptions

- Python not available → install it first (Python 3.10+ required).
- Dependencies missing → install with `pip install -r requirements.txt`.
- Validation fails → fix issues and re-run the post-flight commands until green.
