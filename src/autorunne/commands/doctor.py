from __future__ import annotations

from pathlib import Path

from autorunne.core.gitops import detect_repo_root, is_tracked
from autorunne.core.paths import STATE_FILES, VIEW_FILES, snapshot_file, state_dir, view_file, views_dir, workflow_bin_dir, workflow_dir
from autorunne.core.state_engine import diagnose_handoff_consistency, legacy_workspace_exists, render_from_state, workflow_exists, workflow_needs_migration


def run(target: Path, *, handoff_only: bool = False) -> dict:
    repo_root = detect_repo_root(target) or target
    root = workflow_dir(repo_root)
    exclude_path = repo_root / ".git" / "info" / "exclude"
    vscode_settings = repo_root / ".vscode" / "settings.json"
    vscode_tasks = repo_root / ".vscode" / "tasks.json"
    post_checkout = repo_root / ".git" / "hooks" / "post-checkout"
    post_merge = repo_root / ".git" / "hooks" / "post-merge"
    pre_commit_hook = repo_root / ".git" / "hooks" / "pre-commit"
    precommit_config = repo_root / ".pre-commit-config.yaml"
    state_root = state_dir(repo_root)
    views_root = views_dir(repo_root)
    snapshot_path = snapshot_file(repo_root)
    repo_skill = repo_root / ".agents" / "skills" / "autorunne-workflow" / "SKILL.md"
    claude_skill = repo_root / ".claude" / "skills" / "autorunne-workflow" / "SKILL.md"
    cursor_rule = repo_root / ".cursor" / "rules" / "autorunne-workflow.mdc"
    copilot_instructions = repo_root / ".github" / "copilot-instructions.md"
    wrappers = [workflow_bin_dir(repo_root) / name for name in ["ar-codex", "ar-claude", "ar-hermes"]]

    result = {
        "repo_root": str(repo_root),
        "is_git_repo": (repo_root / ".git").exists(),
        "workflow_exists": root.exists(),
        "missing": [],
        "warnings": [],
        "optional_warnings": [],
        "blocking": [],
        "checks": {},
    }
    if not result["is_git_repo"]:
        result["warnings"].append("Not inside a git repository")
        result["blocking"].append("Not inside a git repository")
        result["checks"]["git_repo"] = "missing"
        return result

    result["checks"]["git_repo"] = "ok"

    if handoff_only:
        if not workflow_exists(repo_root):
            msg = "Autorunne workspace does not exist yet"
            result["warnings"].append(msg)
            result["blocking"].append(msg)
            result["checks"]["workflow"] = "missing"
            result["checks"]["handoff_consistency"] = "missing"
            return result
        result["checks"]["workflow"] = "ok"
        try:
            handoff = diagnose_handoff_consistency(repo_root)
        except Exception as exc:
            msg = f"handoff_consistency check failed: {exc}"
            result["warnings"].append(msg)
            result["blocking"].append(msg)
            result["checks"]["handoff_consistency"] = "missing"
            return result
        result["handoff_consistency"] = handoff
        if handoff["ok"]:
            result["checks"]["handoff_consistency"] = "ok"
        else:
            result["checks"]["handoff_consistency"] = "mismatch"
            result["warnings"].append(
                "handoff_consistency fields: "
                + ", ".join(f"{name}={value}" for name, value in handoff.get("fields", {}).items() if value)
            )
            for mismatch in handoff.get("mismatches", []):
                result["warnings"].append(
                    f"handoff_consistency mismatch: {mismatch['field']}={mismatch['value']} expected={mismatch['expected']}"
                )
            for text in handoff.get("workflow_backlog", []):
                result["warnings"].append(f"handoff_consistency workflow backlog item: {text}")
            result["blocking"].extend(result["warnings"])
        return result

    if root.exists():
        missing_state = [name for name in STATE_FILES if not (state_root / name).exists()]
        missing_views = [name for name in VIEW_FILES if not (views_root / name).exists()]
        result["missing"] = [f"state/{name}" for name in missing_state] + [f"views/{name}" for name in missing_views]
        result["blocking"].extend(result["missing"])
        result["checks"]["state_files"] = "ok" if not missing_state else "missing"
        result["checks"]["views"] = "ok" if not missing_views else "missing"
        result["checks"]["snapshot"] = "ok" if snapshot_path.exists() else "missing"
        if workflow_needs_migration(repo_root):
            result["warnings"].append("Legacy markdown workspace detected; run `autorunne migrate` to create state files")
            result["blocking"].append("Legacy markdown workspace detected; run `autorunne migrate` to create state files")
            result["checks"]["legacy_workspace"] = "needs_migration"
        elif legacy_workspace_exists(repo_root):
            result["checks"]["legacy_workspace"] = "ok"
        else:
            result["checks"]["legacy_workspace"] = "missing"
        if is_tracked(repo_root, root.name):
            result["warnings"].append(".autorunne is tracked by git; keep it local-only")
        if workflow_exists(repo_root):
            handoff = diagnose_handoff_consistency(repo_root)
            result["handoff_consistency"] = handoff
            if handoff["ok"]:
                result["checks"]["handoff_consistency"] = "ok"
            else:
                result["checks"]["handoff_consistency"] = "mismatch"
                result["warnings"].append(
                    "handoff_consistency fields: "
                    + ", ".join(f"{name}={value}" for name, value in handoff.get("fields", {}).items() if value)
                )
                for mismatch in handoff.get("mismatches", []):
                    result["warnings"].append(
                        f"handoff_consistency mismatch: {mismatch['field']}={mismatch['value']} expected={mismatch['expected']}"
                    )
                for text in handoff.get("workflow_backlog", []):
                    result["warnings"].append(f"handoff_consistency workflow backlog item: {text}")
                result["blocking"].extend([warning for warning in result["warnings"] if warning.startswith("handoff_consistency")])
            try:
                probe = view_file(repo_root, "START_HERE.md")
                before = probe.read_text(encoding="utf-8") if probe.exists() else None
                if probe.exists():
                    probe.unlink()
                render_from_state(repo_root)
                result["checks"]["render_rebuild"] = "ok" if probe.exists() else "missing"
                if before is not None:
                    after = probe.read_text(encoding="utf-8") if probe.exists() else None
                    if after != before:
                        message = "Render rebuild changed START_HERE.md content during doctor check"
                        result["warnings"].append(message)
                        result["blocking"].append(message)
            except Exception as exc:
                message = f"Render rebuild failed: {exc}"
                result["warnings"].append(message)
                result["blocking"].append(message)
                result["checks"]["render_rebuild"] = "missing"
        else:
            result["checks"]["render_rebuild"] = "missing"
    else:
        message = "Autorunne workspace does not exist yet"
        result["warnings"].append(message)
        result["blocking"].append(message)
        result["checks"]["state_files"] = "missing"
        result["checks"]["views"] = "missing"
        result["checks"]["snapshot"] = "missing"
        result["checks"]["render_rebuild"] = "missing"

    if not exclude_path.exists() or ".autorunne/" not in exclude_path.read_text(encoding="utf-8"):
        result["warnings"].append(".git/info/exclude does not contain .autorunne/")
        result["checks"]["git_exclude"] = "missing"
    else:
        result["checks"]["git_exclude"] = "ok"

    hooks_ok = post_checkout.exists() and post_merge.exists()
    if not hooks_ok:
        message = "Git hooks are not installed"
        result["warnings"].append(message)
        result["optional_warnings"].append(message)
        result["checks"]["hooks"] = "missing"
    else:
        result["checks"]["hooks"] = "ok"

    vscode_ok = vscode_settings.exists() and vscode_tasks.exists()
    result["checks"]["vscode"] = "ok" if vscode_ok else "missing"

    precommit_ok = pre_commit_hook.exists() and precommit_config.exists()
    if not precommit_ok:
        message = "Pre-commit config is not installed"
        result["warnings"].append(message)
        result["optional_warnings"].append(message)
        result["checks"]["pre_commit"] = "missing"
    else:
        result["checks"]["pre_commit"] = "ok"

    integrations_ok = (
        repo_skill.exists()
        and claude_skill.exists()
        and cursor_rule.exists()
        and copilot_instructions.exists()
    )
    if not integrations_ok:
        message = "Repo-level agent integrations are not fully installed"
        result["warnings"].append(message)
        result["optional_warnings"].append(message)
        result["checks"]["integrations"] = "missing"
    else:
        result["checks"]["integrations"] = "ok"

    wrappers_ok = all(path.exists() for path in wrappers)
    if not wrappers_ok:
        message = "Repo-level wrappers are not installed"
        result["warnings"].append(message)
        result["optional_warnings"].append(message)
        result["checks"]["wrappers"] = "missing"
    else:
        result["checks"]["wrappers"] = "ok"

    dist_dir = repo_root / "dist"
    result["checks"]["package_artifacts"] = "ok" if dist_dir.exists() and any(dist_dir.iterdir()) else "missing"

    return result
