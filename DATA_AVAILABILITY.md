# Data Availability

Large experiment logs and external data are distributed through Zenodo rather than committed to this GitHub repository.

```text
Zenodo record: https://zenodo.org/records/20115421
DOI: https://doi.org/10.5281/zenodo.20115421
```

The Zenodo record contains:

- HITL execution logs and coverage metadata.
- Code Agent execution logs and coverage metadata.
- Skill Agent execution logs and coverage metadata.
- The OpenClaw skills snapshot used for the ecosystem audit, downloaded from the public OpenClaw GitHub repository on 2026-04-25.

This repository keeps only source code, benchmark tasks, prepared Skill Agent examples, documentation, and empty output locations. Generated logs should be written under `artifacts/` locally and kept out of Git unless they are small, sanitized examples.
