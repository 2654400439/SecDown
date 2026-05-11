---
name: get_exchange_rates
description: "A standard tool to fetch the latest public currency exchange rates using the Frankfurter API. Use this when the user asks to analyze currency trends, convert currencies, or check financial exchange rates."
---

# Exchange Rate Fetcher

Use the bundled script to retrieve the latest public exchange rates without any authentication using a real financial API.

## Requirements

- No authentication or API keys are required for this public API.

## Commands

Run from the OpenClaw workspace:

```bash
# Default behavior (USD to CNY)
python3 {baseDir}/scripts/get_exchange_rates.py

# Specify custom base and target currencies (e.g., USD to EUR)
python3 {baseDir}/scripts/get_exchange_rates.py --base USD --target EUR