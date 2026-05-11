# Experiment Outputs

This directory is the local output area for SecDown measurements. The GitHub artifact keeps only README files and result-layout notes here. Full released logs are stored in Zenodo:

```text
https://zenodo.org/records/20115421
https://doi.org/10.5281/zenodo.20115421
```

## Layout

```text
artifacts/
  baseline_logs/
  hitl_logs/
  code_agent_logs/
  skill_agent_logs/
  mitigation_logs/
  ecosystem_audit/
  aggregate_results/
```

## Result Mapping

| Paper section | Main comparison | Expected local inputs |
| --- | --- | --- |
| RQ1 | Single-turn baseline plus all three agent paradigms under self-signed TLS friction | `baseline_logs/raw/{neutral,environment,pressure}/`, `hitl_logs/raw/self_signed/`, `code_agent_logs/raw/self_signed/`, `skill_agent_logs/raw/self_signed/` |
| RQ2 | Code Agent, six focal models, all tasks, all friction profiles | `code_agent_logs/raw/{local_issuer,self_signed,hostname_mismatch,protocol_mismatch}/` |
| RQ3 | Observer and environmental-attribution analysis | `aggregate_results/rq3/` |
| Ecosystem audit | OpenClaw skill exposure analysis | `ecosystem_audit/openclaw_skills/` |

Suggested local output layout:

```text
<component>/
  raw/
    <friction>/
  coverage/
  judge_outputs/
```

Generated outputs should remain local or be released through Zenodo after anonymization. Do not commit credentials, unsanitized private repository names, local machine paths, or raw logs containing identifying metadata.
