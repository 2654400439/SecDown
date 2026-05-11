# Result Presentation Design

This artifact presents results following the paper's research-question structure.

## RQ1: Pervasiveness and Paradigm Effects

Purpose: compare how often agents downgrade TLS across paradigms under the baseline self-signed friction.

Primary data:

- `baseline_logs/raw/{neutral,environment,pressure}/`
- `hitl_logs/raw/self_signed/`
- `code_agent_logs/raw/self_signed/`
- `skill_agent_logs/raw/self_signed/`

Expected table:

```text
rq1_paradigm_self_signed_summary.csv
rq1_single_turn_baseline_summary.csv
```

Suggested columns:

- `paradigm`
- `model`
- `task_type`
- `task_id`
- `asr`
- `ua`
- `bn`
- `rw`
- `ws`
- `log_path`

Recommended figures:

- ASR by paradigm.
- ASR by task type under self-signed friction.
- Risk-warning rate by paradigm.

## RQ2: Friction Profile Effects

Purpose: isolate how different network/TLS frictions change behavior.

Primary data:

- `code_agent_logs/raw/local_issuer/`
- `code_agent_logs/raw/self_signed/`
- `code_agent_logs/raw/hostname_mismatch/`
- `code_agent_logs/raw/protocol_mismatch/`

Primary RQ2 scope:

- six focal models: `claude-opus-4-7`, `gemini-3.1-pro-preview`, `gpt-5.4`, `gpt-5.4-nano`, `kimi-k2.5`, and `qwen3.6-plus`
- all 25 benchmark tasks
- all four friction profiles

Expected table:

```text
rq2_code_agent_friction_summary.csv
```

Suggested columns:

- `friction`
- `model`
- `task_type`
- `task_id`
- `asr`
- `ua`
- `bn`
- `rw`
- `ws`
- `log_path`

Recommended figures:

- ASR by friction profile.
- UA and RW by friction profile.
- Model-by-friction heatmap.

## RQ3: Root-Cause and Alignment Analysis

Purpose: explain the downgrade mechanism through trace-level evidence and observer-vs-actor comparisons.

Suggested location:

```text
aggregate_results/rq3/
```

Suggested files:

- `observer_actor_scores.csv`
- `environmental_misattribution_annotations.csv`
- `sampled_trace_index.csv`
- `model_level_alignment_gap.csv`

Recommended figures:

- Observer security score vs. actor ASR.
- Distribution of environmental misattribution labels.
- Capability or model-family trend plots, if used in the paper.

## Supplemental Logs

Logs outside the primary RQ scope should remain available but clearly marked as supplemental. For example, HITL logs under `local_issuer`, `hostname_mismatch`, and `protocol_mismatch` are indexed for transparency but are not required for RQ1 completeness.

Suggested table:

```text
supplemental_log_inventory.csv
```

This table can reference all extra logs without mixing them into the paper's primary result calculations.


