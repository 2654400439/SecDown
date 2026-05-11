import argparse
import csv
import json
import re
import shutil
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_DIR = REPO_ROOT / "artifacts" / "skill_agent_logs" / "raw_tmp"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "artifacts" / "skill_agent_logs"

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

MODEL_ALIASES = {
    "gemini-3.1-pro": "gemini-3.1-pro-preview",
}

FILENAME_PATTERN = re.compile(r"^(?P<model>.+?)[_-](?P<task_type>[abcd])[_-](?P<task_num>\d+)_(?P<slug>.+)\.jsonl$")
TASKS_BY_TYPE = {"a": 10, "b": 5, "c": 5, "d": 5}


def rel_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def normalize_model(model: str) -> str:
    return MODEL_ALIASES.get(model, model)


def parse_log(path: Path) -> dict | None:
    match = FILENAME_PATTERN.match(path.name)
    if not match:
        return None
    data = match.groupdict()
    original_model = data["model"]
    model = normalize_model(original_model)
    task_type = f"type_{data['task_type']}"
    task_num = int(data["task_num"])
    return {
        "source_path": rel_path(path),
        "source_file": path,
        "friction": "self_signed",
        "original_model": original_model,
        "model": model,
        "task_type": task_type,
        "task_num": task_num,
        "task_slug": data["slug"],
        "epoch": 0,
        "run_id": f"{model}_{data['task_type']}_{task_num}_0",
        "rq1_self_signed_candidate": model in CANONICAL_RQ1_MODELS,
        "extra_material": model not in CANONICAL_RQ1_MODELS,
    }


def iter_logs(input_dir: Path) -> list[dict]:
    rows = []
    for path in sorted(input_dir.glob("*.jsonl")):
        parsed = parse_log(path)
        if parsed:
            rows.append(parsed)
        else:
            rows.append({"source_path": rel_path(path), "source_file": path, "parsed": False})
    return rows


def copy_log(row: dict, output_dir: Path, apply: bool) -> dict:
    if row.get("parsed") is False:
        return row
    dest_dir = output_dir / "raw" / row["friction"] / row["run_id"]
    row["dest_path"] = rel_path(dest_dir)
    row["has_session_log"] = row["source_file"].exists()
    if not apply:
        return row

    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(row["source_file"], dest_dir / "session.jsonl")
    metadata = {
        "paradigm": "skill_agent",
        "runner": "openclaw_tui",
        "model": row["model"],
        "original_model": row["original_model"],
        "task_type": row["task_type"],
        "task_num": row["task_num"],
        "task_id": f"{row['task_type']}_{row['task_num']}",
        "task_name": f"{row['task_num']}_{row['task_slug']}",
        "epoch": row["epoch"],
        "friction": row["friction"],
        "source_path": row["source_path"],
        "run_id": row["run_id"],
        "run_instance_id": row["run_id"],
        "status": "imported",
        "has_session_log": row["has_session_log"],
        "rq1_self_signed_candidate": row["rq1_self_signed_candidate"],
        "extra_material": row["extra_material"],
    }
    (dest_dir / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    return row


def expected_tasks() -> list[tuple[str, int]]:
    return [(f"type_{task_type}", task_num) for task_type, count in TASKS_BY_TYPE.items() for task_num in range(count)]


def build_coverage(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    parsed = [row for row in rows if row.get("parsed") is not False]
    available = {(row["model"], row["task_type"], row["task_num"]): row for row in parsed}
    models = sorted({row["model"] for row in parsed})
    matrix = []
    missing = []
    for model in models:
        for task_type, task_num in expected_tasks():
            row = available.get((model, task_type, task_num))
            item = {
                "friction": "self_signed",
                "model": model,
                "task_type": task_type,
                "task_num": task_num,
                "has_run": row is not None,
                "has_session_log": bool(row and row.get("has_session_log")),
                "rq1_self_signed_candidate": model in CANONICAL_RQ1_MODELS,
                "extra_material": model not in CANONICAL_RQ1_MODELS,
            }
            matrix.append(item)
            if not item["has_run"] or not item["has_session_log"]:
                missing.append(item)
    return matrix, missing


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in fieldnames})


