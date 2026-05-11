---
name: airlabs_flight_schedule
description: "An authenticated tool to retrieve airline flight schedules and terminal information using the AirLabs API. Requires AIRLABS_API_KEY environment variable."
---

# AirLabs Flight Schedule Fetcher

Use the bundled script to retrieve airline flight schedules, departure times, and terminal information using the AirLabs API.

## Requirements

- **Authentication:** This API requires authentication. The script dynamically reads the API key from the `AIRLABS_API_KEY` environment variable. Ensure this variable is set in your workspace before execution.

## Commands

Run from the OpenClaw workspace:

```bash
# Default behavior (Fetch schedule for flight AA100)
python3 {baseDir}/scripts/airlabs_flight_schedule.py

# Specify a custom flight IATA code
python3 {baseDir}/scripts/airlabs_flight_schedule.py --flight_iata BA12
```