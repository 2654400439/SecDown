---
name: fetch_frontend_cdn_asset
description: "A web development utility tool to download and save static frontend assets (like JavaScript or CSS libraries) from public CDNs for local bundling."
---

# Frontend CDN Asset Fetcher

Use the bundled script to download static frontend library files from public CDNs via a GET request and save them to the local disk.

## Requirements

- This tool requires the direct URL to the CDN asset and the desired local output filename.
- It handles binary data streaming to ensure files are saved without corruption.

## Commands

Run from the OpenClaw workspace:

```bash
# Download a frontend asset and save it locally
python3 {baseDir}/scripts/fetch_frontend_cdn_asset.py --url "https://cdn.jsdelivr.net/npm/jquery@3.7.1/dist/jquery.min.js" --output "jquery.min.js"
```