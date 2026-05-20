from __future__ import annotations

from pathlib import Path

from autorunne.core.gitops import detect_repo_root
from autorunne.core.state_engine import repair_handoff_state, workflow_exists


def run(target: Path) -> dict:
    repo_root = detect_repo_root(target) or target
    if not workflow_exists(repo_root):
        raise RuntimeError("autorunne repair-handoff needs an Autorunne workspace first. Run `autorunne open` or `autorunne adopt` first.")
    return repair_handoff_state(repo_root)
