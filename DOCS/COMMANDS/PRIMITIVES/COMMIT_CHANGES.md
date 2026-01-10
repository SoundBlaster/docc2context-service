# COMMIT_CHANGES — Stage and Commit Changes

**Version:** 1.0.0

## Purpose

Stage modified files and commit them with a clear, descriptive commit message.

## Inputs

- Changes to commit: staged or unstaged files in the working tree
- Commit message: provided explicitly or derived from the changes

## Algorithm

1. Review what will be committed:
   - Run: `git status` to see modified, staged, and untracked files
   - Verify that the correct files are being committed

2. Stage changes:
   - Stage all changes: `git add .`
   - Or stage specific files: `git add {file1} {file2} ...`
   - Verify staged files: `git status` or `git diff --cached`

3. Commit with a clear message:
   - Run: `git commit -m "{commit-message}"`
   - Commit message should be:
     - Descriptive and clear about what was changed
     - Follow repository conventions (e.g., conventional commits format if used)
     - Examples:
       - `feat: add GITWORKFLOW command for branch, commit, push, PR workflow`
       - `fix: correct typo in README`
       - `docs: update command documentation`

4. Verify commit:
   - Run: `git log -1` to see the commit that was just created

## Output

- Changes staged and committed to the current branch
- Commit hash and message confirmation

## Exceptions

- No changes to commit → stop and ask if changes should be made first
- Commit message is empty or invalid → require a valid commit message
- Git hooks fail (if configured) → address hook failures before proceeding





