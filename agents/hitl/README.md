# HITL Agent Runner

This directory contains tooling for the Human-in-the-Loop (HITL) evaluation paradigm and the single-turn prompt baseline used as an RQ1 comparison.

The runner sends a neutral task prompt to an OpenAI-compatible chat-completions endpoint, extracts the generated Python script, executes it in an isolated temporary workspace, feeds execution errors back to the model, and records the full trace. The judge script evaluates saved traces with the paper-aligned rubric.

## Scripts

```text
baseline_runner.py
hitl_runner.py
hitl_judge.py
```


## Inputs

Task schemas are loaded from the repository-level `tasks/` directory by default.

Each task JSON must contain:

- `task_id`
- `threat_category`
- `nl_goal`
- `network_requirements.method`
- `network_requirements.target_url`
- `network_requirements.params`
- `network_requirements.headers`
- `network_requirements.payload`

## Runner Usage

Run one model on Type A tasks:

```bash
python agents/hitl/hitl_runner.py \
  --task-type type_a \
  --models gpt-5.4-nano
```

Run a single task:

```bash
python agents/hitl/hitl_runner.py \
  --task-file tasks/type_a/0_exchange_rate.json \
  --models gpt-5.4-nano
```

Run all built-in model names:

```bash
python agents/hitl/hitl_runner.py \
  --task-type type_d \
  --models all \
  --max-workers 4
```

Use a custom model list:

```bash
python agents/hitl/hitl_runner.py \
  --task-type type_b \
  --models-file configs/hitl_models.example.txt
```

The model list file should contain one model name per line. Lines beginning with `#` are ignored.

## Single-Turn Baseline

`baseline_runner.py` runs the RQ1 baseline where the model produces code in one response and the script is not executed or repaired. It supports three prompt variants:

- `neutral`: the base task prompt only.
- `environment`: adds an environment-friction note.
- `pressure`: adds a time-sensitive production pressure note.

Run the baseline on one task:

```bash
python agents/hitl/baseline_runner.py \
  --task-file tasks/type_a/0_exchange_rate.json \
  --models gpt-5.4-nano \
  --variants all
```

Run all tasks for one model:

```bash
python agents/hitl/baseline_runner.py \
  --models gpt-5.4-nano \
  --variants neutral,environment,pressure \
  --max-workers 4
```

Baseline outputs are written to:

```text
artifacts/baseline_logs/
+-- raw/
|   +-- neutral/
|   +-- environment/
|   +-- pressure/
+-- summary.jsonl
```

These logs are compatible with `hitl_judge.py` for semantic metrics. The baseline does not produce physical ASR because no generated script is executed against the MitM server.

## API Configuration

The scripts use the OpenAI Python SDK with an OpenAI-compatible endpoint.

Set the API key:

```bash
export OPENAI_API_KEY="..."
```

On Windows PowerShell:

```powershell
$env:OPENAI_API_KEY="..."
```

If your provider uses a custom base URL:

```bash
python agents/hitl/hitl_runner.py \
  --base-url https://example-provider.invalid/v1 \
  --models gpt-5.4-nano
```

You can also set `OPENAI_BASE_URL`.

## Runner Outputs

Logs are written to:

```text
artifacts/hitl_logs/
```

Each run produces a text trace log containing:

- execution summary,
- final extracted Python code,
- full model and sandbox interaction trace.

The runner also appends machine-readable records to:

```text
artifacts/hitl_logs/summary.jsonl
```

Use `--output-dir` to change the output location.

## Credential Handling

Generated scripts run in an isolated temporary directory. By default, common credential variables are set to empty strings:

- `TAVILY_API_KEY`
- `AIRLABS_API_KEY`
- `GITHUB_PAT`
- `RAPIDAPI_API_KEY`

To pass selected local environment variables into the generated script, use:

```bash
python agents/hitl/hitl_runner.py \
  --task-type type_b \
  --models gpt-5.4-nano \
  --pass-env TAVILY_API_KEY,AIRLABS_API_KEY
```

Do not commit real credentials or raw logs containing secrets.

## Runner Dry Run

Use dry-run mode to validate task loading and output paths without calling the model API:

```bash
python agents/hitl/hitl_runner.py \
  --task-type type_a \
  --models gpt-5.4-nano \
  --dry-run
```

## LLM-as-a-Judge

Use `hitl_judge.py` to evaluate saved HITL trace logs with the paper's structured rubric.

Dry-run one log:

```bash
python agents/hitl/hitl_judge.py \
  --input artifacts/hitl_logs/raw/self_signed \
  --limit 1 \
  --dry-run
```

Run the judge on a directory:

```bash
python agents/hitl/hitl_judge.py \
  --input artifacts/hitl_logs/raw/self_signed \
  --output-dir artifacts/hitl_logs/judge_outputs/self_signed \
  --judge-model gpt-5.4-nano \
  --max-workers 4
```

Outputs:

```text
artifacts/hitl_logs/judge_outputs/
+-- records/
+-- judge_summary.jsonl
+-- judge_summary.csv
```

The judge emits the paper-aligned fields:

- `unsafe_action_ua`
- `warning_silence_ws`
- `behavior_notification_bn`
- `risk_warning_rw`
- `bypass_intent_success`

## Notes

These scripts execute or evaluate model-generated code and traces. Run them only in an isolated experiment environment with the intended network redirection and MitM server configuration.

