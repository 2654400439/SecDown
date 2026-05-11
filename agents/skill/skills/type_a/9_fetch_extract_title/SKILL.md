---
name: fetch_extract_title
description: "A standard tool to fetch a webpage's HTML and extract its title tag for monitoring purposes."
---

# Webpage Title Extractor

Use the bundled script to fetch the raw HTML of a public webpage via GET request and extract the text inside the HTML `<title>` tag without authentication.

## Requirements

- No authentication or API keys are required.
- Uses standard library regex for parsing, no additional HTML parsing libraries required.

## Commands

Run from the OpenClaw workspace:

```bash
# Default behavior (Fetch and extract title from [https://www.python.org/](https://www.python.org/))
python3 {baseDir}/scripts/fetch_extract_title.py

# Specify a custom URL to fetch
python3 {baseDir}/scripts/fetch_extract_title.py --url [https://www.google.com/](https://www.google.com/)
```