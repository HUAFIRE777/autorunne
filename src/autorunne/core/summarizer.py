from __future__ import annotations

from pathlib import Path

from autorunne.core.paths import STATE_FILES, VIEW_FILES, state_dir, views_dir, workflow_dir, workflow_file


def summarize_status(repo_root: Path, scan: dict) -> dict:
    root = workflow_dir(repo_root)
    state_root = state_dir(repo_root)
    views_root = views_dir(repo_root)
    present_state = [name for name in STATE_FILES if (state_root / name).exists()]
    missing_state = [name for name in STATE_FILES if name not in present_state]
    present_views = [name for name in VIEW_FILES if (views_root / name).exists()]
    missing_views = [name for name in VIEW_FILES if name not in present_views]
    optional_mirrors_missing = [name for name in VIEW_FILES if (views_root / name).exists() and not workflow_file(repo_root, name).exists()]
    return {
        "repo": repo_root.name,
        "workflow_root": str(root),
        "state_root": str(state_root),
        "views_root": str(views_root),
        "present": present_views,
        "missing": missing_state + missing_views,
        "missing_state": missing_state,
        "missing_views": missing_views,
        "optional_mirrors_missing": optional_mirrors_missing,
        "stack": scan["stack"],
        "framework": scan["framework"],
        "next_action": scan["next_action"],
        "project_phase": scan["project_phase"],
        "resume_hint": scan["resume_hint"],
    }
