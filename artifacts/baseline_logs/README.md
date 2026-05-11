# Single-Turn Baseline Logs

This directory stores the RQ1 single-turn code-generation baseline. Unlike the HITL, Code Agent, and Skill Agent paradigms, this baseline only asks the model to produce code once. It does not execute the generated script and therefore does not provide a physical MitM-server ASR signal.

Prompt variants:

- `neutral`: base task prompt.
- `environment`: base task prompt plus an environment-friction note.
- `pressure`: base task prompt plus a time-sensitive task-pressure note.
- `environment_pressure`: optional combined variant, disabled by default.

Recommended layout:

```text
baseline_logs/
+-- raw/
|   +-- neutral/
|   +-- environment/
|   +-- pressure/
+-- summary.jsonl
+-- README.md
```

Use `agents/hitl/baseline_runner.py` to generate logs. Use `agents/hitl/hitl_judge.py` to evaluate the generated code for semantic metrics such as `unsafe_action_ua`, `behavior_notification_bn`, `risk_warning_rw`, and `warning_silence_ws`.

