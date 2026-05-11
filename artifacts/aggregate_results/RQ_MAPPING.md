# Result Mapping to Paper RQs

This file defines how artifact logs should be interpreted against the paper's research questions.

## RQ1: Pervasiveness and Paradigm Effects

Goal: compare all three agent paradigms under the baseline self-signed TLS friction.

Expected inputs:

- Single-turn baseline: `artifacts/baseline_logs/raw/{neutral,environment,pressure}/`
- HITL Agent: `artifacts/hitl_logs/raw/self_signed/`
- Code Agent: `artifacts/code_agent_logs/raw/self_signed/`
- Skill Agent: `artifacts/skill_agent_logs/raw/self_signed/`

Expected scope:

- 16 canonical models
- 25 benchmark tasks
- baseline `self_signed` friction
- all three paradigms
- single-turn baseline variants: neutral, environment, and pressure

## RQ2: Friction Profile Effects

Goal: isolate the impact of different TLS/network frictions.

Expected inputs:

- Code Agent only: `artifacts/code_agent_logs/raw/<friction>/`

Expected scope:

- six focal models used in the paper's friction-profile analysis:
  `claude-opus-4-7`, `gemini-3.1-pro-preview`, `gpt-5.4`, `gpt-5.4-nano`, `kimi-k2.5`, and `qwen3.6-plus`
- 25 benchmark tasks
- `local_issuer`
- `self_signed`
- `hostname_mismatch`
- `protocol_mismatch`

## RQ3: Root-Cause and Alignment Analysis

Goal: analyze why agents downgrade TLS despite recognizing the risk in observer settings.

Expected inputs may include:

- sampled execution traces,
- observer-vs-actor judgment data,
- environmental misattribution annotations,
- model-level summary tables,
- plotting-ready CSV/JSON files.

RQ3 materials can be placed under `artifacts/aggregate_results/rq3/` or another documented subdirectory.

## Supplemental Logs

Some logs exist outside the exact RQ scope, such as HITL measurements under non-baseline frictions. These should be retained as supplemental materials and indexed in coverage reports, but they should not be treated as required paper coverage.


