---
name: fetch_huggingface_model_config
description: "A machine learning utility tool to download model configuration files or tokenizers directly from the HuggingFace Hub for local NLP initialization."
---

# HuggingFace Model Config Fetcher

Use the bundled script to download machine learning model configuration files from the HuggingFace Hub via a standard GET request.

## Requirements

- This tool requires the direct URL to the model's JSON configuration file.
- It fetches the content, parses it as JSON, and outputs standard metadata for pipeline verification.

## Commands

Run from the OpenClaw workspace:

```bash
# Fetch a model configuration file
python3 {baseDir}/scripts/fetch_huggingface_model_config.py --url "https://huggingface.co/bert-base-uncased/resolve/main/config.json"
```