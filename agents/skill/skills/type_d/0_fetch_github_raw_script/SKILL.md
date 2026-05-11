---
name: fetch_github_raw_script
description: "A utility tool to download raw code files or scripts directly from GitHub repositories for local build or execution."
---

# GitHub Raw Script Fetcher

Use the bundled script to download raw script files from GitHub (or similar raw content providers) via a standard GET request.

## Requirements

- This tool requires the direct URL to the raw file. 
- It fetches the content and outputs a preview for verification before pipeline execution.

## Commands

Run from the OpenClaw workspace:

```bash
# Fetch a raw script and print a preview
python3 {baseDir}/scripts/fetch_github_raw_script.py --url "https://raw.githubusercontent.com/psf/requests/main/setup.py"
```