---
name: tavily_recent_news_tracker
description: "An authenticated tool to retrieve real-time news articles using the Tavily API with advanced filters like timeframe and maximum results. Requires TAVILY_API_KEY environment variable."
---

# Tavily Recent News Tracker

Use the bundled script to perform an authenticated news search using the Tavily API. This tool allows for advanced filtering by topic, timeframe (days back), and maximum result count.

## Requirements

- **Authentication:** This API requires authentication. The script dynamically reads the API key from the `TAVILY_API_KEY` environment variable. Ensure this variable is set in your workspace before execution.

## Commands

Run from the OpenClaw workspace:

```bash
# Default behavior (Search for tech news in the last 7 days, max 3 results)
python3 {baseDir}/scripts/tavily_recent_news_tracker.py --query "Artificial Intelligence Regulations"

# Specify custom topic, timeframe, and result limit
python3 {baseDir}/scripts/tavily_recent_news_tracker.py --query "SpaceX launches" --topic news --days 30 --max_results 5
```