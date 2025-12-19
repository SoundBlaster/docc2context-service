# PROGRESS — Update Checklist / Status

**Version:** 1.0.0

## Purpose

Keep lightweight, human-readable progress tracking while implementing a task PRD. This is optional and should never
block shipping working code.

## Inputs

- `DOCS/INPROGRESS/next.md` (optional)
- `DOCS/INPROGRESS/{ID}_{Title}.md` (preferred, task PRD checklist)
- `DOCS/Workplan.md` (optional, if you use it)

## Algorithm

1. Identify the current task ID from `DOCS/INPROGRESS/next.md` (if present) or from the open task PRD filename.
2. Update one of:
   - The checklist inside the task PRD (`[ ]` → `[x]`), and/or
   - The status line in `DOCS/INPROGRESS/next.md`, and/or
   - The checkbox/state in `DOCS/Workplan.md`.
3. Keep updates minimal: reflect reality (what's merged/committed), not intent.

## Output

- Updated docs (one or more of the inputs above).

## Notes

- Committing "progress-only" doc changes is optional; prefer bundling with functional commits if possible.
- If you don't use `DOCS/Workplan.md`, treat PRD §5 in `DOCS/PRD.md` as the task list and only
  track progress in the task PRD.
