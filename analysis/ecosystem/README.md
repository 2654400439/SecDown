# Ecosystem Audit

This directory contains the release-facing script for the OpenClaw skill ecosystem analysis described in the paper.

`openclaw_skills_analysis.py` analyzes an extracted OpenClaw skills snapshot and classifies skills by network-facing behavior and pre-existing TLS-insecure patterns.

The paper analysis used a skills snapshot downloaded from the public OpenClaw GitHub repository on 2026-04-25. The complete snapshot is larger than 1 GB and is archived with the artifact data package:

```text
https://zenodo.org/records/20115421
https://doi.org/10.5281/zenodo.20115421
```

Run on the full extracted snapshot:

```bash
python analysis/ecosystem/openclaw_skills_analysis.py \
  --skills-root /path/to/extracted/openclaw/skills \
  --output-dir artifacts/ecosystem_audit/openclaw_skills \
  --workers 8
```

Smoke test with the prepared Skill Agent examples included in this repository:

```bash
python analysis/ecosystem/openclaw_skills_analysis.py \
  --skills-root agents/skill/skills \
  --output-dir artifacts/ecosystem_audit/openclaw_skill_audit_smoke \
  --limit 10
```

Outputs:

```text
artifacts/ecosystem_audit/openclaw_skills/
  summary.json
  summary.csv
  skill_inventory.csv
```

Classification fields:

- `network_skills`: skills that appear to perform network operations.
- `level_1`: network-facing skills using dynamic scripts or easy-to-downgrade CLIs such as `curl`, `wget`, or `git`.
- `level_2`: network-facing skills using harder-to-classify CLIs or compiled/static-language networking stacks.
- `pre_insecure_count`: skills that already contain TLS-insecure patterns such as `verify=False`, `curl -k`, or `rejectUnauthorized: false`.

This is a static, pattern-based ecosystem measurement. It is designed for large-scale exposure analysis, not for proving exploitability of every individual skill.
