# Utility Scripts

## Privacy Scan

`privacy_scan.py` performs detection-only scanning for common sensitive strings in logs and artifact files.

Example:

```bash
python scripts/privacy_scan.py artifacts/hitl_logs agents/hitl tasks \
  --output-dir artifacts/privacy_scan/hitl_initial
```

The scanner does not modify files. It writes redacted findings to:

```text
privacy_findings.csv
privacy_findings.json
privacy_summary.json
privacy_report.md
```

Review findings manually before deciding whether any anonymization is needed.

## Anonymize Logs

`anonymize_logs.py` performs high-confidence in-place anonymization for secrets, local user paths, and known private repository identifiers.

Dry run:

```bash
python scripts/anonymize_logs.py artifacts/hitl_logs/raw
```

Apply changes:

```bash
python scripts/anonymize_logs.py artifacts/hitl_logs/raw --apply
```

Review-level anonymization:

```bash
python scripts/anonymize_logs.py artifacts/hitl_logs/raw --include-review --apply
```

By default, this script intentionally does not replace review-only findings such as arbitrary emails, generic local paths, GitHub user URLs, or GitHub user metadata. Use `--include-review` after inspecting the privacy scan report and deciding that these values should be anonymized for release.

The default rules cover high-confidence artifact cleanup items, including API keys in request payloads, bearer tokens, common token placeholders, local user directories, and known private repository identifiers from the experiment logs. It does not modify unknown emails, arbitrary GitHub URLs, or generic local paths unless a replacement rule has been added deliberately.

## Organize Code Agent Logs

`organize_code_agent_logs.py` imports existing Aider benchmark output folders from `artifacts/code_agent_logs/raw_tmp/` into the release-facing artifact layout.

Dry run:

```bash
python scripts/organize_code_agent_logs.py
```

Apply:

```bash
python scripts/organize_code_agent_logs.py --apply
```

The script writes normalized run directories under `artifacts/code_agent_logs/raw/<friction>/` and coverage reports under `artifacts/code_agent_logs/coverage/`.

## Organize Skill Agent Logs

`organize_skill_agent_logs.py` imports flat OpenClaw session logs from `artifacts/skill_agent_logs/raw_tmp/` into the release-facing Skill Agent layout.

Dry run:

```bash
python scripts/organize_skill_agent_logs.py
```

Apply:

```bash
python scripts/organize_skill_agent_logs.py --apply
```

The script writes normalized run directories under `artifacts/skill_agent_logs/raw/self_signed/` and coverage reports under `artifacts/skill_agent_logs/coverage/`. The current mapping is intended for the Skill Agent self-signed condition used in RQ1.

## Summarize Results

`summarize_results.py` aggregates judge outputs into paper-aligned RQ1/RQ2 tables. It preserves the distinction between the paper's physical ASR source and the judge's semantic success inference.

With server-side success data:

```bash
python scripts/summarize_results.py \
  --judge-input artifacts/hitl_logs/judge_outputs artifacts/code_agent_logs/judge_outputs artifacts/skill_agent_logs/judge_outputs \
  --server-success artifacts/aggregate_results/server_success.csv \
  --output-dir artifacts/aggregate_results
```

Provisional semantic-only summary:

```bash
python scripts/summarize_results.py \
  --judge-input artifacts/hitl_logs/judge_outputs artifacts/code_agent_logs/judge_outputs artifacts/skill_agent_logs/judge_outputs \
  --physical-fallback semantic \
  --output-dir artifacts/aggregate_results
```

The summary files include:

```text
artifacts/aggregate_results/normalized_judge_records.csv
artifacts/aggregate_results/grouped_summary.csv
artifacts/aggregate_results/rq1/rq1_paradigm_self_signed_summary.csv
artifacts/aggregate_results/rq2/rq2_code_agent_friction_summary.csv
artifacts/aggregate_results/summary_metadata.json
```

`asr_physical_percent` should be used for paper ASR when server-side success data is available. `asr_semantic_percent` is derived from the judge field `bypass_intent_success` and is included only as a reference. BN, RW, WS, and UA are conditional metrics over physically successful attacks; when `--physical-fallback semantic` is used, this conditional denominator is explicitly marked by `physical_success_source=semantic_fallback` in the normalized records.


