from __future__ import annotations

from pathlib import Path

from autorunne.core.gitops import detect_repo_root
from autorunne.core.vscode import install_vscode_integration


def run(target: Path) -> dict:
    repo_root = detect_repo_root(target) or target
    if not (repo_root / ".git").exists():
        raise RuntimeError("autorunne vscode needs a Git repository first. ⏰ Run `git init` first, then rerun `autorunne vscode`.")
    paths = install_vscode_integration(repo_root)
    return {"repo_root": str(repo_root), **paths}
