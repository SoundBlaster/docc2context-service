# ARCHIVE — Archive Completed Task PRDs

**Version:** 1.0.0

## Purpose

If you are using the optional `DOCS/INPROGRESS/` task-PRD workflow, ARCHIVE moves completed task PRDs out of the active
folder into `DOCS/TASKS_ARCHIVE/` to keep the workspace tidy.

If you are not using `DOCS/INPROGRESS/`, this command is a no-op.

## Inputs

- `DOCS/INPROGRESS/*.md` — task PRDs and summaries
- `DOCS/Workplan.md` — project work plan, tracks completion of tasks
- `DOCS/INPROGRESS/next.md` — current selection (may be empty)

## Algorithm

1. See content of inputs
2. Determine which task PRDs from `DOCS/INPROGRESS` are "completed":
   - If task exists in the `DOCS/Workplan.md` file: completed = task marked `[x]`.
   - Otherwise: completed = task PRD explicitly marked "Completed" in its own header.
3. For each completed task PRD and other files:
   - Move it from `DOCS/INPROGRESS/` to the tasks archive in the folder with template name `DOCS/TASKS_ARCHIVE/{Task_ID}_{Task_Title}/`.
   - Append an archive stamp at the end of file: `**Archived:** YYYY-MM-DD`.
4. Update/create `DOCS/TASKS_ARCHIVE/INDEX.md` with a simple list grouped by PRD Phase (Phase 1, Phase 2, Phase 3) if known in the order of its executed.
5. Remove archived tasks from the `DOCS/INPROGRESS/next.md`

## Output

- Updated `DOCS/TASKS_ARCHIVE/` contents and `INDEX.md`
- Cleaned `DOCS/INPROGRESS`
