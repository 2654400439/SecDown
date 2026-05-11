# Code Agent Runner

This directory contains the runner for the autonomous Code Agent evaluation paradigm. The implementation uses Aider as the code-editing agent and launches Aider from Python so that tasks, models, friction labels, logs, and repetitions can be batched consistently with the HITL runner.

## Script

```text
code_runner.py
code_judge.py
```

## Prerequisite

Install Aider in the experiment environment before running non-dry-run measurements:

```bash
python -m pip install aider-chat
```

The runner expects an OpenAI-compatible endpoint. Set an API key:

```bash
export OPENAI_API_KEY="..."
```

On Windows PowerShell:

```powershell
$env:OPENAI_API_KEY="..."
```

If the provider uses a custom base URL, pass `--base-url` or set `OPENAI_BASE_URL`.

## Inputs

Task schemas are loaded from the repository-level `tasks/` directory by default. Each task JSON should contain the same fields used by the HITL runner:

- `task_id`
- `threat_category`
- `nl_goal`
- `network_requirements.method`
- `network_requirements.target_url`
- `network_requirements.params`
- `network_requirements.headers`
- `network_requirements.payload`

## Usage

Dry-run a single task without launching Aider:

```bash
python agents/code/code_runner.py \
  --task-file tasks/type_a/0_exchange_rate.json \
  --models gpt-5.4-nano \
  --friction self_signed \
  --dry-run
```

Run one model on Type A tasks:

```bash
python agents/code/code_runner.py \
  --task-type type_a \
  --models gpt-5.4-nano \
  --friction self_signed
```

Run all built-in model names:

```bash
python agents/code/code_runner.py \
  --task-type type_d \
  --models all \
  --friction hostname_mismatch \
  --max-workers 4
```

Use a custom model list:

```bash
python agents/code/code_runner.py \
  --task-type type_b \
  --models-file configs/hitl_models.example.txt \
  --friction local_issuer
```

The model list file should contain one model name per line. Lines beginning with `#` are ignored.

## Mitigation Modes

The Code Agent runner also supports the paper's mitigation experiments:

- `none`: no mitigation; default Code Agent measurement.
- `l1-generic`: injects a generic secure-coding policy through Aider's `--read` mechanism.
- `l1-targeted`: injects a minimal TLS-specific policy that forbids certificate-validation bypasses and authorizes safe task failure.
- `l2-ast`: adds a framework-side AST/security linter to the test wrapper and blocks generated code before execution if it disables TLS validation.

Example L1 run:

```bash
python agents/code/code_runner.py \
  --task-type type_a \
  --models gpt-5.4-nano \
  --friction self_signed \
  --mitigation l1-targeted \
  --output-dir artifacts/mitigation_logs
```

Example L2 run:

```bash
python agents/code/code_runner.py \
  --task-type type_a \
  --models gpt-5.4-nano \
  --friction self_signed \
  --mitigation l2-ast \
  --output-dir artifacts/mitigation_logs
```

Mitigated runs are archived under:

```text
artifacts/mitigation_logs/raw/<friction>/<mitigation>/<run_id>/
```

## Aider Configuration

Model names without a provider prefix are passed to Aider as `openai/<model>` by default. Change this with:

```bash
python agents/code/code_runner.py --provider-prefix anthropic --models claude-sonnet-4-6
```

Forward additional Aider flags with repeated `--aider-arg` options:

```bash
python agents/code/code_runner.py \
  --task-file tasks/type_a/0_exchange_rate.json \
  --models gpt-5.4-nano \
  --aider-arg=--no-auto-commits
```

## Outputs

Logs are written to:

```text
artifacts/code_agent_logs/
```

Each run is archived under:

```text
artifacts/code_agent_logs/raw/<friction>/<run_id>/
```

Each run directory contains:

- `prompt.txt`
- `script.py`
- `llm_req_res.log` when Aider emits one
- `console.txt`
- `aider_model_settings.yml`
- `metadata.json`

The runner also appends machine-readable records to:

```text
artifacts/code_agent_logs/summary.jsonl
```

## Credential Handling

Generated scripts run in isolated temporary workspaces. By default, common credential variables are set to empty strings:

- `TAVILY_API_KEY`
- `AIRLABS_API_KEY`
- `GITHUB_PAT`
- `RAPIDAPI_API_KEY`

To pass selected environment variables into generated code, use:

```bash
python agents/code/code_runner.py \
  --task-type type_b \
  --models gpt-5.4-nano \
  --pass-env TAVILY_API_KEY,AIRLABS_API_KEY
```

Do not commit real credentials or raw logs containing secrets. Use `scripts/privacy_scan.py` and `scripts/anonymize_logs.py` before release.

## LLM-as-a-Judge

Use `code_judge.py` to evaluate Aider run directories with the same paper-aligned rubric used for HITL logs. Unlike the HITL judge, this script reads the Code Agent archive structure and combines `metadata.json`, `prompt.txt`, `script.py`, `console.txt`, and `llm_req_res.log` into one judge input.

Dry-run one saved run:

```bash
python agents/code/code_judge.py \
  --input artifacts/code_agent_logs/raw/self_signed/<run_id> \
  --dry-run
```

Run the judge on a friction directory:

```bash
python agents/code/code_judge.py \
  --input artifacts/code_agent_logs/raw/self_signed \
  --output-dir artifacts/code_agent_logs/judge_outputs/self_signed \
  --judge-model gpt-5.4-nano \
  --max-workers 4
```

Outputs:

```text
artifacts/code_agent_logs/judge_outputs/
+-- records/
+-- judge_summary.jsonl
+-- judge_summary.csv
```

The judge emits the same paper-aligned fields as the HITL judge:

- `unsafe_action_ua`
- `warning_silence_ws`
- `behavior_notification_bn`
- `risk_warning_rw`
- `bypass_intent_success`


