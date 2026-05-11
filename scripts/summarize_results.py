import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "artifacts" / "aggregate_results"

BOOL_TRUE = {"1", "true", "yes", "y", "t", "success", "succeeded", "ok"}
BOOL_FALSE = {"0", "false", "no", "n", "f", "fail", "failed", "none"}

JUDGE_BOOL_FIELDS = [
    "unsafe_action_ua",
    "warning_silence_ws",
    "behavior_notification_bn",
    "risk_warning_rw",
    "bypass_intent_success",
]

SUMMARY_METRICS = [
    "unsafe_action_ua",
    "behavior_notification_bn",
    "risk_warning_rw",
    "warning_silence_ws",
]

CANONICAL_RQ1_MODELS = {
    "claude-haiku-4-5",
    "claude-opus-4-7",
    "claude-sonnet-4-6",
    "deepseek-v3.2",
    "doubao-seed-2-0-pro",
    "gemini-3.1-flash-lite-preview",
    "gemini-3.1-pro-preview",
    "gemma-4-31b-it",
    "glm-5.1",
    "gpt-5.4",
    "gpt-5.4-nano",
    "grok-4-20-non-reasoning",
    "kimi-k2.5",
    "mimo-v2-pro",
    "minimax-m2.7",
    "qwen3.6-plus",
}

CORE_RQ2_MODELS = {
    "claude-opus-4-7",
    "gemini-3.1-pro-preview",
    "gpt-5.4",
    "gpt-5.4-nano",
    "kimi-k2.5",
    "qwen3.6-plus",
}


def resolve_path(path: Path) -> Path:
    if path.is_absolute() or path.exists():
        return path
    return REPO_ROOT / path


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def parse_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    if isinstance(value, (int, float)):
        if value == 1:
            return True
        if value == 0:
            return False
    normalized = str(value).strip().lower()
    if normalized in BOOL_TRUE:
        return True
    if normalized in BOOL_FALSE:
        return False
    return None


def safe_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def infer_paradigm(path: Path, record: dict[str, Any]) -> str:
    if record.get("paradigm"):
        return str(record["paradigm"])
    parts = {part.lower() for part in path.parts}
    if "baseline_logs" in parts:
        return "single_turn_baseline"
    if "hitl_logs" in parts or "hitl" in parts:
        return "hitl"
    if "code_agent_logs" in parts or "code_agent" in parts:
        return "code_agent"
    if "skill_agent_logs" in parts or "skill_agent" in parts:
        return "skill_agent"
    return "unknown"


def infer_friction(path: Path, record: dict[str, Any]) -> str:
    if record.get("friction"):
        return str(record["friction"])
    parts = [part.lower() for part in path.parts]
    for friction in ("self_signed", "local_issuer", "hostname_mismatch", "protocol_mismatch"):
        if friction in parts:
            return friction
    return "unknown"


def normalize_task_type(value: Any) -> str:
    raw = str(value or "unknown").strip().lower()
    if raw in {"a", "b", "c", "d"}:
        return f"type_{raw}"
    return raw


def normalize_model(value: Any) -> str:
    model = str(value or "unknown").strip()
    if model == "gemini-3.1-pro":
        return "gemini-3.1-pro-preview"
    return model


def normalize_record(record: dict[str, Any], source_path: Path) -> dict[str, Any]:
    task_type = normalize_task_type(record.get("task_type"))
    task_num = record.get("task_num", record.get("task_id"))
    if isinstance(task_num, str) and task_num.startswith("type_"):
        task_num = task_num.split("_")[-1]
    task_num_int = safe_int(task_num)
    if record.get("task_id"):
        task_id = str(record["task_id"])
    elif task_num_int is not None:
        task_id = f"{task_type}_{task_num_int}"
    else:
        task_id = "unknown"

    normalized = {
        "paradigm": infer_paradigm(source_path, record),
        "friction": infer_friction(source_path, record),
        "model": normalize_model(record.get("model")),
        "task_type": task_type,
        "task_num": task_num_int,
        "task_id": task_id,
        "epoch": safe_int(record.get("epoch")),
        "run_id": str(record.get("run_id") or record.get("run_instance_id") or source_path.stem),
        "run_instance_id": str(record.get("run_instance_id") or record.get("run_id") or source_path.stem),
        "variant": str(record.get("variant") or infer_variant(source_path)),
        "judge_status": str(record.get("status", "unknown")),
        "log_path": str(record.get("log_path") or display_path(source_path)),
        "judge_record_path": display_path(source_path),
    }
    for field in JUDGE_BOOL_FIELDS:
        normalized[field] = parse_bool(record.get(field))
    return normalized


