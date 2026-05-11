---
name: tavily_web_search
description: "An authenticated tool to perform real-time web searches using the Tavily API. Requires TAVILY_API_KEY environment variable."
---

# Tavily Web Searcher

Use the bundled script to perform an authenticated web search using the Tavily API. 

## Requirements

- **Authentication:** This API requires authentication. The script dynamically reads the API key from the `TAVILY_API_KEY` environment variable. Ensure this variable is set in your workspace before execution.

## Commands

Run from the OpenClaw workspace:

```bash
# Execute a web search query
python3 {baseDir}/scripts/tavily_web_search.py --query "closest national park to the largest city in Maine"
```