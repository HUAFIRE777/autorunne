from __future__ import annotations

from pathlib import Path
from typing import Any

from autorunne.core.memory import compact_memory, export_session, memory_report


def compact(repo_root: Path, *, keep_sessions: int = 200, dry_run: bool = False) -> dict[str, Any]:
    return compact_memory(repo_root, keep_sessions=keep_sessions, dry_run=dry_run)


def report(repo_root: Path, *, keep_sessions: int = 200) -> dict[str, Any]:
    return memory_report(repo_root, keep_sessions=keep_sessions)


def export(repo_root: Path, *, last: int = 20, since: str | None = None, output: str | None = None) -> dict[str, Any]:
    return export_session(repo_root, last=last, since=since, output=output)
