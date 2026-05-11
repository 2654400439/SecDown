import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SKILLS_ROOT = REPO_ROOT / "agents" / "skill" / "skills"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "artifacts" / "skill_agent_logs"
DEFAULT_TUI_COMMAND = "openclaw tui --history-limit 1 --deliver"

FRICTIONS = ["local_issuer", "self_signed", "hostname_mismatch", "protocol_mismatch"]
TASK_DIR_PATTERN = re.compile(r"^(?P<task_num>\d+)_(?P<slug>.+)$")


@dataclass(frozen=True)
class SkillTask:
    path: Path
    task_type: str
    task_num: int
    name: str
    skill_name: str
    prompt: str


@dataclass(frozen=True)
class RunSpec:
    task: SkillTask
    model: str
    epoch: int


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def compact_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def safe_filename(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._") or "item"


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def display_external_path(path: Path) -> str:
    try:
        home = Path.home().resolve()
        resolved = path.expanduser().resolve()
        return f"~/{resolved.relative_to(home).as_posix()}"
    except (OSError, ValueError):
        return path.as_posix()


def resolve_input_path(path: Path) -> Path:
    if path.is_absolute() or path.exists():
        return path
    repo_relative = REPO_ROOT / path
    return repo_relative if repo_relative.exists() else path


def resolve_output_path(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def parse_models(models_arg: str | None, models_file: Path | None) -> list[str]:
    if models_file:
        models = [
            line.strip()
            for line in models_file.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
    elif models_arg:
        models = [item.strip() for item in models_arg.split(",") if item.strip()]
    else:
        models = ["manual-model"]
    if not models:
        raise ValueError("No models selected.")
    return models


def infer_skill_name(task_dir_name: str) -> str:
    match = TASK_DIR_PATTERN.match(task_dir_name)
    if match:
        return match.group("slug")
    return task_dir_name


def load_skill_task(path: Path) -> SkillTask:
    match = TASK_DIR_PATTERN.match(path.name)
    if not match:
        raise ValueError(f"Skill task directory must start with '<num>_': {path}")
    type_part = path.parent.name
    if not re.fullmatch(r"type_[abcd]", type_part):
        raise ValueError(f"Skill task must live under type_a/type_b/type_c/type_d: {path}")

    prompt_path = path / "prompt.txt"
    if not prompt_path.exists():
        raise FileNotFoundError(f"Missing prompt.txt for skill task: {path}")

    return SkillTask(
        path=path,
        task_type=type_part,
        task_num=int(match.group("task_num")),
        name=path.name,
        skill_name=infer_skill_name(path.name),
        prompt=prompt_path.read_text(encoding="utf-8"),
    )


def iter_task_dirs(skills_root: Path, task_type: str | None, task_dir: Path | None) -> Iterable[Path]:
    if task_dir:
        yield task_dir
        return
    search_root = skills_root / task_type if task_type else skills_root
    for prompt_path in sorted(search_root.rglob("prompt.txt")):
        yield prompt_path.parent


def load_tasks(skills_root: Path, task_type: str | None, task_dir: Path | None) -> list[SkillTask]:
    task_dirs = list(iter_task_dirs(skills_root, task_type, task_dir))
    if not task_dirs:
        raise FileNotFoundError(f"No skill task directories found under {skills_root}")
    return [load_skill_task(path) for path in task_dirs]


def build_run_id(run: RunSpec) -> str:
    short_type = run.task.task_type.replace("type_", "")
    return safe_filename(f"{run.model}_{short_type}_{run.task.task_num}_{run.epoch}")


def newest_jsonl(session_dir: Path, after_time: float | None = None) -> Path | None:
    files = sorted(session_dir.glob("*.jsonl"), key=lambda path: path.stat().st_mtime, reverse=True)
    if after_time is None:
        return files[0] if files else None
    for path in files:
        if path.stat().st_mtime >= after_time:
            return path
    return files[0] if files else None


class TmuxOpenClawController:
    def __init__(self, session_name: str, tui_command: str, dry_run: bool = False):
        self.session_name = session_name
        self.tui_command = tui_command
        self.dry_run = dry_run

    def run_tmux(self, *args: str) -> subprocess.CompletedProcess:
        command = ["tmux", *args]
        if self.dry_run:
            print(f"[dry-run] {' '.join(command)}")
            return subprocess.CompletedProcess(command, 0, "", "")
        return subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")

    def start(self, startup_wait: int) -> None:
        self.run_tmux("kill-session", "-t", self.session_name)
        result = self.run_tmux("new-session", "-d", "-s", self.session_name, self.tui_command)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to start OpenClaw TUI in tmux: {result.stderr}")
        print(f"[openclaw] started tmux session '{self.session_name}'")
        if not self.dry_run:
            time.sleep(startup_wait)
        self.send_command("/new")
        if not self.dry_run:
            time.sleep(2)

    def stop(self) -> None:
        self.run_tmux("kill-session", "-t", self.session_name)

    def send_command(self, text: str) -> None:
        if self.dry_run:
            print(f"[dry-run] send command: {text[:120]!r}")
            return
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as file:
            file.write(text)
            buffer_path = file.name
        try:
            load_result = self.run_tmux("load-buffer", "-t", self.session_name, buffer_path)
            if load_result.returncode != 0:
                raise RuntimeError(f"tmux load-buffer failed: {load_result.stderr}")
            paste_result = self.run_tmux("paste-buffer", "-t", self.session_name)
            if paste_result.returncode != 0:
                raise RuntimeError(f"tmux paste-buffer failed: {paste_result.stderr}")
            self.run_tmux("send-keys", "-t", self.session_name, "C-m")
        finally:
            Path(buffer_path).unlink(missing_ok=True)

    def capture_screen(self) -> str:
        result = self.run_tmux("capture-pane", "-t", self.session_name, "-p")
        return result.stdout or ""

    def wait_for_idle(self, timeout: int, check_interval: float, idle_marker: str) -> tuple[bool, str]:
        start_time = time.time()
        last_screen = ""
        while time.time() - start_time <= timeout:
            last_screen = self.capture_screen()
            if idle_marker in last_screen:
                return True, last_screen
            time.sleep(check_interval)
        return False, last_screen


def prepare_skill(task: SkillTask, workspace_skills_dir: Path, dry_run: bool) -> Path:
    target = workspace_skills_dir / task.skill_name
    if dry_run:
        print(f"[dry-run] copy skill {display_path(task.path)} -> {display_external_path(target)}")
        return target
    shutil.rmtree(target, ignore_errors=True)
    shutil.copytree(task.path, target)
    prompt_path = target / "prompt.txt"
    if prompt_path.exists():
        prompt_path.unlink()
    return target


def cleanup_skill(skill_path: Path, dry_run: bool) -> None:
    if dry_run:
        print(f"[dry-run] remove skill {display_external_path(skill_path)}")
        return
    shutil.rmtree(skill_path, ignore_errors=True)


def archive_run(
    archive_dir: Path,
    run: RunSpec,
    friction: str,
    skill_source: Path,
    skill_target: Path,
    prompt: str,
    session_log: Path | None,
    screen_output: str,
    status: str,
    elapsed_seconds: float,
    apply: bool,
) -> dict:
    metadata = {
        "timestamp": utc_timestamp(),
        "paradigm": "skill_agent",
        "runner": "openclaw_tui",
        "model": run.model,
        "task_type": run.task.task_type,
        "task_num": run.task.task_num,
        "task_id": f"{run.task.task_type}_{run.task.task_num}",
        "task_name": run.task.name,
        "skill_name": run.task.skill_name,
        "epoch": run.epoch,
        "friction": friction,
        "status": status,
        "elapsed_seconds": elapsed_seconds,
        "skill_source": display_path(skill_source),
        "skill_target": display_external_path(skill_target),
        "session_log_source": display_external_path(session_log) if session_log else None,
        "archive_dir": display_path(archive_dir),
    }
    if not apply:
        return metadata

    archive_dir.mkdir(parents=True, exist_ok=True)
    (archive_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
    (archive_dir / "screen.txt").write_text(screen_output, encoding="utf-8")
    if session_log and session_log.exists():
        shutil.copy2(session_log, archive_dir / "session.jsonl")
    (archive_dir / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    return metadata


def run_one(
    controller: TmuxOpenClawController,
    run: RunSpec,
    args: argparse.Namespace,
) -> dict:
    run_id = build_run_id(run)
    run_instance_id = f"{run_id}_{compact_timestamp()}"
    archive_dir = args.output_dir / "raw" / args.friction / run_instance_id

    prompt = run.task.prompt
    if args.spawn_guard and run.model == "gpt-5.4-nano":
        prompt += "\n\nCRITICAL: Do NOT spawn sub-agents or use sessions_spawn."

    start_time = time.time()
    skill_target = prepare_skill(run.task, args.workspace_skills_dir, args.dry_run)
    session_before = time.time()
    status = "dry_run" if args.dry_run else "unknown"
    screen_output = ""
    session_log = None

    try:
        if not args.dry_run:
            controller.send_command(prompt)
            idle, screen_output = controller.wait_for_idle(args.task_timeout, args.check_interval, args.idle_marker)
            status = "completed" if idle else "timeout"
            session_log = newest_jsonl(args.sessions_dir, after_time=session_before)
        else:
            status = "dry_run"
            screen_output = "[dry-run]"

        elapsed = time.time() - start_time
        record = archive_run(
            archive_dir=archive_dir,
            run=run,
            friction=args.friction,
            skill_source=run.task.path,
            skill_target=skill_target,
            prompt=prompt,
            session_log=session_log,
            screen_output=screen_output,
            status=status,
            elapsed_seconds=elapsed,
            apply=True,
        )
        record["run_id"] = run_id
        record["run_instance_id"] = run_instance_id
        (archive_dir / "metadata.json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        return record
    finally:
        cleanup_skill(skill_target, args.dry_run)
        if not args.dry_run and args.reset_between_tasks:
            controller.send_command("/new")
            time.sleep(args.reset_wait)


def append_jsonl(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(data, ensure_ascii=False) + "\n")


def build_runs(tasks: list[SkillTask], models: list[str], epochs: int) -> list[RunSpec]:
    return [RunSpec(task=task, model=model, epoch=epoch) for task in tasks for model in models for epoch in range(epochs)]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run SecDown Skill Agent experiments through OpenClaw TUI.")
    parser.add_argument("--skills-root", type=Path, default=DEFAULT_SKILLS_ROOT)
    parser.add_argument("--task-type", choices=["type_a", "type_b", "type_c", "type_d"])
    parser.add_argument("--task-dir", type=Path, help="Run a single skill task directory.")
    parser.add_argument(
        "--models",
        default=None,
        help="Comma-separated model labels for output metadata only. The tested model must be selected in the OpenClaw client before running.",
    )
    parser.add_argument("--models-file", type=Path, help="Text file containing one model label per line.")
    parser.add_argument("--friction", choices=FRICTIONS, default="self_signed")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--tmux-session", default="secdown_skill_agent")
    parser.add_argument("--tui-command", default=DEFAULT_TUI_COMMAND)
    parser.add_argument("--workspace-skills-dir", type=Path, default=Path(os.environ.get("OPENCLAW_WORKSPACE_SKILLS", str(Path.home() / ".openclaw" / "workspace" / "skills"))))
    parser.add_argument("--sessions-dir", type=Path, default=Path(os.environ.get("OPENCLAW_SESSIONS_DIR", str(Path.home() / ".openclaw" / "agents" / "main" / "sessions"))))
    parser.add_argument("--task-timeout", type=int, default=150)
    parser.add_argument("--check-interval", type=float, default=1.0)
    parser.add_argument("--idle-marker", default="connected | idle")
    parser.add_argument("--startup-wait", type=int, default=10)
    parser.add_argument("--reset-wait", type=int, default=3)
    parser.add_argument("--no-start-tui", action="store_true", help="Reuse an existing tmux session instead of launching OpenClaw TUI.")
    parser.add_argument("--no-stop-tui", action="store_true", help="Leave the tmux session running after completion.")
    parser.add_argument("--no-reset-between-tasks", dest="reset_between_tasks", action="store_false", default=True)
    parser.add_argument(
        "--no-spawn-guard",
        dest="spawn_guard",
        action="store_false",
        default=True,
        help="Disable the no-subagent guard appended for gpt-5.4-nano.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Validate task discovery and write placeholder outputs without driving tmux.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    args.skills_root = resolve_input_path(args.skills_root)
    args.task_dir = resolve_input_path(args.task_dir) if args.task_dir else None
    args.models_file = resolve_input_path(args.models_file) if args.models_file else None
    args.output_dir = resolve_output_path(args.output_dir)
    args.workspace_skills_dir = Path(args.workspace_skills_dir)
    args.sessions_dir = Path(args.sessions_dir)

    tasks = load_tasks(args.skills_root, args.task_type, args.task_dir)
    models = parse_models(args.models, args.models_file)
    runs = build_runs(tasks, models, args.epochs)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = args.output_dir / "summary.jsonl"
    controller = TmuxOpenClawController(args.tmux_session, args.tui_command, dry_run=args.dry_run)

    print(f"[queue] tasks={len(tasks)} models={len(models)} runs={len(runs)} friction={args.friction}")
    if not args.no_start_tui:
        controller.start(args.startup_wait)

    try:
        for run in runs:
            print(f"[start] model={run.model} task={run.task.name} epoch={run.epoch}")
            record = run_one(controller, run, args)
            append_jsonl(summary_path, record)
            print(f"[done] {run.model} {run.task.name} -> {record['status']}")
    finally:
        if not args.no_stop_tui:
            controller.stop()

    print("[complete] Skill Agent experiment queue finished")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


