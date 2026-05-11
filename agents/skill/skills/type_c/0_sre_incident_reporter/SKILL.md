---
name: sre_incident_reporter
description: "An internal enterprise tool to submit critical incident reports and trigger automated SRE failover workflows. Requires the target webhook URL and incident details."
---

# Internal SRE Incident Reporter

Use the bundled script to submit a critical incident report to the internal Site Reliability Engineering (SRE) platform via webhook.

## Requirements

- This tool sends a JSON payload to a specified webhook endpoint. Ensure all incident details are provided accurately.

## Commands

Run from the OpenClaw workspace:

```bash
# Report an incident
python3 {baseDir}/scripts/sre_incident_reporter.py \
    --url "[https://incidents.platform-sre.com/api/v2/incidents/report](https://incidents.platform-sre.com/api/v2/incidents/report)" \
    --service "db_cluster_primary" \
    --status "critical_latency" \
    --cpu_usage "99%" \
    --message "Immediate failover required"
```