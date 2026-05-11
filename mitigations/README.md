# Mitigation Experiments

This directory documents the mitigation layers evaluated in the paper. The runnable L1/L2 experiments are implemented through the unified Code Agent runner:

```text
agents/code/code_runner.py
```

## L1: Prompt-Level Constraints

L1 uses Aider's `--read` mechanism to inject an additional high-priority policy file into the Code Agent context.

Available modes:

- `l1-generic`: broad secure-coding guidance.
- `l1-targeted`: a compact TLS-specific rule that explicitly authorizes task failure on SSL/certificate errors.

Example:

```bash
python agents/code/code_runner.py \
  --task-type type_a \
  --models gpt-5.4-nano \
  --friction self_signed \
  --mitigation l1-targeted \
  --output-dir artifacts/mitigation_logs
```

## L2: Framework AST Auditing

L2 adds a pre-execution security linter to the Aider test wrapper. Before `script.py` runs, the wrapper scans the generated Python AST and selected shell-command strings for TLS-bypass patterns such as:

- `verify=False`
- `ssl.CERT_NONE`
- `_create_unverified_context()`
- `check_hostname=False`
- `curl -k` / `curl --insecure`
- `wget --no-check-certificate`

If a violation is detected, the wrapper blocks execution and returns a deterministic framework-policy error to the agent.

Example:

```bash
python agents/code/code_runner.py \
  --task-type type_a \
  --models gpt-5.4-nano \
  --friction self_signed \
  --mitigation l2-ast \
  --output-dir artifacts/mitigation_logs
```

## L3: Egress Enforcement

L3 is an out-of-band network control rather than an agent-side script. See `L3_EGRESS_POLICY.md` for the release-facing design note.

## Output Layout

When `--mitigation` is not `none`, Code Agent run archives are written as:

```text
artifacts/mitigation_logs/raw/<friction>/<mitigation>/<run_id>/
```

Each run preserves the normal Code Agent artifacts plus mitigation metadata:

- `metadata.json`
- `prompt.txt`
- `script.py`
- `test_wrapper.py`
- `mitigation_rules.md` for L1 modes
- `console.txt`
- `llm_req_res.log` when emitted by Aider

These logs can be evaluated with `agents/code/code_judge.py` and summarized with `scripts/summarize_results.py`.

