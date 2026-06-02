from __future__ import annotations

from pathlib import Path

from autorunne.commands.finish import FinishValidationError, _resolve_validation_command, _run_validation
from autorunne.core.gitops import detect_repo_root
from autorunne.core.memory import maybe_auto_compact
from autorunne.core.summaries import generate_checkpoint_summary
from autorunne.core.state_engine import collect_git_details, record_checkpoint


def run(
    target: Path,
    summary: str | None = None,
    next_action: str | None = None,
    validation_command: str | None = None,
    skip_validation: bool = False,
) -> dict:
    repo_root = detect_repo_root(target) or target
    if not (repo_root / ".git").exists():
        raise RuntimeError("autorunne checkpoint needs a Git repository first. ⏰ Run `git init` first, then rerun `autorunne checkpoint`.")

    git_details = collect_git_details(repo_root)
    clean_summary = summary.strip() if summary and summary.strip() else generate_checkpoint_summary(repo_root, git_details)
    resolved_next_action = next_action.strip() if next_action else clean_summary
    resolved_validation_command = _resolve_validation_command(repo_root, validation_command, skip_validation)
    validation = _run_validation(repo_root, resolved_validation_command)
    record_checkpoint(repo_root, clean_summary, resolved_next_action, git_details, validation=validation)
    auto_compact = maybe_auto_compact(repo_root, reason="checkpoint")
    return {
        "repo_root": str(repo_root),
        "summary": clean_summary,
        "next_action": resolved_next_action,
        "validation": validation,
        "auto_compact": auto_compact,
    }
