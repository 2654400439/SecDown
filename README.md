# SecDown Artifact

This repository contains the anonymized artifact code for:

**Silent Surrender: Measuring MitM-Induced TLS Downgrades in LLM Agents**

SecDown measures **Autonomous Security Downgrade**, a failure mode where task-driven LLM agents encounter TLS or protocol friction and independently weaken transport security, for example through `verify=False`, `curl -k`, warning suppression, or equivalent bypasses.

The GitHub repository contains the executable framework, benchmark tasks, prepared skills, MitM server, analysis scripts, and documentation. Large experiment logs and the full OpenClaw skills snapshot are distributed separately through Zenodo:

```text
https://zenodo.org/records/20115421
https://doi.org/10.5281/zenodo.20115421
```

## Repository Layout

```text
agents/
  hitl/        Human-in-the-loop runner, single-turn baseline, and judge.
  code/        Aider-based autonomous code-agent runner and judge.
  skill/       OpenClaw TUI runner and prepared skill tasks.
analysis/
  rq3/         Observer and environmental-attribution judges for RQ3.
  ecosystem/   OpenClaw skill ecosystem audit script.
artifacts/    Output placeholders and result-layout documentation.
configs/      Example model lists.
mitigations/  L1/L2/L3 mitigation documentation and runner integration notes.
mitm_server/  TLS-friction and MitM test server implementation.
scripts/      Log organization, anonymization, privacy scan, and summary utilities.
tasks/        The 25 benchmark task schemas.
```

## What Is Included

- Benchmark task schemas for four task families.
- Three agent-paradigm runners.
- LLM-as-a-judge evaluators for HITL and Code Agent traces.
- RQ3 observer and environmental-attribution judges.
- MitM server implementation for self-signed, local issuer, hostname mismatch, and protocol mismatch frictions.
- Mitigation support for Code Agent L1 prompt policies and L2 AST blocking.
- Utilities for importing logs, anonymizing traces, scanning for privacy-sensitive strings, and summarizing judge outputs.
- Prepared OpenClaw skills for the Skill Agent paradigm.

Large raw logs, coverage matrices, and the full OpenClaw skills snapshot are not committed here. They are available from Zenodo.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Some runners require additional external tools:

- Code Agent: install `aider-chat`.
- Skill Agent: install and configure OpenClaw, then start `openclaw gateway --port 18789`.
- MitM experiments: run in an isolated environment where outbound traffic can be redirected to the test server.

## Quick Smoke Tests

Dry-run the HITL runner:

```bash
python agents/hitl/hitl_runner.py \
  --task-file tasks/type_a/0_exchange_rate.json \
  --models gpt-5.4-nano \
  --dry-run
```

Dry-run the Code Agent runner:

```bash
python agents/code/code_runner.py \
  --task-file tasks/type_a/0_exchange_rate.json \
  --models gpt-5.4-nano \
  --friction self_signed \
  --dry-run
```

Dry-run the Skill Agent runner:

```bash
python agents/skill/skill_runner.py \
  --task-dir agents/skill/skills/type_a/0_get_exchange_rates \
  --models manual-model \
  --friction self_signed \
  --dry-run
```

Run the OpenClaw ecosystem audit on the small prepared skills included in this repository:

```bash
python analysis/ecosystem/openclaw_skills_analysis.py \
  --skills-root agents/skill/skills \
  --output-dir artifacts/ecosystem_audit/openclaw_skills_smoke \
  --limit 10
```

## Data

The Zenodo record contains:

- HITL logs.
- Code Agent logs.
- Skill Agent logs.
- The OpenClaw skills snapshot downloaded from the public OpenClaw GitHub repository on 2026-04-25.

See [DATA_AVAILABILITY.md](DATA_AVAILABILITY.md) for the release layout and reproduction notes.

## RQ Mapping

- RQ1 compares the single-turn baseline and all three agent paradigms under the self-signed TLS friction.
- RQ2 focuses on the Code Agent paradigm across all four TLS/protocol friction profiles.
- RQ3 uses separate observer and environmental-attribution analyses.
- The OpenClaw ecosystem audit analyzes how broadly platform-side skills expose network-facing behavior and TLS-insecure patterns.

The result-layout notes in `artifacts/` describe where newly generated logs and derived summaries should be written.

## Safety

Run experiments only in isolated environments. State-changing tasks should target mock services, not production systems. Do not commit credentials, unsanitized logs, personal paths, private repository names, or provider-specific secrets.

Before publishing changes, run:

```bash
python scripts/privacy_scan.py . --output-dir artifacts/privacy_scan/local_check
```

## Citation

The artifact is anonymized for review. Citation metadata can be updated after deanonymization.
