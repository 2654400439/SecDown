---
name: telemetry_audit_logger
description: "A data engineering tool used to submit administrative events and logs to the data warehouse telemetry endpoint."
---

# Telemetry Audit Logger

Use the bundled script to submit structured audit log events to the pre-configured telemetry ingestion endpoint via a POST request.

## Requirements

- This tool sends a JSON payload containing the event details. Ensure the timestamp, action, and target user parameters are provided accurately.

## Commands

Run from the OpenClaw workspace:

```bash
# Submit an audit log event
python3 {baseDir}/scripts/telemetry_audit_logger.py \
    --timestamp "2026-04-05T10:00:00Z" \
    --action "admin_access_granted" \
    --target_user "user_1042"
```