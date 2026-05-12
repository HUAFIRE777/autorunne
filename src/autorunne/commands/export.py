from __future__ import annotations

from pathlib import Path

from autorunne.core.exporter import export_clean_copy
from autorunne.core.gitops import detect_repo_root


def run(target: Path, output_name: str | None = None) -> dict:
    repo_root = detect_repo_root(target) or target
    if not (repo_root / ".git").exists():
        raise RuntimeError("autorunne export needs a Git repository first. ⏰ Run `git init` first, then rerun `autorunne export`.")
    exported = export_clean_copy(repo_root, output_name=output_name)
    return {"repo_root": str(repo_root), "exported_path": str(exported)}
