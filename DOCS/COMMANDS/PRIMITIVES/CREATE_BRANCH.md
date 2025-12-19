# CREATE_BRANCH — Create and Checkout New Branch

**Version:** 1.0.0

## Purpose

Create a new git branch with a descriptive name and check it out for further work.

## Inputs

- Branch name: provided explicitly or derived from the task/work being done
- Current branch: should be `main` or `master` (or confirm if on another branch)

## Algorithm

1. Determine branch name:
   - If provided explicitly, use it
   - If not provided, derive it from the current task or work context
   - Branch name should be descriptive and follow repository conventions:
     - `task-{id}-{description}` (e.g., `task-1.2-cli-deployment`)
     - `feature/{name}` (e.g., `feature/add-git-workflow`)
     - `fix/{name}` (e.g., `fix/typo-in-readme`)

2. Create and checkout the new branch:
   - Run: `git checkout -b {branch-name}`
   - The `-b` flag creates the branch if it doesn't exist and checks it out

3. Verify branch creation:
   - Run: `git branch --show-current` to confirm you're on the new branch

## Output

- New branch created and checked out locally
- Current branch name matches the requested branch name

## Exceptions

- Branch name conflicts with existing branch → suggest alternative name or ask to overwrite
- Not in a git repository → stop and report error (should have been caught by VERIFY_GIT_STATE)
- Uncommitted changes conflict with branch creation → stash changes or commit them first

