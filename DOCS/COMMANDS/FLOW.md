# FLOW — Iterative Development Workflow

**Version:** 1.0.0

## Purpose

Defines the canonical iterative workflow for **DocC2Context Service** development. This four-step cycle ensures systematic progression through the PRD work plan ([PRD §5](../PRD.md#5-implementation-roadmap-refined)) while maintaining clean task tracking and validation.

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

See [SELECT.md](SELECT.md) for details.

Choose the next highest-priority task and record it to [`DOCS/INPROGRESS/next.md`](../../INPROGRESS/next.md).

---

### 2. PLAN

See [PLAN.md](PLAN.md) for details.

Transform the selected task into an implementation-ready PRD at [`DOCS/INPROGRESS/{ID}_{Title}.md`](../../INPROGRESS/).

---

### 3. EXECUTE

See [EXECUTE.md](EXECUTE.md) for details.

Implement the planned task following TDD, validate like CI, and update task documentation.

**Git Operations:**
- Pre-flight:
  - **[Verify git state](PRIMITIVES/VERIFY_GIT_STATE.md)**
  - **[Create branch](PRIMITIVES/CREATE_BRANCH.md)** (if starting new work)
- Finalization: Use **[GITWORKFLOW](GITWORKFLOW.md)** or individual primitives:
  - **[Commit changes](PRIMITIVES/COMMIT_CHANGES.md)**
  - **[Push branch](PRIMITIVES/PUSH_BRANCH.md)**
  - **[Create PR](PRIMITIVES/CREATE_PR.md)**

---

### 4. ARCHIVE

See [ARCHIVE.md](ARCHIVE.md) for details.

Move completed task PRDs to [`DOCS/TASKS_ARCHIVE/`](../../TASKS_ARCHIVE/) and update the archive index.

---

## When to Use This Flow

**Use this flow when:**
- Starting a new development session
- Completing a task and ready for the next one
- Unsure what to work on next
- Need to maintain systematic progress through [PRD §5](../PRD.md#5-implementation-roadmap-refined)

**Skip this flow when:**
- Handling urgent hotfixes (can return to flow after)
- Making trivial documentation updates
- Responding to immediate build/test failures

## Flow Discipline

1. **Complete the cycle**: Don't skip steps. Each step has essential outputs for the next.
2. **One task at a time**: Finish [EXECUTE](EXECUTE.md) before running [SELECT](SELECT.md) again.
3. **Validate always**: Never skip [EXECUTE](EXECUTE.md) validation, even for "simple" changes.
4. **Archive regularly**: Keep [`DOCS/INPROGRESS/`](../../INPROGRESS/) clean to avoid confusion.

## Exceptions

- **No tasks available**: [SELECT](SELECT.md) will report "Nothing to do" — project may be complete.
- **Validation fails**: Stay in [EXECUTE](EXECUTE.md) until all checks pass; do not proceed to [ARCHIVE](ARCHIVE.md).
- **Dependencies blocked**: [SELECT](SELECT.md) may allow selection but flag for resolution in [PLAN](PLAN.md).

## Related Documentation

- [README.md](README.md) — Command system overview
- [PROGRESS.md](PROGRESS.md) — Status tracking across tasks
- [PRD.md](../PRD.md) — Canonical requirements and work plan
- [Workplan.md](../Workplan.md) — Detailed task breakdown with acceptance criteria