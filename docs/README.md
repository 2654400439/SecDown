# Paper and supplementary material

**Silent Surrender: Measuring MitM-Induced TLS Downgrades in LLM Agents**

Accepted at NDSS 2027.

- [Supplementary material (PDF)](SecDown-Supplementary-Material.pdf)
- [Editable LaTeX source](SecDown-Supplementary-Material-source.zip)
- [Complete task inventory (CSV)](supplementary-data/task_inventory.csv)
- [Representative task schema (JSON)](supplementary-data/example_task_schema.json)
- [Prompt-variant core instructions (JSON)](supplementary-data/prompt_variants.json)
- [Conference paper DOI](https://doi.org/10.14722/ndss.2027.230944)

Supplement version: **1.0 — October 28, 2026**.

The author-provided supplement contains the detailed material documented in the accepted revised manuscript:

| Section | Content |
|---|---|
| S1 | All 25 benchmark tasks, endpoint specifications, backend types, and a representative JSON schema |
| S2 | Agent paradigms, execution budgets, framework versions, and the 16-model snapshot ledger |
| S3 | Task scaffolds, evaluation metrics, human validation, and the automated evaluator prompt |
| S4 | TLS bypass controls, client error signatures, and selective-targeting measurements |
| S5 | Task-set-size sensitivity, P1–P3 prompt variants, and complete per-model prompt results |
| S6 | Matched coding-harness comparison and post-error continuation analysis |
| S7 | Browser implementations, matched results, recovery mechanisms, and HSTS analysis |
| S8 | Commercial web-agent setup, observations, and measurement limits |
| S9 | Three annotated execution cases |
| S10 | Extended related work |

The CSV and JSON files are readable exports of the report's inventory, example schema, and prompt-variant core instructions. They do not replace the executable benchmark task files or agent runners in the repository. The PDF contains the complete documented scaffolds and their explanatory annotations. Execution cases are excerpts with the original redactions; they are not complete raw logs.

All report numbering is independent of the conference paper. Model and framework versions describe the configurations measured in the study.

Authors: Yifei Cheng, Xinhao Deng, Yujia Zhu, Baiyang Li, Yaochen Ren, Gang Xiong, Zhen Li, Jiang Xie, Xixun Lin, and Qingyun Liu.

Corresponding author: Yujia Zhu, zhuyujia@iie.ac.cn.
