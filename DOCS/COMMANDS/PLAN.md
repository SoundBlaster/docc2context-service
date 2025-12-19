# PLAN — Generate Task PRD

**Version:** 1.1.0

## Purpose

Turn a selected task (usually from PRD §5) into an **implementation-ready, single-task PRD** with concrete steps and
verification commands that match the current repository.

PLAN is a documentation-only command. Do **not** build or test the project while performing PLAN unless you explicitly
changed source code during this command (uncommon); the default flow should only adjust task PRDs.

## Inputs

- Selection: `DOCS/INPROGRESS/next.md` (preferred) or an explicit task ID (e.g., `Task 1.1`)
- Canonical project PRD: `DOCS/PRD.md`
- Optional tracking: `DOCS/Workplan.md` (if you use it)

## Algorithm

1. Determine the task ID + title:
   - Parse `DOCS/INPROGRESS/next.md`, or accept an explicit ID passed in the prompt.
2. Pull task details from `DOCS/PRD.md` §5 or `DOCS/Workplan.md` (priority, effort, dependencies, expected outputs).
3. Translate the task into an execution-ready plan:
   - Concrete file paths under `app/` and `tests/`
   - Explicit API surface touched (endpoints, services, utilities)
   - Verification commands that exist in this repo (see `.github/workflows/ci.yml` if present, or standard Python testing)
4. Emit `DOCS/INPROGRESS/{ID}_{Title}.md` with:
   - A checklist of subtasks
   - Acceptance criteria per subtask
   - Final "Definition of done" aligned to PRD acceptance criteria

## Output

- `DOCS/INPROGRESS/{ID}_{Title}.md`

## Exceptions

- Missing selection and no explicit ID → stop and ask for a task ID.
- Task ID not found in PRD §5 or Workplan → stop and ask to confirm the ID.
- Output PRD already exists → require an explicit overwrite decision.
