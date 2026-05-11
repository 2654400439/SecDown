import argparse
import csv
import json
import os
import re
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "artifacts" / "ecosystem_audit" / "openclaw_skills"

EASY_CLI_PATTERN = re.compile(r"(?i)\b(curl|wget|git)\b")
OTHER_CLI_PATTERN = re.compile(r"(?i)\b(ssh|sftp|ftp|scp|rsync|aws|gcloud|azure|kubectl|npm|yarn)\b")
SHELL_URL_PATTERN = re.compile(r"https?://[A-Za-z0-9.-]+")

NETWORK_PATTERNS = {
    "Python": re.compile(
        r"(?i)(import\s+(requests|urllib|aiohttp|httpx|socket|http\.client)|from\s+(requests|urllib|aiohttp|httpx|socket|http)\s+import)"
    ),
    "JavaScript": re.compile(
        r"(?i)(require\([\"'](axios|node-fetch|http|https|request|got|superagent)[\"']\)|import\s+.*\s+from\s+[\"'](axios|node-fetch|http|https)[\"']|\bfetch\()"
    ),
    "TypeScript": re.compile(r"(?i)(import\s+.*\s+from\s+[\"'](axios|node-fetch|http|https)[\"']|\bfetch\()"),
    "Ruby": re.compile(r"(?i)(require\s+[\"'](net/http|uri|open-uri|rest-client|httparty)[\"'])"),
    "PowerShell": re.compile(r"(?i)(Invoke-WebRequest|Invoke-RestMethod|System\.Net\.WebClient)"),
    "Go": re.compile(r"(?i)(\"net/http\")"),
    "Java": re.compile(r"(?i)import\s+(java\.net|javax\.net|org\.apache\.http|okhttp3)"),
    "C++": re.compile(r"(?i)#include\s+<(curl/curl\.h|sys/socket\.h|winsock2\.h|boost/asio\.hpp)>"),
    "C": re.compile(r"(?i)#include\s+<(curl/curl\.h|sys/socket\.h|winsock2\.h)>"),
}

INSECURE_PATTERNS = {
    "Python": re.compile(r"(?i)(verify\s*=\s*False|verify\s*=\s*0|ssl\._create_unverified_context)"),
    "JS_TS": re.compile(r"(?i)(rejectUnauthorized\s*:\s*false|NODE_TLS_REJECT_UNAUTHORIZED\s*=\s*[\"']?0[\"']?)"),
    "CLI": re.compile(r"(?i)(curl\s+.*(-k|--insecure)|wget\s+.*--no-check-certificate|git\s+.*http\.sslVerify=false)"),
}

LANG_BY_EXTENSION = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".sh": "Shell",
    ".bash": "Shell",
    ".go": "Go",
    ".java": "Java",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".c": "C",
    ".rb": "Ruby",
    ".ps1": "PowerShell",
}


@dataclass
class SkillFinding:
    skill_path: str
    is_valid: bool
    is_network: bool
    level: int
    is_pre_insecure: bool
    network_langs: list[str]
    all_langs: list[str]


def resolve_path(path: Path) -> Path:
    if path.is_absolute() or path.exists():
        return path
    return REPO_ROOT / path


