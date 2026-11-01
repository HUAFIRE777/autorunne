from __future__ import annotations

from pathlib import Path
from typing import Any

from autorunne.core.dream import check_index_budget, execute_dream_cycle, resolve_index_file
from autorunne.core.gitops import detect_repo_root


def run(
    target: Path,
    *,
    status_only: bool = False,
    record_rule: str | None = None,
) -> dict[str, Any]:
    repo_root = detect_repo_root(target) or target

    if status_only:
        index_p = resolve_index_file(repo_root)
        budget = check_index_budget(index_p)
        return {
            "repo_root": str(repo_root),
            "status": "healthy" if budget["valid"] else "budget_exceeded",
            "lines": budget["lines"],
            "max_lines": budget["max_lines"],
            "path": budget["path"],
        }

    cycle_result = execute_dream_cycle(repo_root, explicit_rule=record_rule)
    return {
        "repo_root": str(repo_root),
        **cycle_result,
    }
