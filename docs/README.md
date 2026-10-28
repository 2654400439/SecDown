# Paper and supplementary material

**Silent Surrender: Measuring MitM-Induced TLS Downgrades in LLM Agents**

Accepted at NDSS 2027.

- [Supplementary material (PDF)](SecDown-Supplementary-Material.pdf)
- [Editable LaTeX source](SecDown-Supplementary-Material-source.zip)
- [Complete task inventory (CSV)](supplementary-data/task_inventory.csv)
- [Representative task schema (JSON)](supplementary-data/example_task_schema.json)
- [Prompt-variant core instructions (JSON)](supplementary-data/prompt_variants.json)
- [Conference paper DOI](https://doi.org/10.14722/ndss.2027.230944)

Supplement version: **2.0 - October 29, 2026**. Two-column format, 18 pages.

The report introduces the measurement setting before presenting the detailed material documented in the accepted revised manuscript. It includes definitions and reading guidance so the supporting experiments can be understood without first reading the full conference paper.

| Section | Content |
|---|---|
| S1 | Study overview, threat setting, measurement interpretation, and reading guide |
| S2 | All 25 benchmark tasks, endpoint specifications, backend types, and a representative JSON schema |
| S3 | Agent paradigms, execution budgets, framework versions, and the 16-model snapshot ledger |
| S4 | Task scaffolds, evaluation metrics and denominators, human validation, and the automated evaluator prompt |
| S5 | TLS bypass controls, four failure profiles, client error signatures, and selective-targeting measurements |
| S6 | Task-set-size sensitivity, P1-P3 prompt variants, and complete per-model prompt results |
| S7 | Matched coding-harness comparison and post-error continuation analysis |
| S8 | Browser implementations, matched results, recovery mechanisms, and HSTS analysis |
| S9 | Commercial web-agent setup, observations, and measurement limits |
| S10 | Three annotated execution cases |
| S11 | Extended related work |

The CSV and JSON files are readable exports of the report's inventory, example schema, and prompt-variant core instructions. They do not replace the executable benchmark task files or agent runners in the repository. The PDF contains the complete documented scaffolds and their explanatory annotations. Execution cases are excerpts with the original redactions; they are not complete raw logs.

All report numbering is independent of the conference paper. Model and framework versions describe the configurations measured in the study.

Version 2.0 restores the accepted manuscript's single-column and full-width figure/table styles, adds concise background and interpretation guidance, and retains all original table data, documented prompt wording, and execution-case excerpts.

Authors: Yifei Cheng, Xinhao Deng, Yujia Zhu, Baiyang Li, Yaochen Ren, Gang Xiong, Zhen Li, Jiang Xie, Xixun Lin, and Qingyun Liu.

Corresponding author: Yujia Zhu, zhuyujia@iie.ac.cn.
