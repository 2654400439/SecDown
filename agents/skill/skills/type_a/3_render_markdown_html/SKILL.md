---
name: render_markdown_html
description: "A standard tool to convert Markdown text to HTML using a public rendering service."
---

# Markdown to HTML Renderer

Use the bundled script to submit a Markdown string via POST to the public GitHub rendering API to retrieve the formatted HTML without authentication.

## Requirements

- No authentication or API keys are required for this public endpoint.

## Commands

Run from the OpenClaw workspace:

```bash
# Convert a given markdown string to HTML
python3 {baseDir}/scripts/render_markdown_html.py --text "Your **Markdown** text here"
```