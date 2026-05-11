import argparse
import csv
import json
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_DIR = REPO_ROOT / "artifacts" / "code_agent_logs" / "raw_tmp"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "artifacts" / "code_agent_logs"

SOURCE_FRICTION_MAP = {
    "benchmark_results": "self_signed",
    "benchmark_results_0420": "self_signed",
    "benchmark_results_le_0422": "hostname_mismatch",
    "benchmark_results_root_0422": "local_issuer",
    "benchmark_results_443http_0422": "protocol_mismatch",
}

CORE_RQ2_MODELS = {
    "claude-opus-4-7",
    "gemini-3.1-pro-preview",
    "gpt-5.4",
    "gpt-5.4-nano",
    "kimi-k2.5",
    "qwen3.6-plus",
}

CANONICAL_RQ1_MODELS = {
    "gpt-5.4-nano",
    "gpt-5.4",
    "claude-sonnet-4-6",
    "claude-haiku-4-5",
    "gemini-3.1-pro-preview",
    "gemini-3.1-flash-lite-preview",
    "deepseek-v3.2",
    "kimi-k2.5",
    "gemma-4-31b-it",
    "claude-opus-4-7",
    "qwen3.6-plus",
    "glm-5.1",
    "grok-4-20-non-reasoning",
    "doubao-seed-2-0-pro",
    "minimax-m2.7",
    "mimo-v2-pro",
}

RUN_DIR_PATTERN = re.compile(r"^(?P<model>.+)_(?P<task_type>[abcd])_(?P<task_num>\d+)_(?P<epoch>\d+)$")
TASKS_BY_TYPE = {"a": 10, "b": 5, "c": 5, "d": 5}


def rel_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def parse_run_dir(path: Path) -> dict | None:
    match = RUN_DIR_PATTERN.match(path.name)
    if not match:
        return None
    data = match.groupdict()
    data["task_type"] = f"type_{data['task_type']}"
    data["task_num"] = int(data["task_num"])
    data["epoch"] = int(data["epoch"])
    return data


def find_first(path: Path, patterns: list[str]) -> Path | None:
    for pattern in patterns:
        matches = sorted(path.glob(pattern))
        if matches:
            return matches[0]
    return None


def iter_source_runs(input_dir: Path) -> list[dict]:
    rows = []
    for source_name, friction in SOURCE_FRICTION_MAP.items():
        source_dir = input_dir / source_name
        if not source_dir.exists():
            continue
        for run_dir in sorted(source_dir.iterdir()):
            if not run_dir.is_dir():
                continue
            parsed = parse_run_dir(run_dir)
            if not parsed:
                rows.append(
                    {
                        "source_dataset": source_name,
                        "source_path": rel_path(run_dir),
                        "friction": friction,
                        "parsed": False,
                    }
                )
                continue

            run_id = run_dir.name
            console = find_first(run_dir, [f"{run_id}_console.txt", "*_console.txt", "console.txt"])
            llm_log = find_first(run_dir, [f"{run_id}_llm.log", "*.log", "llm_req_res.log"])
            script = find_first(run_dir, [f"{run_id}_script.py", "*.py", "script.py"])

            rows.append(
                {
                    "source_dataset": source_name,
                    "source_path": rel_path(run_dir),
                    "source_dir": run_dir,
                    "friction": friction,
                    "parsed": True,
                    "run_id": run_id,
                    "model": parsed["model"],
                    "task_type": parsed["task_type"],
                    "task_num": parsed["task_num"],
                    "epoch": parsed["epoch"],
                    "has_console": console is not None,
                    "has_llm_log": llm_log is not None,
                    "has_script": script is not None,
                    "console_source": console,
                    "llm_log_source": llm_log,
                    "script_source": script,
                    "rq1_self_signed_candidate": friction == "self_signed" and parsed["model"] in CANONICAL_RQ1_MODELS,
                    "rq2_core_candidate": parsed["model"] in CORE_RQ2_MODELS,
                    "extra_material": not (
                        (friction == "self_signed" and parsed["model"] in CANONICAL_RQ1_MODELS)
                        or parsed["model"] in CORE_RQ2_MODELS
                    ),
                }
            )
    return rows


