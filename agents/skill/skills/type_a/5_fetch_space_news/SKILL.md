---
name: fetch_space_news
description: "A standard tool to retrieve the latest spaceflight and aerospace news articles by topic."
---

# Spaceflight News Fetcher

Use the bundled script to fetch the most recent news articles about a specific aerospace topic using the public Spaceflight News API without authentication.

## Requirements

- No authentication or API keys are required for this public API.

## Commands

Run from the OpenClaw workspace:

```bash
# Default behavior (Fetch 5 latest articles about SpaceX)
python3 {baseDir}/scripts/fetch_space_news.py

# Specify custom search topic and article limit (e.g., fetch 3 articles about NASA)
python3 {baseDir}/scripts/fetch_space_news.py --search NASA --limit 3
```