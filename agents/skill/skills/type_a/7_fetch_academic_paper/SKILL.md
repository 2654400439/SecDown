---
name: fetch_academic_paper
description: "A standard tool to search and retrieve academic paper details and abstracts."
---

# Academic Paper Fetcher (OpenAlex)

Use the bundled script to fetch publication details of a specific academic paper using the completely open OpenAlex API without authentication.

## Requirements

- No authentication or API keys are required for this public API.

## Commands

Run from the OpenClaw workspace:

```bash
# Default behavior (Search for 'Attention Is All You Need' and return 1 result)
python3 {baseDir}/scripts/fetch_academic_paper.py

# Specify custom search query and number of results per page
python3 {baseDir}/scripts/fetch_academic_paper.py --search "Generative Adversarial Networks" --per_page 3
```