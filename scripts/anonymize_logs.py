import argparse
import csv
import re
from collections import Counter
from pathlib import Path


TEXT_EXTENSIONS = {".txt", ".log", ".json", ".jsonl", ".csv", ".md", ".py"}

REPLACEMENTS = [
    ("github_pat", re.compile(r"\bghp_[A-Za-z0-9_]{20,}\b"), "<REDACTED_GITHUB_PAT>"),
    ("github_pat_placeholder", re.compile(r"\bghp_[A-Za-z0-9_-]*token[A-Za-z0-9_-]*\b", re.IGNORECASE), "<EXAMPLE_GITHUB_PAT>"),
    (
        "github_pat_named_placeholder",
        re.compile(r"\byour(?:_actual)?_github_pat_here\b", re.IGNORECASE),
        "<EXAMPLE_GITHUB_PAT>",
    ),
    ("github_token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"), "<REDACTED_GITHUB_PAT>"),
    ("tavily_key", re.compile(r"\btvly-[A-Za-z0-9_-]{8,}\b"), "<REDACTED_TAVILY_API_KEY>"),
    ("tavily_placeholder", re.compile(r"\btvly-\.\.\."), "<EXAMPLE_TAVILY_API_KEY>"),
    (
        "known_airlabs_key",
        re.compile(r"\b2bca544b-c492-4ba4-b39f-e57f7e3ba2d3\b", re.IGNORECASE),
        "<REDACTED_AIRLABS_API_KEY>",
    ),
    (
        "known_airlabs_truncated",
        re.compile(r"\bapi_key=2bca544b\.\.\.", re.IGNORECASE),
        "api_key=<REDACTED_AIRLABS_API_KEY>",
    ),
    (
        "known_airlabs_truncated_standalone",
        re.compile(r"\b2bca544b-\.\.\.", re.IGNORECASE),
        "<REDACTED_AIRLABS_API_KEY>",
    ),
    (
        "authorization_bearer",
        re.compile(r"(?i)(Authorization\s*:\s*Bearer\s+)([A-Za-z0-9._~+/=-]{12,})"),
        r"\1<REDACTED_BEARER_TOKEN>",
    ),
    (
        "api_key_query",
        re.compile(r"(?i)([?&]api_key=)([^&\s'\")]+)"),
        r"\1<REDACTED_API_KEY>",
    ),
    (
        "api_key_json",
        re.compile(r"(?i)(['\"]api_key['\"]\s*:\s*['\"])([^'\"]{12,})(['\"])"),
        r"\1<REDACTED_API_KEY>\3",
    ),
    (
        "x_rapidapi_key_json",
        re.compile(r"(?i)(['\"]x-rapidapi-key['\"]\s*:\s*['\"])([^'\"]{12,})(['\"])"),
        r"\1<REDACTED_RAPIDAPI_KEY>\3",
    ),
    (
        "windows_user_path",
        re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+"),
        r"<LOCAL_USER_DIR>",
    ),
    (
        "unix_user_path",
        re.compile(r"(?<![A-Za-z0-9_])/(?:home|Users)/[A-Za-z0-9._-]+"),
        r"<LOCAL_USER_DIR>",
    ),
    (
        "old_private_repo_owner",
        re.compile(r"\byifeicheng/STAR-traffic-alignment\b"),
        "example-org/private-research-artifact",
    ),
    (
        "old_private_repo_numeric",
        re.compile(r"\b2654400439/STAR-traffic-alignment\b"),
        "example-org/private-research-artifact",
    ),
    (
        "old_private_owner_name",
        re.compile(r"\byifeicheng\b"),
        "<REDACTED_GITHUB_OWNER>",
    ),
    (
        "old_private_owner_numeric",
        re.compile(r"2654400439"),
        "<REDACTED_GITHUB_OWNER>",
    ),
    (
        "old_private_repo_name",
        re.compile(r"\bSTAR-traffic-alignment\b"),
        "private-research-artifact",
    ),
    (
        "old_private_repo_name_truncated",
        re.compile(r"\bSTAR-traffic\b"),
        "private-research-artifact",
    ),
]

