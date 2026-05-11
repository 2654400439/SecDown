---
name: search_train_connections
description: "A standard tool to retrieve detailed public transit routes and schedules in Switzerland."
---

# Swiss Public Transit Search

Use the bundled script to retrieve detailed public transit routes and schedules between locations in Switzerland using the Swiss Open Transport API.

## Requirements

- No authentication or API keys are required.

## Commands

Run from the OpenClaw workspace:

```bash
# Default behavior (Direct trains from Zurich to Geneva)
python3 {baseDir}/scripts/search_train_connections.py

# Specify custom origin, destination, and direct connection preference (1 for direct, 0 for all)
python3 {baseDir}/scripts/search_train_connections.py --origin Bern --destination Basel --direct 1
```