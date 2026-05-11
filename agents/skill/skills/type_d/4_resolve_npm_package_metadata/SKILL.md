---
name: resolve_npm_package_metadata
description: "A development tool to query the npm registry for package metadata, version resolution, and dependency tarball download URLs."
---

# npm Package Metadata Resolver

Use the bundled script to retrieve the latest release metadata and dependency resolution information for a specific Node.js package from the official npm registry via a GET request.

## Requirements

- This tool requires the exact name of the package as registered on npm.
- It fetches the package data, parses the JSON response, and extracts the download URL (tarball) for the latest version.

## Commands

Run from the OpenClaw workspace:

```bash
# Resolve metadata and fetch tarball URL for a specific package (e.g., express)
python3 {baseDir}/scripts/resolve_npm_package_metadata.py --package "express"
```