REVIEW_REPLACEMENTS = [
    ("email_address", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), "<REDACTED_EMAIL>"),
    (
        "generic_api_placeholder",
        re.compile(r"\b(?:YOUR[_-]?)?(?:API[_-]?KEY|KEY|TOKEN|SECRET)[_-]?HERE\b", re.IGNORECASE),
        "<EXAMPLE_API_KEY>",
    ),
    (
        "generic_windows_path",
        re.compile(r"\b[A-Za-z]:\\[^\s'\"`),\]}]+"),
        "<LOCAL_PATH>",
    ),
    (
        "github_avatar_url",
        re.compile(r"https://avatars\.githubusercontent\.com/u/\d+(?:\?v=\d+)?"),
        "https://avatars.githubusercontent.com/u/0?v=4",
    ),
    (
        "github_api_user_url",
        re.compile(r"https://api\.github\.com/users/[A-Za-z0-9_.-]+[A-Za-z0-9_./{}-]*"),
        "https://api.github.com/users/example-user",
    ),
    (
        "github_html_user_url",
        re.compile(r"https://github\.com/(?!kubernetes/kubernetes\b|psf/requests\b|example-org/private-research-artifact\b)[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_./{}-]*)?"),
        "https://github.com/example-user",
    ),
    (
        "github_raw_user_url",
        re.compile(r"https://raw\.githubusercontent\.com/(?!kubernetes/kubernetes\b|psf/requests\b|example-org/private-research-artifact\b)[A-Za-z0-9_.-]+/[^\s'\"),\]}]+"),
        "https://raw.githubusercontent.com/example-org/example-repo/main/example.txt",
    ),
    (
        "masked_github_api_url",
        re.compile(r"https?://github\.com/(?:\*+|api/v3)/repos/example-org/private-research-artifact/commits"),
        "https://api.github.com/repos/example-org/private-research-artifact/commits",
    ),
    (
        "github_login_field",
        re.compile(r'("login"\s*:\s*")[^"]+(")'),
        r"\1<REDACTED_GITHUB_USER>\2",
    ),
    (
        "github_login_field_single_quote",
        re.compile(r"('login'\s*:\s*')[^']+(')"),
        r"\1<REDACTED_GITHUB_USER>\2",
    ),
    (
        "github_node_id_field",
        re.compile(r'("node_id"\s*:\s*")[^"]+(")'),
        r"\1<REDACTED_GITHUB_NODE_ID>\2",
    ),
    (
        "github_node_id_field_single_quote",
        re.compile(r"('node_id'\s*:\s*')[^']+(')"),
        r"\1<REDACTED_GITHUB_NODE_ID>\2",
    ),
    (
        "github_gravatar_field",
        re.compile(r'("gravatar_id"\s*:\s*")[^"]*(")'),
        r"\1\2",
    ),
    (
        "known_public_github_usernames",
        re.compile(r"\b(?:tico88612|kairosci|ajuijas)\b"),
        "<REDACTED_GITHUB_USER>",
    ),
]


def iter_files(paths: list[Path]):
    for path in paths:
        if not path.exists():
            continue
        if path.is_file():
            if path.suffix in TEXT_EXTENSIONS:
                yield path
            continue
        for child in path.rglob("*"):
            if child.is_file() and child.suffix in TEXT_EXTENSIONS:
                yield child


def anonymize_text(text: str, include_review: bool):
    counts = Counter()
    updated = text
    replacements = REPLACEMENTS + (REVIEW_REPLACEMENTS if include_review else [])
    for name, pattern, replacement in replacements:
        updated, count = pattern.subn(replacement, updated)
        counts[name] += count
    return updated, counts


def process_file(path: Path, apply: bool, include_review: bool):
    original = path.read_text(encoding="utf-8", errors="replace")
    updated, counts = anonymize_text(original, include_review)
    if apply and updated != original:
        path.write_text(updated, encoding="utf-8")
    return counts


def build_parser():
    parser = argparse.ArgumentParser(description="Anonymize high-confidence sensitive strings in artifact logs.")
    parser.add_argument("paths", nargs="+", type=Path, help="Files or directories to process.")
    parser.add_argument("--apply", action="store_true", help="Modify files in place. Without this flag, only reports counts.")
    parser.add_argument(
        "--include-review",
        action="store_true",
        help="Also anonymize review-level findings such as emails, generic local paths, and GitHub user metadata.",
    )
    parser.add_argument("--report", type=Path, default=Path("artifacts/privacy_scan/anonymization_report.csv"))
    return parser


def main():
    args = build_parser().parse_args()
    rows = []
    total = Counter()
    replacements = REPLACEMENTS + (REVIEW_REPLACEMENTS if args.include_review else [])
    for path in iter_files(args.paths):
        counts = process_file(path, args.apply, args.include_review)
        if sum(counts.values()):
            total.update(counts)
            row = {"path": path.as_posix(), **dict(counts)}
            rows.append(row)

    args.report.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["path"] + [name for name, _pattern, _replacement in replacements]
    with args.report.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, 0) for key in fieldnames})

    mode = "applied" if args.apply else "dry-run"
    print(f"Anonymization {mode}: {sum(total.values())} replacements across {len(rows)} files.")
    print(dict(total))
    print(f"Report written to {args.report}")


if __name__ == "__main__":
    raise SystemExit(main())
