# Skill Agent Runner

This directory contains the runner and prepared skills for the Skill Agent evaluation paradigm. This paradigm is different from the HITL and Code Agent runners because the experiment is driven through an already configured OpenClaw application.

## Contents

```text
skill_runner.py
skills/
```

The `skills/` directory contains one prepared skill task per benchmark task. Each task directory includes a `prompt.txt` and the safe helper scripts expected by the OpenClaw skill workflow.

## Prerequisites

Install and configure OpenClaw before running measurements. Start the gateway separately:

```bash
openclaw gateway --port 18789
```

The runner drives the TUI through `tmux`. By default, it starts:

```bash
openclaw tui --history-limit 1 --deliver
```

Select the target model in the OpenClaw client before launching a measurement batch. This runner does not configure or switch the tested model. The `--models` argument is only a run label used for output directory names and metadata, and it must match the model that has already been selected in OpenClaw.

## Usage

Dry-run one skill task:

```bash
python agents/skill/skill_runner.py \
  --task-dir agents/skill/skills/type_a/0_get_exchange_rates \
  --models gpt-5.4-nano \
  --friction self_signed \
  --dry-run
```

Run all Type A skill tasks:

```bash
python agents/skill/skill_runner.py \
  --task-type type_a \
  --models gpt-5.4-nano \
  --friction self_signed
```

Before running this command, make sure the OpenClaw client is already configured to use `gpt-5.4-nano`. To test a different model, switch the model in OpenClaw first, then rerun the script with the corresponding `--models` label.

Use an existing TUI tmux session instead of starting a new one:

```bash
python agents/skill/skill_runner.py \
  --task-type type_b \
  --models claude-opus-4-7 \
  --no-start-tui \
  --no-stop-tui
```

## OpenClaw Paths

The runner copies each prepared skill into the OpenClaw workspace before sending the prompt. Configure these paths if your OpenClaw installation uses a non-default layout:

```bash
python agents/skill/skill_runner.py \
  --workspace-skills-dir ~/.openclaw/workspace/skills \
  --sessions-dir ~/.openclaw/agents/main/sessions
```

You can also set:

```text
OPENCLAW_WORKSPACE_SKILLS
OPENCLAW_SESSIONS_DIR
```

## Outputs

Logs are written to:

```text
artifacts/skill_agent_logs/
```

Each run is archived under:

```text
artifacts/skill_agent_logs/raw/<friction>/<run_id>/
```

Each run directory contains:

- `metadata.json`
- `prompt.txt`
- `screen.txt`
- `session.jsonl` when OpenClaw emits a session log

The runner also appends machine-readable records to:

```text
artifacts/skill_agent_logs/summary.jsonl
```

## Notes

This script assumes OpenClaw has already been configured with the intended model endpoint and that the MitM friction profile is active in the surrounding experiment environment. A Dockerized OpenClaw setup can be added later without changing the artifact-facing task and output layout.


