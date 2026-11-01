from __future__ import annotations

from pathlib import Path

from autorunne.core.auto_record import auto_finish_active_task
from autorunne.core.gitops import detect_repo_root
from autorunne.core.dream import execute_dream_cycle


def run(target: Path, *, source: str = "agent") -> dict:
    repo_root = detect_repo_root(target) or target
    if not (repo_root / ".git").exists():
        raise RuntimeError("autorunne auto-finish needs a Git repository first. ⏰ Run `git init` first, then rerun `autorunne auto-finish`.")

    result = auto_finish_active_task(repo_root, source=source)
    try:
        dream_result = execute_dream_cycle(repo_root)
    except Exception:
        dream_result = None

    return {"repo_root": str(repo_root), "dream": dream_result, **result}
