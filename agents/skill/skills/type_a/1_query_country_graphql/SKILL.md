---
name: query_country_graphql
description: "A standard tool to execute GraphQL queries to fetch country, capital, and language information."
---

# Country Data Fetcher (GraphQL)

Use the bundled script to execute a GraphQL query via POST to retrieve nested geographic and language data without authentication using the public Countries GraphQL API.

## Requirements

- No authentication or API keys are required for this public API.

## Commands

Run from the OpenClaw workspace:

```bash
# Default behavior (Query data for Brazil - BR)
python3 {baseDir}/scripts/query_country_graphql.py

# Specify a custom country code (e.g., US, FR, JP)
python3 {baseDir}/scripts/query_country_graphql.py --code US
```