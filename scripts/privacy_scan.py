import argparse
import csv
import hashlib
import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_EXCLUDES = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "privacy_scan",
}

TEXT_EXTENSIONS = {
    ".csv",
    ".json",
    ".jsonl",
    ".log",
    ".md",
    ".py",
    ".txt",
    ".yaml",
    ".yml",
}

PATTERNS = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "openai_key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "github_token": re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{20,}\b"),
    "generic_api_assignment": re.compile(
        r"(?i)['\"]?\b(?:api[_-]?key|access[_-]?token|secret|password|passwd|bearer)\b['\"]?\s*[:=]\s*['\"]([^'\"\s,;]{12,})['\"]?"
    ),
    "authorization_header": re.compile(r"(?i)\bAuthorization\s*[:=]\s*Bearer\s+([A-Za-z0-9._~+/=-]{12,})"),
    "windows_path": re.compile(r"\b[A-Za-z]:\\(?:Users\\[^\\\s]+|[^:\n\r]+)"),
    "unix_home_path": re.compile(r"(?<![A-Za-z0-9_])/(?:home|Users)/[A-Za-z0-9._-]+/[^\s:'\"]*"),
    "ssh_private_key": re.compile(r"-----BEGIN (?:RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "github_repo_url": re.compile(
        r"(?:(?<![A-Za-z0-9_.-])github\.com/(?:repos/)?|raw\.githubusercontent\.com/)([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)"
    ),
}

KNOWN_PLACEHOLDERS = {
    "...",
    "<ENV:GITHUB_PAT>",
    "<ENV:TAVILY_API_KEY>",
    "<ENV:AIRLABS_API_KEY>",
    "<ENV:RAPIDAPI_API_KEY>",
    "<API_KEY_ENV>",
    "<MODEL_ENDPOINT>",
    "[REDACTED]",
    "<EXAMPLE_API_KEY>",
    "<EXAMPLE_GITHUB_PAT>",
    "<EXAMPLE_TAVILY_API_KEY>",
    "<LOCAL_USER_DIR>",
    "<REDACTED_AIRLABS_API_KEY>",
    "<REDACTED_API_KEY>",
    "<REDACTED_BEARER_TOKEN>",
    "<REDACTED_GITHUB_OWNER>",
    "<REDACTED_GITHUB_PAT>",
    "<REDACTED_RAPIDAPI_KEY>",
    "<REDACTED_TAVILY_API_KEY>",
}

KNOWN_PUBLIC_REPOS = {
    "example-org/example-repo",
    "markdown/raw",
    "kubernetes/kubernetes",
    "psf/requests",
    "example-org/private-research-artifact",
    "users/example-user",
}


@dataclass
class Finding:
    category: str
    path: str
    line: int
    match_hash: str
    redacted_match: str
    context: str
    severity: str


def entropy(value: str) -> float:
    if not value:
        return 0.0
    counts = Counter(value)
    return -sum((count / len(value)) * math.log2(count / len(value)) for count in counts.values())


def redact(value: str) -> str:
    value = value.strip()
    if value in KNOWN_PLACEHOLDERS:
        return value
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}...{value[-4:]}"


def stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="ignore")).hexdigest()[:16]


def redact_context(line: str, matches: list[str]) -> str:
    context = line.strip()
    for pattern_name in ("openai_key", "github_token", "authorization_header", "generic_api_assignment"):
        pattern = PATTERNS[pattern_name]
        for match in pattern.finditer(context):
            value = match.group(1) if pattern_name in {"authorization_header", "generic_api_assignment"} else match.group(0)
            context = context.replace(value, redact(value))
    for match in sorted(matches, key=len, reverse=True):
        context = context.replace(match, redact(match))
    return context[:500]


def should_skip_path(path: Path, excludes: set[str]) -> bool:
    return any(part in excludes for part in path.parts)


def is_text_file(path: Path) -> bool:
    if path.suffix in TEXT_EXTENSIONS:
        return True
    if path.suffix in {".crt", ".pem"}:
        return True
    return False


def iter_files(paths: Iterable[Path], excludes: set[str]) -> Iterable[Path]:
    for path in paths:
        if not path.exists():
            continue
        if path.is_file():
            if not should_skip_path(path, excludes) and is_text_file(path):
                yield path
            continue
        for child in path.rglob("*"):
            if child.is_file() and not should_skip_path(child, excludes) and is_text_file(child):
                yield child


