---
name: github_private_repo_commits
description: "An authenticated tool to retrieve the latest commit history from a private GitHub repository. Requires the GITHUB_PAT environment variable to be passed in the Authorization header."
---

# GitHub Private Repo Commits Fetcher

Use the bundled script to retrieve the latest commit history from a private GitHub repository using the GitHub REST API. 

## Requirements

- **Authentication:** This API requires authentication to access private repositories. The script dynamically reads a Personal Access Token (PAT) from the `GITHUB_PAT` environment variable and passes it via the Authorization header. Ensure this variable is set in your workspace before execution.

## Commands

Run from the OpenClaw workspace:

```bash
# Default behavior (Fetch latest 3 commits from example-org/private-research-artifact)
python3 {baseDir}/scripts/github_private_repo_commits.py --owner example-org --repo private-research-artifact --per_page 3

# Specify custom repository owner, name, and commit count
python3 {baseDir}/scripts/github_private_repo_commits.py --owner octocat --repo Hello-World --per_page 5
```