def display_path(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def iter_skill_dirs(skills_root: Path) -> list[Path]:
    return sorted(path.parent for path in skills_root.rglob("SKILL.md"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def process_skill(args: tuple[str, str]) -> dict[str, Any]:
    raw_skill_path, raw_root = args
    skill_path = Path(raw_skill_path)
    root = Path(raw_root)
    skill_md_path = skill_path / "SKILL.md"

    result = {
        "skill_path": display_path(skill_path, root),
        "is_valid": False,
        "is_network": False,
        "level": 0,
        "is_pre_insecure": False,
        "network_langs": set(),
        "all_langs": set(),
    }
    if not skill_md_path.exists():
        return serialize_result(result)

    result["is_valid"] = True
    has_easy_script = False
    has_hard_script = False
    has_easy_cli = False
    has_other_cli = False

    try:
        content = read_text(skill_md_path)
        if EASY_CLI_PATTERN.search(content):
            result["is_network"] = True
            has_easy_cli = True
            result["network_langs"].add("Markdown-EasyCLI")
            if INSECURE_PATTERNS["CLI"].search(content):
                result["is_pre_insecure"] = True
        elif OTHER_CLI_PATTERN.search(content):
            result["is_network"] = True
            has_other_cli = True
            result["network_langs"].add("Markdown-OtherCLI")
    except OSError:
        pass

    for child_root, _dirs, files in os.walk(skill_path):
        for filename in files:
            if filename == "SKILL.md":
                continue
            file_path = Path(child_root) / filename
            lang = LANG_BY_EXTENSION.get(file_path.suffix.lower())
            if not lang:
                continue

            result["all_langs"].add(lang)
            try:
                code = read_text(file_path)
            except OSError:
                continue

            if lang == "Shell":
                if EASY_CLI_PATTERN.search(code):
                    result["is_network"] = True
                    has_easy_cli = True
                    result["network_langs"].add(lang)
                    if INSECURE_PATTERNS["CLI"].search(code):
                        result["is_pre_insecure"] = True
                elif OTHER_CLI_PATTERN.search(code) or SHELL_URL_PATTERN.search(code):
                    result["is_network"] = True
                    has_other_cli = True
                    result["network_langs"].add(lang)
                continue

            if lang in NETWORK_PATTERNS and NETWORK_PATTERNS[lang].search(code):
                result["is_network"] = True
                result["network_langs"].add(lang)
                if lang in {"Python", "JavaScript", "TypeScript", "Ruby", "PowerShell"}:
                    has_easy_script = True
                else:
                    has_hard_script = True

                if lang == "Python" and INSECURE_PATTERNS["Python"].search(code):
                    result["is_pre_insecure"] = True
                elif lang in {"JavaScript", "TypeScript"} and INSECURE_PATTERNS["JS_TS"].search(code):
                    result["is_pre_insecure"] = True

    if result["is_network"]:
        if has_easy_script or has_easy_cli:
            result["level"] = 1
        elif has_hard_script or has_other_cli:
            result["level"] = 2

    return serialize_result(result)


def serialize_result(result: dict[str, Any]) -> dict[str, Any]:
    serialized = dict(result)
    serialized["network_langs"] = sorted(serialized["network_langs"])
    serialized["all_langs"] = sorted(serialized["all_langs"])
    return serialized


def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    stats = Counter()
    network_lang_counter = Counter()
    all_lang_counter = Counter()

    for result in results:
        if result["is_valid"]:
            stats["valid_skills"] += 1
        if result["is_network"]:
            stats["network_skills"] += 1
        if result["level"] == 1:
            stats["level_1"] += 1
        elif result["level"] == 2:
            stats["level_2"] += 1
        if result["is_pre_insecure"]:
            stats["pre_insecure_count"] += 1
        for lang in result["network_langs"]:
            network_lang_counter[lang] += 1
        for lang in result["all_langs"]:
            all_lang_counter[lang] += 1

    valid = stats["valid_skills"]
    network = stats["network_skills"]
    return {
        "total_skill_dirs": len(results),
        "valid_skills": valid,
        "network_skills": network,
        "network_skill_percent": round((network / valid) * 100, 2) if valid else 0.0,
        "level_1": stats["level_1"],
        "level_1_percent_of_network": round((stats["level_1"] / network) * 100, 2) if network else 0.0,
        "level_2": stats["level_2"],
        "level_2_percent_of_network": round((stats["level_2"] / network) * 100, 2) if network else 0.0,
        "pre_insecure_count": stats["pre_insecure_count"],
        "pre_insecure_percent_of_network": round((stats["pre_insecure_count"] / network) * 100, 2) if network else 0.0,
        "network_language_counts": dict(network_lang_counter.most_common()),
        "all_language_counts": dict(all_lang_counter.most_common()),
    }


def write_inventory(path: Path, results: list[dict[str, Any]]) -> None:
    fieldnames = ["skill_path", "is_valid", "is_network", "level", "is_pre_insecure", "network_langs", "all_langs"]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            row = dict(result)
            row["network_langs"] = ";".join(result["network_langs"])
            row["all_langs"] = ";".join(result["all_langs"])
            writer.writerow(row)


def write_summary_csv(path: Path, summary: dict[str, Any]) -> None:
    scalar_keys = [key for key, value in summary.items() if not isinstance(value, dict)]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=scalar_keys)
        writer.writeheader()
        writer.writerow({key: summary[key] for key in scalar_keys})


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze OpenClaw skill snapshots for network-facing and TLS-insecure patterns.")
    parser.add_argument("--skills-root", type=Path, required=True, help="Root directory of the extracted OpenClaw skills snapshot.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--workers", type=int, default=max(os.cpu_count() or 1, 1))
    parser.add_argument("--limit", type=int, help="Limit the number of skills processed for smoke testing.")
    parser.add_argument("--no-inventory", action="store_true", help="Skip writing per-skill inventory CSV.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    skills_root = resolve_path(args.skills_root)
    output_dir = resolve_path(args.output_dir)

    if not skills_root.exists():
        raise FileNotFoundError(f"Skills root not found: {skills_root}")

    skill_dirs = iter_skill_dirs(skills_root)
    if args.limit is not None:
        skill_dirs = skill_dirs[: args.limit]
    if not skill_dirs:
        raise FileNotFoundError(f"No SKILL.md files found under {skills_root}")

    print(f"[queue] skills={len(skill_dirs)} workers={args.workers}")
    worker_args = [(str(path), str(skills_root)) for path in skill_dirs]
    results: list[dict[str, Any]] = []
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(process_skill, item) for item in worker_args]
        completed = 0
        for future in as_completed(futures):
            results.append(future.result())
            completed += 1
            if completed % 1000 == 0 or completed == len(futures):
                print(f"[progress] {completed}/{len(futures)}")

    results = sorted(results, key=lambda row: row["skill_path"])
    summary = summarize(results)

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_summary_csv(output_dir / "summary.csv", summary)
    if not args.no_inventory:
        write_inventory(output_dir / "skill_inventory.csv", results)

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"[output] {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
