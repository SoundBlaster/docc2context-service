# FLOW — Iterative Development Workflow

**Version:** 1.0.0

## Purpose

Defines the canonical iterative workflow for **DocC2Context Service** development. This four-step cycle ensures systematic progression through the PRD work plan (PRD §5) while maintaining clean task tracking and validation.

FLOW is the top-level orchestrator; each step is a dedicated command with its own responsibility.

## Workflow Cycle

```
┌─────────────────────────────────────────┐
│  1. SELECT  →  Choose next task         │
│  2. PLAN    →  Create task PRD          │
│  3. EXECUTE →  Implement & validate     │
│  4. ARCHIVE →  Move completed work      │
└─────────────────────────────────────────┘
           ↑                       ↓
           └───────── Repeat ──────┘
```

## Commands

### 1. SELECT

See `DOCS/COMMANDS/SELECT.md` for details.

Choose the next highest-priority task and record it to `DOCS/INPROGRESS/next.md`.

---

### 2. PLAN

See `DOCS/COMMANDS/PLAN.md` for details.

Transform the selected task into an implementation-ready PRD at `DOCS/INPROGRESS/{ID}_{Title}.md`.

---

### 3. EXECUTE

See `DOCS/COMMANDS/EXECUTE.md` for details.

Implement the planned task following TDD, validate like CI, and update task documentation.

---

### 4. ARCHIVE

See `DOCS/COMMANDS/ARCHIVE.md` for details.

Move completed task PRDs to `DOCS/TASKS_ARCHIVE/` and update the archive index.

---

## When to Use This Flow

**Use this flow when:**
- Starting a new development session
- Completing a task and ready for the next one
- Unsure what to work on next
- Need to maintain systematic progress through PRD §5

**Skip this flow when:**
- Handling urgent hotfixes (can return to flow after)
- Making trivial documentation updates
- Responding to immediate build/test failures

## Flow Discipline

1. **Complete the cycle**: Don't skip steps. Each step has essential outputs for the next.
2. **One task at a time**: Finish EXECUTE before running SELECT again.
3. **Validate always**: Never skip EXECUTE validation, even for "simple" changes.
4. **Archive regularly**: Keep `DOCS/INPROGRESS/` clean to avoid confusion.

## Exceptions

- **No tasks available**: SELECT will report "Nothing to do" — project may be complete.
- **Validation fails**: Stay in EXECUTE until all checks pass; do not proceed to ARCHIVE.
- **Dependencies blocked**: SELECT may allow selection but flag for resolution in PLAN.

## Related Documentation

- `DOCS/COMMANDS/README.md` — Command system overview
- `DOCS/COMMANDS/PROGRESS.md` — Status tracking across tasks
- `DOCS/PRD.md` — Canonical requirements and work plan
- `DOCS/Workplan.md` — Detailed task breakdown with acceptance criteria