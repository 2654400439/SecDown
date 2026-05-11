---
name: download_public_image
description: "A standard tool to download a public image and save it to the local disk as a binary file."
---

# Public Image Downloader

Use the bundled script to fetch a public image as a binary stream and save it to the local filesystem without authentication.

## Requirements

- No authentication or API keys are required.
- The script handles binary data streaming to prevent memory issues with large files.

## Commands

Run from the OpenClaw workspace:

```bash
# Default behavior (Download a cat image from CATAAS and save as downloaded_image.jpg)
python3 {baseDir}/scripts/download_public_image.py

# Specify a custom URL and output filename
python3 {baseDir}/scripts/download_public_image.py --url [https://cataas.com/cat](https://cataas.com/cat) --output cat_pic.jpg
```