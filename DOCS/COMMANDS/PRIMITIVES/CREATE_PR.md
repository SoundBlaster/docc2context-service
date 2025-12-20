# CREATE_PR — Create Pull Request

**Version:** 1.0.0

## Purpose

Create a pull request for the pushed branch to submit changes for review.

## Inputs

- Branch name: the branch that was pushed (source branch)
- Base branch: typically `main` or `master` (target branch)
- PR title: provided explicitly or derived from the commit message
- PR description: provided explicitly or derived from the commit message

## Algorithm

1. Determine PR details:
   - PR title should match or be derived from the commit message
   - PR description should include:
     - What changes were made
     - Why the changes were made
     - Any relevant context or references to issues/tasks

2. Create pull request using GitHub CLI (preferred):
   - Check if GitHub CLI is available: `gh --version`
   - If available, run: `gh pr create --title "{title}" --body "{description}"`
   - Optionally specify base branch: `gh pr create --base main --title "{title}" --body "{description}"`

3. Alternative: Create PR via GitHub web interface:
   - Provide instructions to navigate to the repository on GitHub
   - Click "Compare & pull request" button (if it appears)
   - Or manually: go to "Pull requests" → "New pull request"
   - Select source and base branches
   - Fill in title and description
   - Click "Create pull request"

## Output

- Pull request created on GitHub
- PR URL for reference and sharing

## Exceptions

- GitHub CLI not available → provide manual instructions for creating PR via web interface
- Branch not pushed to remote → push the branch first (see PUSH_BRANCH)
- Authentication issues with GitHub CLI → configure authentication: `gh auth login`
- PR creation fails → check branch permissions and repository settings


