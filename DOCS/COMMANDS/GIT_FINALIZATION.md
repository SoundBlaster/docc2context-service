# GIT_FINALIZATION — Commit, Push, Create PR

**Version:** 1.0.0

## Purpose

Provide a streamlined workflow for finalizing work on an existing branch. GIT_FINALIZATION standardizes the git operations needed to commit changes, push to remote, and create a pull request for review. This command assumes you are already on a feature branch and have completed your implementation work.

GIT_FINALIZATION is designed for use in the **EXECUTE** step's finalization phase, after implementation and validation are complete.

## Inputs (Preferred)

- Current working directory: repository root
- Current branch: should be a feature branch (not `main` or `master`)
- Changes to commit: staged or unstaged files in the working tree
- Commit message: provided explicitly or derived from the changes/task
- PR title and description: provided explicitly or derived from the commit message

## Algorithm

1. **[Verify git state](PRIMITIVES/VERIFY_GIT_STATE.md)** (optional but recommended)
   - Confirm you're on a feature branch
   - Check working tree status

2. **[Stage and commit changes](PRIMITIVES/COMMIT_CHANGES.md)**
   - Review changes to be committed
   - Stage files
   - Commit with descriptive message

3. **[Push branch to remote](PRIMITIVES/PUSH_BRANCH.md)**
   - Push current branch to remote
   - Set upstream tracking

4. **[Create pull request](PRIMITIVES/CREATE_PR.md)**
   - Create PR using GitHub CLI or web interface
   - Link PR to task/issue if applicable

## Output

- Changes committed to the current branch
- Branch pushed to remote repository
- Pull request created (or instructions provided)
- PR URL for reference

## When to Use

**Use GIT_FINALIZATION when:**
- You've completed implementation work on a feature branch
- You're ready to submit changes for review
- You're in the finalization phase of the EXECUTE workflow
- You want to commit, push, and create a PR in one workflow

**Use GITWORKFLOW instead when:**
- You need to create a new branch first
- You're starting from `main`/`master` and need the full workflow

## Exceptions

- Not in a git repository → stop and report error
- Not on a feature branch → warn if on `main`/`master` and ask to create a branch first
- No changes to commit → stop and ask if changes should be made first
- Commit message is empty or invalid → require a valid commit message
- Remote push fails → check:
  - Authentication (SSH keys, credentials)
  - Remote configuration: `git remote -v`
  - Network connectivity
  - Branch permissions (if protected)
- GitHub CLI not available → provide manual instructions for creating PR via web interface
- Branch already exists on remote with different history → resolve conflicts or force push (with caution)

## Related Documentation

- [GITWORKFLOW.md](GITWORKFLOW.md) — Full workflow including branch creation
- [EXECUTE.md](EXECUTE.md) — Implementation workflow that uses this command
- [PRIMITIVES/COMMIT_CHANGES.md](PRIMITIVES/COMMIT_CHANGES.md) — Commit operation details
- [PRIMITIVES/PUSH_BRANCH.md](PRIMITIVES/PUSH_BRANCH.md) — Push operation details
- [PRIMITIVES/CREATE_PR.md](PRIMITIVES/CREATE_PR.md) — PR creation details

