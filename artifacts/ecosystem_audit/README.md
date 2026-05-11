# Ecosystem Audit Outputs

This directory is reserved for derived ecosystem-analysis outputs.

The complete OpenClaw skills snapshot used in the paper is distributed through Zenodo:

```text
https://zenodo.org/records/20115421
https://doi.org/10.5281/zenodo.20115421
```

After downloading and extracting that snapshot, run:

```bash
python analysis/ecosystem/openclaw_skills_analysis.py \
  --skills-root /path/to/extracted/openclaw/skills \
  --output-dir artifacts/ecosystem_audit/openclaw_skills
```

Expected generated files:

```text
openclaw_skills/
  summary.json
  summary.csv
  skill_inventory.csv
```
