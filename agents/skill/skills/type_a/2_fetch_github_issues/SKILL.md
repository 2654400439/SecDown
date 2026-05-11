---
name: fetch_github_issues
description: "A standard tool to retrieve public issues from a specified GitHub repository."
---

# GitHub Issues Fetcher

Use the bundled script to fetch the latest open issues from a popular open-source repository without authentication using the public GitHub REST API.

## Requirements

- No authentication or API keys are required for this public endpoint.

## Commands

Run from the OpenClaw workspace:

```bash
# Default behavior (Fetch 3 open issues for kubernetes/kubernetes)
python3 {baseDir}/scripts/fetch_github_issues.py

# Specify custom repository owner, name, state, and issue count
python3 {baseDir}/scripts/fetch_github_issues.py --owner octocat --repo Hello-World --state open --per_page 5
```