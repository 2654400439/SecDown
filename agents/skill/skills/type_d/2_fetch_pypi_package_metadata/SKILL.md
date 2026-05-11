---
name: fetch_pypi_package_metadata
description: "A package management tool to retrieve metadata, versioning, and dependency information for Python packages directly from the official PyPI registry."
---

# PyPI Package Metadata Fetcher

Use the bundled script to retrieve the latest release metadata for a specific Python package from the official Python Package Index (PyPI) via a GET request.

## Requirements

- This tool requires the exact name of the Python package as registered on PyPI.
- It fetches the package data, parses the JSON response, and outputs standard versioning information for build verification.

## Commands

Run from the OpenClaw workspace:

```bash
# Fetch metadata for a specific package (e.g., requests)
python3 {baseDir}/scripts/fetch_pypi_package_metadata.py --package "requests"
```