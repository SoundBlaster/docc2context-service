# GITWORKFLOW — Create Branch, Commit, Push, Create PR

**Version:** 1.0.0

## Purpose

Provide a simple, repeatable workflow for shipping changes to the repository:

1. Create a new branch from the current state
2. Commit changes with an appropriate message
3. Push the branch to the remote repository
4. Create a pull request

GITWORKFLOW standardizes the git operations needed to submit work for review. It assumes you have already implemented and validated your changes locally.

## Inputs (Preferred)

- Current working directory: repository root
- Changes to commit: staged or unstaged files in the working tree
- Branch name: provided explicitly or derived from the task/work being done
- Commit message: provided explicitly or derived from the changes
- PR title and description: provided explicitly or derived from the commit message

## Algorithm

1. **[Verify git state](PRIMITIVES/VERIFY_GIT_STATE.md):**
   - Confirm you are in a git repository: `git rev-parse --git-dir`
   - Check current branch: `git branch --show-current`
   - Verify working tree status: `git status --porcelain`
   - If on `main` or `master`, proceed to create a new branch. If already on a feature branch, confirm before proceeding.

2. **[Create new branch](PRIMITIVES/CREATE_BRANCH.md):**
   - Branch name should be descriptive and follow repository conventions (e.g., `task-{id}-{description}`, `feature/{name}`, `fix/{name}`)
   - Create and checkout the new branch: `git checkout -b {branch-name}`
   - If branch name is not provided, derive it from the current task or work context

3. **[Stage and commit changes](PRIMITIVES/COMMIT_CHANGES.md):**
   - Review what will be committed: `git status`
   - Stage all changes: `git add .` (or stage specific files as needed)
   - Commit with a clear message: `git commit -m "{commit-message}"`
   - Commit message should be descriptive and follow repository conventions (e.g., conventional commits format if used)

4. **[Push branch to remote](PRIMITIVES/PUSH_BRANCH.md):**
   - Push the branch: `git push -u origin {branch-name}`
   - The `-u` flag sets upstream tracking for the branch

5. **[Create pull request](PRIMITIVES/CREATE_PR.md):**
   - Use GitHub CLI if available: `gh pr create --title "{title}" --body "{description}"`
   - Or provide instructions to create PR via GitHub web interface
   - PR title should match or be derived from the commit message
   - PR description should include:
     - What changes were made
     - Why the changes were made
     - Any relevant context or references to issues/tasks

## Output

- New branch created and checked out locally
- Changes committed to the branch
- Branch pushed to remote repository
- Pull request created (or instructions provided)

## Exceptions

- Not in a git repository → stop and report error
- No changes to commit → stop and ask if changes should be made first
- Branch name conflicts with existing branch → suggest alternative name or ask to overwrite
- Remote push fails → check authentication and remote configuration
- GitHub CLI not available → provide manual instructions for creating PR via web interface
- Uncommitted changes conflict with branch creation → stash changes or commit them first

## Example Usage

```bash
# After implementing changes and validating them
# 1. Create branch
git checkout -b add-git-workflow-command

# 2. Stage and commit
git add DOCS/COMMANDS/GITWORKFLOW.md
git commit -m "Add GITWORKFLOW command for branch, commit, push, PR workflow"

# 3. Push
git push -u origin add-git-workflow-command

# 4. Create PR
gh pr create --title "Add GITWORKFLOW command" --body "Adds a new command specification for the standard git workflow: create branch, commit, push, and create PR."
```

