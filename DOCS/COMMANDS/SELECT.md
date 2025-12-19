# SELECT — Next Work Item

**Version:** 1.1.0

## Purpose

Select the next task to execute for **DocC2Context Service**, using the PRD's work plan (PRD §5) as the canonical task
list unless a repo-local `DOCS/Workplan.md` exists.

SELECT is a documentation-only command. Do **not** build or test the project while performing SELECT unless you
explicitly touched source code during this command (rare). The default assumption is that no code is modified here.

SELECT does **not** create implementation steps; it only chooses "what's next" and records minimal metadata for PLAN.

## Inputs (Preferred Order)

1. `DOCS/Workplan.md` — checkbox list derived from PRD §5
2. `DOCS/PRD.md` — PRD work plan tasks and milestones
3. `DOCS/INPROGRESS/next.md` — current selection (may be empty)

## Algorithm

1. Determine the set of candidate tasks:
   - If `DOCS/Workplan.md` exists: choose from unchecked items.
   - Otherwise: choose from PRD §5 task IDs (Task 1.1, 1.2, 2.1, etc.) that are not marked complete elsewhere.
2. Respect dependencies if they are tracked (Workplan dependency notes or PRD task dependencies).
3. Prefer highest priority first (Workplan Priority column), then earlier phase order (Phase 1 → Phase 3), then numeric order.
4. Write/update `DOCS/INPROGRESS/next.md` as a **minimal selection record** (no checklists).

## Output

- `DOCS/INPROGRESS/next.md`
- If `DOCS/Workplan.md` exists: mark the selected task as `INPROGRESS` (optional but recommended).

## `next.md` Template (Minimal)

```markdown
# Next Task: {ID} — {Title}

**Source:** PRD §5
**Priority:** {Critical/High/Medium/Low}
**Phase:** {1/2/3}
**Effort:** {Estimated hours}
**Dependencies:** {Task IDs or None}
**Status:** Selected

## Description

{1–3 sentences, copied from PRD §5 or Workplan}

## Next Step

Run PLAN to generate an implementation-ready task PRD for this item.
```

## Exceptions

- No candidates found → stop and report "Nothing to do" (likely everything is complete or tracking is missing).
- Dependencies unknown → allow selection but record `Dependencies: Unknown` and call it out for resolution in PLAN.