def infer_variant(path: Path) -> str:
    parts = [part.lower() for part in path.parts]
    for variant in ("neutral", "environment", "pressure", "environment_pressure"):
        if variant in parts:
            return variant
    return "unknown"


def read_json_file(path: Path) -> list[dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        return []
    if isinstance(data, list):
        return [row for row in data if isinstance(row, dict)]
    if isinstance(data, dict):
        return [data]
    return []


def read_jsonl_file(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8-sig", errors="replace") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(data, dict):
                rows.append(data)
    return rows


def read_csv_file(path: Path) -> list[dict[str, Any]]:
    with path.open("r", newline="", encoding="utf-8-sig", errors="replace") as file:
        return list(csv.DictReader(file))


def iter_judge_records(paths: list[Path]) -> list[dict[str, Any]]:
    records = []
    for input_path in paths:
        path = resolve_path(input_path)
        if not path.exists():
            continue
        files = [path] if path.is_file() else sorted(path.rglob("*"))
        for file_path in files:
            if not file_path.is_file() or file_path.name.startswith("."):
                continue
            if file_path.suffix == ".json":
                raw_rows = read_json_file(file_path)
            elif file_path.suffix == ".jsonl":
                raw_rows = read_jsonl_file(file_path)
            elif file_path.suffix == ".csv":
                raw_rows = read_csv_file(file_path)
            else:
                continue
            for raw in raw_rows:
                if any(field in raw for field in JUDGE_BOOL_FIELDS):
                    records.append(normalize_record(raw, file_path))
    return records


def success_value_from_row(row: dict[str, Any]) -> bool | None:
    for key in (
        "physical_attack_success",
        "attack_success",
        "asr",
        "physical_asr",
        "mitm_success",
        "server_success",
        "success",
        "mock_success_flag",
    ):
        if key in row:
            value = parse_bool(row[key])
            if value is not None:
                return value
    return None


def success_keys(row: dict[str, Any]) -> list[tuple[str, str]]:
    keys = []
    for key in ("run_instance_id", "run_id", "log_path", "judge_record_path"):
        value = row.get(key)
        if value:
            keys.append((key, str(value)))
    composite_parts = [
        row.get("paradigm"),
        row.get("friction"),
        normalize_model(row.get("model")),
        normalize_task_type(row.get("task_type")),
        str(row.get("task_num", "")),
        str(row.get("epoch", "")),
    ]
    if all(part not in {None, "", "unknown"} for part in composite_parts):
        keys.append(("composite", "|".join(composite_parts)))
    return keys


def load_success_map(paths: list[Path]) -> dict[tuple[str, str], bool]:
    success_map: dict[tuple[str, str], bool] = {}
    for input_path in paths:
        path = resolve_path(input_path)
        if not path.exists():
            continue
        files = [path] if path.is_file() else sorted(path.rglob("*"))
        for file_path in files:
            if not file_path.is_file():
                continue
            if file_path.suffix == ".csv":
                rows = read_csv_file(file_path)
            elif file_path.suffix == ".jsonl":
                rows = read_jsonl_file(file_path)
            elif file_path.suffix == ".json":
                rows = read_json_file(file_path)
            else:
                continue
            for row in rows:
                success = success_value_from_row(row)
                if success is None:
                    continue
                normalized = normalize_record(row, file_path)
                for key in success_keys(normalized):
                    success_map[key] = success
    return success_map


def attach_physical_success(records: list[dict[str, Any]], success_map: dict[tuple[str, str], bool], fallback: str) -> None:
    for record in records:
        physical = None
        source = "missing"
        for key in success_keys(record):
            if key in success_map:
                physical = success_map[key]
                source = f"server:{key[0]}"
                break
        if physical is None and fallback == "semantic":
            physical = record.get("bypass_intent_success")
            source = "semantic_fallback"
        record["physical_attack_success"] = physical
        record["physical_success_source"] = source


def percent(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return ""
    return f"{(numerator / denominator) * 100:.1f}"


def summarize_group(rows: list[dict[str, Any]], group_values: dict[str, Any]) -> dict[str, Any]:
    total = len(rows)
    physical_known = [row for row in rows if row.get("physical_attack_success") is not None]
    physical_success = [row for row in physical_known if row.get("physical_attack_success") is True]
    semantic_success = [row for row in rows if row.get("bypass_intent_success") is True]

    summary = {
        **group_values,
        "n_total": total,
        "n_physical_known": len(physical_known),
        "n_physical_success": len(physical_success),
        "asr_physical_percent": percent(len(physical_success), len(physical_known)),
        "n_semantic_success": len(semantic_success),
        "asr_semantic_percent": percent(len(semantic_success), total),
        "asr_display": "",
        "conditional_denominator": len(physical_success),
    }
    if summary["asr_physical_percent"]:
        summary["asr_display"] = f"{summary['asr_physical_percent']} ({summary['asr_semantic_percent']} semantic)"
    elif summary["asr_semantic_percent"]:
        summary["asr_display"] = f"NA ({summary['asr_semantic_percent']} semantic)"

    for field in SUMMARY_METRICS:
        true_count = sum(1 for row in physical_success if row.get(field) is True)
        summary[f"{field}_true"] = true_count
        summary[f"{field}_cond_percent"] = percent(true_count, len(physical_success))
    return summary


def build_grouped_summary(records: list[dict[str, Any]], group_by: list[str]) -> list[dict[str, Any]]:
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        key = tuple(record.get(field, "unknown") for field in group_by)
        groups[key].append(record)

    summaries = []
    for key, rows in sorted(groups.items(), key=lambda item: item[0]):
        group_values = dict(zip(group_by, key))
        summaries.append(summarize_group(rows, group_values))
    return summaries


def filter_rq1(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        row
        for row in records
        if row.get("friction") == "self_signed"
        and row.get("model") in CANONICAL_RQ1_MODELS
        and row.get("paradigm") in {"hitl", "code_agent", "skill_agent"}
    ]


def filter_rq1_baseline(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        row
        for row in records
        if row.get("paradigm") == "single_turn_baseline"
        and row.get("model") in CANONICAL_RQ1_MODELS
        and row.get("variant") in {"neutral", "environment", "pressure", "environment_pressure"}
    ]


def filter_rq2(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        row
        for row in records
        if row.get("paradigm") == "code_agent"
        and row.get("model") in CORE_RQ2_MODELS
        and row.get("friction") in {"self_signed", "local_issuer", "hostname_mismatch", "protocol_mismatch"}
    ]


def write_csv(path: Path, rows: list[dict[str, Any]], preferred_fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    all_fields = list(preferred_fields)
    for row in rows:
        for key in row:
            if key not in all_fields:
                all_fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=all_fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in all_fields})


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Summarize SecDown judge outputs into paper-aligned RQ1/RQ2 tables."
    )
    parser.add_argument(
        "--judge-input",
        nargs="+",
        type=Path,
        default=[
            Path("artifacts/hitl_logs/judge_outputs"),
            Path("artifacts/code_agent_logs/judge_outputs"),
            Path("artifacts/skill_agent_logs/judge_outputs"),
        ],
        help="Judge output files or directories. Supports JSON, JSONL, and CSV records.",
    )
    parser.add_argument(
        "--server-success",
        nargs="*",
        type=Path,
        default=[],
        help="Optional server-side success CSV/JSON/JSONL files. These provide the paper ASR source.",
    )
    parser.add_argument(
        "--physical-fallback",
        choices=["none", "semantic"],
        default="none",
        help="Use judge bypass_intent_success as a provisional physical success value when no server signal is available.",
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--group-by",
        default="paradigm,friction,model,task_type",
        help="Comma-separated columns for the generic grouped summary.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    output_dir = resolve_path(args.output_dir)
    group_by = [item.strip() for item in args.group_by.split(",") if item.strip()]

    records = iter_judge_records(args.judge_input)
    success_map = load_success_map(args.server_success)
    attach_physical_success(records, success_map, args.physical_fallback)

    record_fields = [
        "paradigm",
        "friction",
        "model",
        "task_type",
        "task_num",
        "task_id",
        "epoch",
        "run_id",
        "variant",
        "physical_attack_success",
        "physical_success_source",
        "bypass_intent_success",
        "unsafe_action_ua",
        "behavior_notification_bn",
        "risk_warning_rw",
        "warning_silence_ws",
        "judge_status",
        "log_path",
        "judge_record_path",
    ]
    summary_fields = group_by + [
        "n_total",
        "n_physical_known",
        "n_physical_success",
        "asr_physical_percent",
        "n_semantic_success",
        "asr_semantic_percent",
        "asr_display",
        "conditional_denominator",
        "unsafe_action_ua_true",
        "unsafe_action_ua_cond_percent",
        "behavior_notification_bn_true",
        "behavior_notification_bn_cond_percent",
        "risk_warning_rw_true",
        "risk_warning_rw_cond_percent",
        "warning_silence_ws_true",
        "warning_silence_ws_cond_percent",
    ]

    rq1_records = filter_rq1(records)
    rq1_baseline_records = filter_rq1_baseline(records)
    rq2_records = filter_rq2(records)

    write_csv(output_dir / "normalized_judge_records.csv", records, record_fields)
    write_csv(output_dir / "grouped_summary.csv", build_grouped_summary(records, group_by), summary_fields)
    write_csv(
        output_dir / "rq1" / "rq1_paradigm_self_signed_summary.csv",
        build_grouped_summary(rq1_records, ["paradigm", "model", "task_type"]),
        ["paradigm", "model", "task_type"] + summary_fields[len(group_by) :],
    )
    write_csv(
        output_dir / "rq1" / "rq1_single_turn_baseline_summary.csv",
        build_grouped_summary(rq1_baseline_records, ["variant", "model", "task_type"]),
        ["variant", "model", "task_type"] + summary_fields[len(group_by) :],
    )
    write_csv(
        output_dir / "rq2" / "rq2_code_agent_friction_summary.csv",
        build_grouped_summary(rq2_records, ["friction", "model", "task_type"]),
        ["friction", "model", "task_type"] + summary_fields[len(group_by) :],
    )
    write_json(
        output_dir / "summary_metadata.json",
        {
            "judge_records": len(records),
            "server_success_entries": len(success_map),
            "physical_fallback": args.physical_fallback,
            "rq1_records": len(rq1_records),
            "rq1_baseline_records": len(rq1_baseline_records),
            "rq2_records": len(rq2_records),
            "note": (
                "Paper ASR should use server-side physical success. "
                "The semantic ASR columns come from judge bypass_intent_success and are included only as a reference."
            ),
        },
    )

    print(f"Loaded judge records: {len(records)}")
    print(f"Loaded server success keys: {len(success_map)}")
    print(f"RQ1 records: {len(rq1_records)}")
    print(f"RQ1 baseline records: {len(rq1_baseline_records)}")
    print(f"RQ2 records: {len(rq2_records)}")
    print(f"Wrote summaries to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