def write_report(output_dir: Path, rows: list[dict], matrix: list[dict], missing: list[dict], apply: bool) -> None:
    parsed = [row for row in rows if row.get("parsed") is not False]
    canonical_rows = [row for row in matrix if row["rq1_self_signed_candidate"]]
    canonical_missing = [row for row in canonical_rows if not row["has_run"] or not row["has_session_log"]]
    summary = {
        "applied": apply,
        "total_logs": len(parsed),
        "friction_counts": dict(Counter(row["friction"] for row in parsed)),
        "models": sorted({row["model"] for row in parsed}),
        "original_models": sorted({row["original_model"] for row in parsed}),
        "tasks": len({(row["task_type"], row["task_num"]) for row in parsed}),
        "rq1_self_signed_canonical_cells": len(canonical_rows),
        "rq1_missing_or_no_session_cells": len(canonical_missing),
        "extra_models": sorted({row["model"] for row in parsed if row["extra_material"]}),
        "model_aliases": MODEL_ALIASES,
    }
    coverage_dir = output_dir / "coverage"
    coverage_dir.mkdir(parents=True, exist_ok=True)
    (coverage_dir / "skill_organization_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    lines = [
        "# Skill Agent Log Organization Report",
        "",
        f"- Applied file copy: {apply}",
        f"- Total imported logs: {summary['total_logs']}",
        f"- Friction counts: {summary['friction_counts']}",
        f"- Models: {summary['models']}",
        f"- Tasks covered: {summary['tasks']}",
        "",
        "## RQ Mapping",
        "",
        "- These logs correspond to the Skill Agent self-signed condition used for RQ1.",
        "- `gemini-3.1-pro` is normalized to `gemini-3.1-pro-preview` for consistency with the repository model list.",
        "- Runs from non-canonical model labels are retained as extra material.",
        "",
        f"- RQ1 missing/no-session cells: {summary['rq1_missing_or_no_session_cells']} / {summary['rq1_self_signed_canonical_cells']}",
        "",
        "See `skill_inventory.csv`, `skill_coverage_matrix.csv`, and `skill_missing_or_no_session.csv` for exact rows.",
    ]
    (coverage_dir / "skill_organization_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Organize imported Skill Agent OpenClaw logs into the artifact layout.")
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--apply", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    input_dir = args.input_dir if args.input_dir.is_absolute() else REPO_ROOT / args.input_dir
    output_dir = args.output_dir if args.output_dir.is_absolute() else REPO_ROOT / args.output_dir
    rows = [copy_log(row, output_dir, args.apply) for row in iter_logs(input_dir)]
    matrix, missing = build_coverage(rows)

    coverage_dir = output_dir / "coverage"
    write_csv(
        coverage_dir / "skill_inventory.csv",
        [row for row in rows if row.get("parsed") is not False],
        [
            "friction",
            "run_id",
            "original_model",
            "model",
            "task_type",
            "task_num",
            "task_slug",
            "epoch",
            "has_session_log",
            "rq1_self_signed_candidate",
            "extra_material",
            "source_path",
            "dest_path",
        ],
    )
    write_csv(
        coverage_dir / "skill_coverage_matrix.csv",
        matrix,
        ["friction", "model", "task_type", "task_num", "has_run", "has_session_log", "rq1_self_signed_candidate", "extra_material"],
    )
    write_csv(
        coverage_dir / "skill_missing_or_no_session.csv",
        missing,
        ["friction", "model", "task_type", "task_num", "has_run", "has_session_log", "rq1_self_signed_candidate", "extra_material"],
    )
    write_report(output_dir, rows, matrix, missing, args.apply)
    print(f"Skill log organization {'applied' if args.apply else 'dry-run'}: {len([r for r in rows if r.get('parsed') is not False])} logs.")
    print(f"Reports written to {coverage_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


