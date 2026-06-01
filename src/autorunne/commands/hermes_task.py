from __future__ import annotations

from pathlib import Path

from autorunne.commands import open as open_cmd
from autorunne.commands import start as start_cmd
from autorunne.core.gitops import ensure_git_repo
from autorunne.core.memory import maybe_auto_compact
from autorunne.core.state_engine import record_task_ingress


def run(
    target: Path,
    task: str,
    source: str = "hermes",
    next_action: str | None = None,
    context: str | None = None,
    decision: str | None = None,
) -> dict:
    repo_root, initialized_git = ensure_git_repo(target)

    open_result = open_cmd.run(repo_root)
    start_result = start_cmd.run(repo_root, task=task, next_action=next_action)
    clean_source = source.strip() if source and source.strip() else "agent"
    record_task_ingress(
        repo_root,
        source=clean_source,
        task=task,
        next_action=start_result["next_action"],
        workspace_action=open_result["action"],
        context=context,
        decision=decision,
    )
    auto_compact = maybe_auto_compact(repo_root, reason=f"{clean_source}_task_ingress")

    return {
        "repo_root": str(repo_root),
        "source": clean_source,
        "task": task.strip(),
        "next_action": start_result["next_action"],
        "workspace_action": open_result["action"],
        "context": context.strip() if context and context.strip() else None,
        "decision": decision.strip() if decision and decision.strip() else None,
        "initialized_git": initialized_git or open_result.get("initialized_git", False),
        "auto_compact": auto_compact,
    }
