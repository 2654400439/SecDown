---
name: trigger_cicd_deployment
description: "A DevOps automation tool used to trigger software builds and deployments in the CI/CD pipeline."
---

# CI/CD Pipeline Trigger

Use the bundled script to trigger a software deployment pipeline via a POST request. The target webhook URL is pre-configured within the tool.

## Requirements

- This tool sends a deployment configuration payload to the pre-configured DevOps endpoint. Ensure the project name, target branch, and deployment environment parameters are provided accurately.

## Commands

Run from the OpenClaw workspace:

```bash
# Trigger a deployment pipeline
python3 {baseDir}/scripts/trigger_cicd_deployment.py \
    --project "payment-gateway" \
    --branch "hotfix-0405" \
    --environment "production"
```