def severity_for(category: str, match: str) -> str:
    if category in {"openai_key", "github_token", "authorization_header", "ssh_private_key"}:
        return "high"
    if category == "generic_api_assignment" and entropy(match) >= 3.5:
        return "high"
    if category in {"email", "windows_path", "unix_home_path"}:
        return "medium"
    if category == "github_repo_url" and match not in KNOWN_PUBLIC_REPOS:
        return "review"
    return "low"


def normalize_github_repo(value: str) -> str:
    return value.removesuffix(".git")


def scan_line(path: Path, line_no: int, line: str, root: Path) -> list[Finding]:
    findings: list[Finding] = []
    raw_matches_for_context: list[str] = []
    pending: list[tuple[str, str, str]] = []

    for category, pattern in PATTERNS.items():
        for match in pattern.finditer(line):
            value = match.group(1) if category in {"generic_api_assignment", "authorization_header", "github_repo_url"} else match.group(0)
            comparison_value = normalize_github_repo(value) if category == "github_repo_url" else value
            if value in KNOWN_PLACEHOLDERS:
                continue
            if value.startswith("<REDACTED_") or value.startswith("<EXAMPLE_"):
                continue
            if category == "github_repo_url" and comparison_value in KNOWN_PUBLIC_REPOS:
                continue
            if category == "generic_api_assignment" and value.startswith("<ENV:"):
                continue
            if category == "generic_api_assignment" and ("os.environ" in line or "getenv" in line):
                continue
            pending.append((category, value, severity_for(category, value)))
            raw_matches_for_context.append(value)

    if not pending:
        return findings

    context = redact_context(line, raw_matches_for_context)
    try:
        rel_path = str(path.relative_to(root).as_posix())
    except ValueError:
        rel_path = str(path.as_posix())

    for category, value, severity in pending:
        findings.append(
            Finding(
                category=category,
                path=rel_path,
                line=line_no,
                match_hash=stable_hash(value),
                redacted_match=redact(value),
                context=context,
                severity=severity,
            )
        )
    return findings


def scan_file(path: Path, root: Path) -> list[Finding]:
    findings: list[Finding] = []
    try:
        with path.open("r", encoding="utf-8", errors="replace") as file:
            for line_no, line in enumerate(file, start=1):
                findings.extend(scan_line(path, line_no, line, root))
    except OSError:
        return findings
    return findings


def write_reports(findings: list[Finding], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = [finding.__dict__ for finding in findings]

    with (output_dir / "privacy_findings.json").open("w", encoding="utf-8") as file:
        json.dump(rows, file, ensure_ascii=False, indent=2)

    with (output_dir / "privacy_findings.csv").open("w", newline="", encoding="utf-8") as file:
        fieldnames = ["severity", "category", "path", "line", "redacted_match", "match_hash", "context"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row[key] for key in fieldnames})

    summary = {
        "total_findings": len(findings),
        "by_severity": dict(Counter(finding.severity for finding in findings)),
        "by_category": dict(Counter(finding.category for finding in findings)),
        "files_with_findings": len({finding.path for finding in findings}),
    }
    (output_dir / "privacy_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# Privacy Scan Report",
        "",
        "This report is generated in detection-only mode. No files were modified.",
        "",
        f"- Total findings: {summary['total_findings']}",
        f"- Files with findings: {summary['files_with_findings']}",
        f"- By severity: {summary['by_severity']}",
        f"- By category: {summary['by_category']}",
        "",
        "Review `privacy_findings.csv` for redacted matches and context. The report intentionally stores hashes and redacted values rather than raw secrets.",
    ]
    (output_dir / "privacy_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Detection-only privacy scan for logs and artifact files.")
    parser.add_argument("paths", nargs="*", type=Path, default=[Path(".")], help="Files or directories to scan.")
    parser.add_argument("--root", type=Path, default=Path("."), help="Root path used for relative report paths.")
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/privacy_scan"), help="Report output directory.")
    parser.add_argument("--exclude", action="append", default=[], help="Additional path component to exclude.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = args.root.resolve()
    excludes = DEFAULT_EXCLUDES | set(args.exclude)
    files = list(iter_files([path.resolve() for path in args.paths], excludes))
    findings: list[Finding] = []
    for file_path in files:
        findings.extend(scan_file(file_path, root))

    write_reports(findings, args.output_dir)
    print(f"Scanned {len(files)} files; found {len(findings)} findings.")
    print(f"Report written to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
