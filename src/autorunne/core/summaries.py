from __future__ import annotations

from pathlib import Path
from typing import Any

from autorunne.core.paths import read_json, state_file


def _short_file_list(files: list[str], *, limit: int = 3) -> str:
    visible = [item for item in files if item]
    if not visible:
        return ""
    shown = ", ".join(visible[:limit])
    if len(visible) > limit:
        shown += f" 等 {len(visible)} 个文件"
    return shown


def generate_checkpoint_summary(repo_root: Path, git_details: dict[str, Any] | None = None) -> str:
    """Return a safe automatic checkpoint summary for zero-prompt agent flows.

    This is intentionally deterministic and local-only: it does not call an LLM,
    does not ask the user, and works for older wrappers that still invoke plain
    `autorunne checkpoint`.
    """
    git_details = git_details or {}
    changed = git_details.get("changed_files") or []
    if changed:
        return f"自动记录本轮进度：更新了 {_short_file_list(changed)}"

    classified = git_details.get("changed_files_by_type") or {}
    integration = classified.get("integration") or []
    if integration:
        return f"自动记录本轮进度：刷新了 agent 交接文件 {_short_file_list(integration)}"

    autorunne_state = classified.get("autorunne_state") or []
    if autorunne_state:
        return "自动记录本轮进度：刷新了 Autorunne 项目状态"

    current = read_json(state_file(repo_root, "current.json"), default={})
    active_task = current.get("active_task")
    if active_task:
        return f"自动记录任务进度：{active_task}"
    next_action = current.get("next_action")
    if next_action:
        return f"自动记录项目进度：下一步是 {next_action}"
    return "自动记录项目进度"


def generate_finish_summary(repo_root: Path, git_details: dict[str, Any] | None = None, task_match: str | None = None) -> str:
    """Return a safe automatic finish summary when an agent/wrapper omits one."""
    current = read_json(state_file(repo_root, "current.json"), default={})
    task = (task_match or current.get("active_task") or "当前任务").strip()
    git_details = git_details or {}

    # Prefer business files over integration files for the summary
    classified = git_details.get("changed_files_by_type") or {}
    business = classified.get("business") or []
    changed = business or git_details.get("changed_files") or []

    if changed:
        return f"完成 {task}：更新了 {_short_file_list(changed)}"
    return f"完成 {task}"
