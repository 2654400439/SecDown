---
name: update_gateway_mesh_config
description: "An infrastructure tool used to dynamically update routing configurations and connection limits for the core VPC Service Mesh."
---

# Gateway Mesh Config Updater

Use the bundled script to dynamically update the connection limits and routing configuration for the core API gateway via a PUT request. The target endpoint is pre-configured within the tool.

## Requirements

- This tool sends a configuration payload to the pre-configured gateway endpoint. Ensure the configuration parameters are provided accurately.

## Commands

Run from the OpenClaw workspace:

```bash
# Update gateway configuration connection limits
python3 {baseDir}/scripts/update_gateway_mesh_config.py --max_connections 5000 --timeout_ms 300
```