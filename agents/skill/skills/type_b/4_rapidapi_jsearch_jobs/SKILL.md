---
name: rapidapi_jsearch_jobs
description: "An authenticated tool to search for job postings using the JSearch API via the RapidAPI gateway. Requires the RAPIDAPI_API_KEY environment variable to be set for the custom authentication header."
---

# RapidAPI JSearch Job Finder

Use the bundled script to search for job postings using the JSearch API aggregated on the RapidAPI platform. 

## Requirements

- **Authentication:** This API requires a RapidAPI key. The script dynamically reads the key from the `RAPIDAPI_API_KEY` environment variable and passes it securely via the `x-rapidapi-key` header. Ensure this variable is set in your workspace before execution.

## Commands

Run from the OpenClaw workspace:

```bash
# Default behavior (Search for developer jobs in Chicago, page 1)
python3 {baseDir}/scripts/rapidapi_jsearch_jobs.py --query "developer jobs in chicago"

# Specify custom search query, page number, and other filters
python3 {baseDir}/scripts/rapidapi_jsearch_jobs.py --query "data scientist in new york" --page 1 --num_pages 2 --country us --date_posted today
```