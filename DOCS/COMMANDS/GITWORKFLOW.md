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

1. **[Verify git state](PRIMITIVES/VERIFY_GIT_STATE.md)**

2. **[Create new branch](PRIMITIVES/CREATE_BRANCH.md)**

3. **[Stage and commit changes](PRIMITIVES/COMMIT_CHANGES.md)**

4. **[Push branch to remote](PRIMITIVES/PUSH_BRANCH.md)**

5. **[Create pull request](PRIMITIVES/CREATE_PR.md)**

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