def copy_run(row: dict, output_dir: Path, apply: bool) -> dict:
    if not row.get("parsed"):
        return row

    dest_dir = output_dir / "raw" / row["friction"] / row["run_id"]
    row["dest_path"] = rel_path(dest_dir)

    if not apply:
        return row

    dest_dir.mkdir(parents=True, exist_ok=True)
    copy_map = [
        (row.get("console_source"), "console.txt"),
        (row.get("llm_log_source"), "llm_req_res.log"),
        (row.get("script_source"), "script.py"),
    ]
    for source, target_name in copy_map:
        if source:
            shutil.copy2(source, dest_dir / target_name)

    metadata = {
        "paradigm": "code_agent",
        "runner": "aider",
        "model": row["model"],
        "task_type": row["task_type"],
        "task_num": row["task_num"],
        "task_id": f"{row['task_type']}_{row['task_num']}",
        "epoch": row["epoch"],
        "friction": row["friction"],
        "source_dataset": row["source_dataset"],
        "source_path": row["source_path"],
        "run_id": row["run_id"],
        "run_instance_id": row["run_id"],
        "status": "imported",
        "has_console": row["has_console"],
        "has_llm_log": row["has_llm_log"],
        "has_script": row["has_script"],
        "rq1_self_signed_candidate": row["rq1_self_signed_candidate"],
        "rq2_core_candidate": row["rq2_core_candidate"],
        "extra_material": row["extra_material"],
    }
    (dest_dir / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    return row


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in fieldnames})


def expected_tasks() -> list[tuple[str, int]]:
    tasks = []
    for short_type, count in TASKS_BY_TYPE.items():
        for task_num in range(count):
            tasks.append((f"type_{short_type}", task_num))
    return tasks


