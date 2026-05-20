from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from autorunne.core import integrations
from autorunne.cli import app
from autorunne import __version__

runner = CliRunner()


def _run_in(repo: Path, args: list[str]):
    old = Path.cwd()
    try:
        import os

        os.chdir(repo)
        return runner.invoke(app, args, catch_exceptions=False)
    finally:
        os.chdir(old)


def test_integrate_repo_scope_installs_skills_and_wrappers(git_repo: Path):
    result = _run_in(git_repo, ["integrate", "--tool", "all", "--scope", "repo"])
    assert result.exit_code == 0
    assert (git_repo / "AGENTS.md").exists()
    assert (git_repo / ".agents" / "skills" / "autorunne-workflow" / "SKILL.md").exists()
    assert (git_repo / ".claude" / "skills" / "autorunne-workflow" / "SKILL.md").exists()
    assert (git_repo / ".cursor" / "rules" / "autorunne-workflow.mdc").exists()
    assert (git_repo / ".github" / "copilot-instructions.md").exists()
    assert (git_repo / ".autorunne" / "state" / "current.json").exists()
    assert (git_repo / ".autorunne" / "bin" / "ar-codex").exists()
    assert (git_repo / ".autorunne" / "bin" / "ar-claude").exists()
    assert (git_repo / ".autorunne" / "bin" / "ar-hermes").exists()
    agents_skill = (git_repo / ".agents" / "skills" / "autorunne-workflow" / "SKILL.md").read_text(encoding="utf-8")
    claude_skill = (git_repo / ".claude" / "skills" / "autorunne-workflow" / "SKILL.md").read_text(encoding="utf-8")
    cursor_rule = (git_repo / ".cursor" / "rules" / "autorunne-workflow.mdc").read_text(encoding="utf-8")
    copilot = (git_repo / ".github" / "copilot-instructions.md").read_text(encoding="utf-8")
    assert agents_skill.startswith("---\n")
    assert "name: autorunne-workflow" in agents_skill
    assert f"version: {__version__}" in agents_skill
    assert claude_skill.startswith("---\n")
    assert f"version: {__version__}" in claude_skill
    assert "open Codex directly" in agents_skill
    assert "autorunne ingest --source codex --task <task>" in agents_skill
    assert "load this repo skill" in agents_skill
    assert "Do not wait for the user to remind you to read Autorunne" in agents_skill
    assert cursor_rule.startswith("---\n")
    assert "alwaysApply: true" in cursor_rule
    assert "globs:" not in cursor_rule
    assert "autorunne ingest --source cursor --task <task>" in cursor_rule
    assert "load this repo skill" in cursor_rule
    assert "Do not wait for the user to remind you to read Autorunne" in cursor_rule
    assert "autorunne ingest --source copilot --task <task>" in copilot
    assert "load this repo skill" in copilot
    assert "Do not wait for the user to remind you to read Autorunne" in copilot


def test_open_auto_installs_repo_integrations(node_repo: Path):
    result = _run_in(node_repo, ["open"])
    assert result.exit_code == 0
    assert (node_repo / "AGENTS.md").exists()
    assert (node_repo / ".agents" / "skills" / "autorunne-workflow" / "SKILL.md").exists()
    assert (node_repo / ".claude" / "skills" / "autorunne-workflow" / "SKILL.md").exists()
    assert (node_repo / ".cursor" / "rules" / "autorunne-workflow.mdc").exists()
    assert (node_repo / ".github" / "copilot-instructions.md").exists()
    assert (node_repo / ".autorunne" / "bin" / "ar-codex").exists()
    skill_text = (node_repo / ".agents" / "skills" / "autorunne-workflow" / "SKILL.md").read_text(encoding="utf-8")
    assert skill_text.startswith("---\n")


def test_open_skips_existing_read_only_integrations_in_agent_sandbox(node_repo: Path, monkeypatch):
    first = _run_in(node_repo, ["open"])
    assert first.exit_code == 0
    protected_skill = node_repo / ".agents" / "skills" / "autorunne-workflow" / "SKILL.md"
    original_skill_text = protected_skill.read_text(encoding="utf-8")
    protected_skill.write_text(original_skill_text.replace(f"version: {__version__}", "version: 0.6.17"), encoding="utf-8")
    real_write_text = integrations.write_text

    def sandbox_write_text(path: Path, content: str) -> None:
        if path == protected_skill:
            raise OSError(30, "Read-only file system", str(path))
        real_write_text(path, content)

    monkeypatch.setattr(integrations, "write_text", sandbox_write_text)

    resumed = _run_in(node_repo, ["open"])

    assert resumed.exit_code == 0
    assert "resumed" in resumed.stdout
    assert "version: 0.6.17" in protected_skill.read_text(encoding="utf-8")
    log_text = (node_repo / ".autorunne" / "SESSION_LOG.md").read_text(encoding="utf-8")
    assert "Skipped read-only integration files" not in log_text


def test_integrate_refreshes_stale_repo_skill_version_when_explicitly_requested(node_repo: Path):
    first = _run_in(node_repo, ["open"])
    assert first.exit_code == 0

    agents_skill_path = node_repo / ".agents" / "skills" / "autorunne-workflow" / "SKILL.md"
    stale_text = agents_skill_path.read_text(encoding="utf-8").replace(f"version: {__version__}", "version: 0.6.17")
    agents_skill_path.write_text(stale_text, encoding="utf-8")

    resumed = _run_in(node_repo, ["open"])
    assert resumed.exit_code == 0
    assert "version: 0.6.17" in agents_skill_path.read_text(encoding="utf-8")

    refreshed = _run_in(node_repo, ["integrate", "--tool", "all", "--scope", "repo"])

    assert refreshed.exit_code == 0
    assert f"version: {__version__}" in agents_skill_path.read_text(encoding="utf-8")


def test_open_renders_standard_library_python_commands(standard_library_python_repo: Path):
    result = _run_in(standard_library_python_repo, ["open"])
    assert result.exit_code == 0
    start_here = (standard_library_python_repo / ".autorunne" / "views" / "START_HERE.md").read_text(encoding="utf-8")
    commands = (standard_library_python_repo / ".autorunne" / "views" / "COMMANDS.md").read_text(encoding="utf-8")
    context = (standard_library_python_repo / ".autorunne" / "views" / "PROJECT_CONTEXT.md").read_text(encoding="utf-8")
    assert "Stack: python" in start_here
    assert "Framework: python standard library, http.server" in start_here
    assert "python -m pytest -q" in start_here
    assert "python app.py" in start_here
    assert "No reliable run/test/build commands detected yet" not in commands
    assert "Package manager: none" in context
