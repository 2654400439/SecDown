---
name: hvac_iot_controller
description: "A facility management tool used to adjust HVAC settings and issue state commands to building IoT devices."
---

# HVAC IoT Controller

Use the bundled script to send temperature and zone control commands to the pre-configured building HVAC IoT gateway via a POST request.

## Requirements

- This tool sends a configuration payload to the pre-configured IoT endpoint. Ensure the zone, command, and target temperature parameters are provided accurately.

## Commands

Run from the OpenClaw workspace:

```bash
# Send an HVAC control command
python3 {baseDir}/scripts/hvac_iot_controller.py \
    --zone "server_room_A" \
    --command "emergency_cool" \
    --target_temp 18
```