def build_coverage(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    parsed_rows = [row for row in rows if row.get("parsed")]
    available = defaultdict(list)
    for row in parsed_rows:
        key = (row["friction"], row["model"], row["task_type"], row["task_num"])
        available[key].append(row)

    matrix = []
    missing = []
    frictions = sorted({row["friction"] for row in parsed_rows})
    models_by_friction = {
        friction: sorted({row["model"] for row in parsed_rows if row["friction"] == friction})
        for friction in frictions
    }

    for friction in frictions:
        for model in models_by_friction[friction]:
            for task_type, task_num in expected_tasks():
                runs = available.get((friction, model, task_type, task_num), [])
                has_any = bool(runs)
                has_console = any(row["has_console"] for row in runs)
                row = {
                    "friction": friction,
                    "model": model,
                    "task_type": task_type,
                    "task_num": task_num,
                    "has_run": has_any,
                    "has_console": has_console,
                    "run_count": len(runs),
                    "rq1_self_signed_candidate": friction == "self_signed" and model in CANONICAL_RQ1_MODELS,
                    "rq2_core_candidate": model in CORE_RQ2_MODELS,
                }
                matrix.append(row)
                if not has_any or not has_console:
                    missing.append(row)
    return matrix, missing


def write_report(output_dir: Path, rows: list[dict], matrix: list[dict], missing: list[dict], apply: bool) -> None:
    parsed = [row for row in rows if row.get("parsed")]
    source_counts = Counter(row["source_dataset"] for row in parsed)
    friction_counts = Counter(row["friction"] for row in parsed)
    missing_console = [row for row in parsed if not row["has_console"]]
    rq2_rows = [row for row in matrix if row["rq2_core_candidate"]]
    rq2_missing = [row for row in rq2_rows if not row["has_run"] or not row["has_console"]]
    rq1_rows = [row for row in matrix if row["rq1_self_signed_candidate"]]
    rq1_missing = [row for row in rq1_rows if not row["has_run"] or not row["has_console"]]

    summary = {
        "applied": apply,
        "total_runs": len(parsed),
        "source_counts": dict(source_counts),
        "friction_counts": dict(friction_counts),
        "models_by_friction": {
            friction: sorted({row["model"] for row in parsed if row["friction"] == friction})
            for friction in sorted(friction_counts)
        },
        "tasks_by_friction": {
            friction: len({(row["task_type"], row["task_num"]) for row in parsed if row["friction"] == friction})
            for friction in sorted(friction_counts)
        },
        "runs_missing_console": len(missing_console),
        "rq1_self_signed_canonical_cells": len(rq1_rows),
        "rq1_missing_or_no_console_cells": len(rq1_missing),
        "rq2_core_cells": len(rq2_rows),
        "rq2_missing_or_no_console_cells": len(rq2_missing),
        "core_rq2_models": sorted(CORE_RQ2_MODELS),
        "canonical_rq1_models": sorted(CANONICAL_RQ1_MODELS),
    }
    coverage_dir = output_dir / "coverage"
    coverage_dir.mkdir(parents=True, exist_ok=True)
    (coverage_dir / "organization_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# Code Agent Log Organization Report",
        "",
        f"- Applied file copy: {apply}",
        f"- Total parsed runs: {summary['total_runs']}",
        f"- Source counts: {summary['source_counts']}",
        f"- Friction counts: {summary['friction_counts']}",
        f"- Runs missing console.txt after import mapping: {summary['runs_missing_console']}",
        "",
        "## RQ Mapping",
        "",
        "- RQ1 uses canonical Code Agent runs under `raw/self_signed/`.",
        "- RQ2 uses the six core models across all four friction profiles.",
        "- Runs outside these sets are retained as extra material.",
        "",
        "## Coverage Caveat",
        "",
        f"- RQ1 missing/no-console cells: {summary['rq1_missing_or_no_console_cells']} / {summary['rq1_self_signed_canonical_cells']}",
        f"- RQ2 missing/no-console cells: {summary['rq2_missing_or_no_console_cells']} / {summary['rq2_core_cells']}",
        "",
        "See `inventory.csv`, `coverage_matrix.csv`, and `missing_or_no_console.csv` for exact rows.",
    ]
    (coverage_dir / "organization_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Organize imported Code Agent logs into the artifact layout.")
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--apply", action="store_true", help="Copy files into raw/<friction>/<run_id>. Without this flag, only writes reports.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    input_dir = args.input_dir if args.input_dir.is_absolute() else REPO_ROOT / args.input_dir
    output_dir = args.output_dir if args.output_dir.is_absolute() else REPO_ROOT / args.output_dir

    rows = iter_source_runs(input_dir)
    rows = [copy_run(row, output_dir, args.apply) for row in rows]
    matrix, missing = build_coverage(rows)

    inventory_fields = [
        "source_dataset",
        "friction",
        "run_id",
        "model",
        "task_type",
        "task_num",
        "epoch",
        "has_console",
        "has_llm_log",
        "has_script",
        "rq1_self_signed_candidate",
        "rq2_core_candidate",
        "extra_material",
        "source_path",
        "dest_path",
    ]
    coverage_fields = [
        "friction",
        "model",
        "task_type",
        "task_num",
        "has_run",
        "has_console",
        "run_count",
        "rq1_self_signed_candidate",
        "rq2_core_candidate",
    ]
    coverage_dir = output_dir / "coverage"
    write_csv(coverage_dir / "inventory.csv", [row for row in rows if row.get("parsed")], inventory_fields)
    write_csv(coverage_dir / "coverage_matrix.csv", matrix, coverage_fields)
    write_csv(coverage_dir / "missing_or_no_console.csv", missing, coverage_fields)
    write_report(output_dir, rows, matrix, missing, args.apply)

    parsed_count = sum(1 for row in rows if row.get("parsed"))
    missing_console_count = sum(1 for row in rows if row.get("parsed") and not row["has_console"])
    mode = "applied" if args.apply else "dry-run"
    print(f"Organization {mode}: {parsed_count} parsed runs, {missing_console_count} without console files.")
    print(f"Reports written to {coverage_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


