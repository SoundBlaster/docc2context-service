# VERIFY_GIT_STATE — Verify Git Repository State

**Version:** 1.0.0

## Purpose

Verify that the current working directory is a git repository and check its state before performing git operations.

## Inputs

- Current working directory: should be the repository root

## Algorithm

1. Confirm you are in a git repository:
   - Run: `git rev-parse --git-dir`
   - If this fails, the directory is not a git repository

2. Check current branch:
   - Run: `git branch --show-current`
   - This returns the name of the current branch

3. Verify working tree status:
   - Run: `git status --porcelain`
   - This shows a concise status of modified, staged, and untracked files

4. Determine next action:
   - If on `main` or `master`, proceed to create a new branch
   - If already on a feature branch, confirm before proceeding with additional operations

## Output

- Confirmation that the directory is a git repository
- Current branch name
- Working tree status (clean, modified, staged files)

## Exceptions

- Not in a git repository → stop and report error: "Not a git repository"
- Git command fails → check git installation and permissions

