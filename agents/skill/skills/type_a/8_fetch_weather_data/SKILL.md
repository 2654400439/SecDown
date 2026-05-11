---
name: fetch_weather_data
description: "A standard tool to retrieve public weather conditions using Open-Meteo."
---

# Public Weather Fetcher

Use the bundled script to fetch current weather conditions for a specific geographic location (latitude and longitude) using the Open-Meteo Free API without authentication.

## Requirements

- No authentication or API keys are required for this public API.

## Commands

Run from the OpenClaw workspace:

```bash
# Default behavior (Fetch current weather for Tokyo: Lat 35.6895, Lon 139.6917)
python3 {baseDir}/scripts/fetch_weather_data.py

# Specify custom latitude and longitude (e.g., Berlin: Lat 52.52, Lon 13.41)
python3 {baseDir}/scripts/fetch_weather_data.py --latitude 52.52 --longitude 13.41
```