# Aggregate Results

Reserved for cross-paradigm result presentation.

Suggested contents:

- coverage summaries across HITL, Code Agent, and Skill Agent paradigms,
- model-by-friction result tables,
- task-category result tables,
- plotting-ready CSV/JSON files,
- sanitized figure source data.

Use `scripts/summarize_results.py` to aggregate judge outputs and server-side success logs into the RQ1/RQ2 summary tables. The script keeps physical ASR separate from the judge's semantic `bypass_intent_success` reference.
