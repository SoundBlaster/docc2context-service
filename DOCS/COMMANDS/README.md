# DocC2Context Service Workflow Commands

**Version:** 2.1.0

## Overview

These command specs describe a lightweight, documentation-driven workflow for this repository. They are meant to be used
as **prompts/instructions for a coding agent** (or a human), not as executable shell scripts.

| Command | Purpose | Details |
|---------|---------|---------|
| **SELECT** | Choose the next work item | [SELECT.md](./SELECT.md) |
| **PLAN** | Turn the selected item into an implementation-ready task PRD | [PLAN.md](./PLAN.md) |
| **EXECUTE** | Pre-flight → implement → validate → finalize | [EXECUTE.md](./EXECUTE.md) |
| **PROGRESS** | Optional checklist/progress updates | [PROGRESS.md](./PROGRESS.md) |
| **ARCHIVE** | Move completed task PRDs out of the way | [ARCHIVE.md](./ARCHIVE.md) |

## Source Of Truth

- Product/design requirements: `DOCS/PRD.md`
- Repository reality (what you can actually run): `requirements.txt` (or `pyproject.toml`), `.github/workflows/ci.yml` (if present)

## Bootstrap (If You Adopt This Workflow)

This repo currently ships only the PRD above. If you want the full "SELECT → PLAN → EXECUTE" loop, create:

```bash
mkdir -p DOCS/INPROGRESS DOCS/TASKS_ARCHIVE
touch DOCS/INPROGRESS/next.md
```

Optionally add `DOCS/Workplan.md` by extracting task IDs from PRD §5 (Task 1.1, 1.2, etc.) into a checkbox list.

## Workflow

```
SELECT → PLAN → EXECUTE → (repeat)
                     ↓
                 ARCHIVE (periodically)
```

**Philosophy:** implementation instructions live in task PRDs derived from `DOCS/PRD.md`. These
commands standardize selection, planning, validation, and documentation updates.

## Validation Baseline

At minimum, match CI locally:

```bash
pytest -v
```

If you have code formatters/linters installed (CI may use them), also run:

```bash
# Format check (if using black)
black --check .

# Type check (if using mypy)
mypy .

# Lint check (if using ruff or flake8)
ruff check .  # or: flake8 .
```

## Repository Files (Current)

```
DOCS/
  COMMANDS/
  PRD.md
  Workplan.md
app/          # (to be created)
tests/        # (to be created)
requirements.txt  # (to be created)
Dockerfile    # (to be created)
.github/workflows/ci.yml  # (optional)
```
