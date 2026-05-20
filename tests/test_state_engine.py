from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from autorunne import __version__
from autorunne.cli import app

runner = CliRunner()


def _run_in(repo: Path, args: list[str]):
    old = Path.cwd()
    try:
        import os

        os.chdir(repo)
        return runner.invoke(app, args, catch_exceptions=False)
    finally:
        os.chdir(old)


def test_render_rebuilds_deleted_view_from_state(python_repo: Path):
    init_result = _run_in(python_repo, ["init"])
    assert init_result.exit_code == 0

    start_here = python_repo / ".autorunne" / "views" / "START_HERE.md"
    assert start_here.exists()
    start_here.unlink()
    assert not start_here.exists()

    render_result = _run_in(python_repo, ["render"])
    assert render_result.exit_code == 0
    assert start_here.exists()
    assert "Zero-prompt handoff" in start_here.read_text(encoding="utf-8")


def test_open_imports_legacy_markdown_workspace(python_repo: Path):
    workflow_root = python_repo / ".autorunne"
    workflow_root.mkdir()
    (workflow_root / "NEXT_ACTION.md").write_text("# Next Action\n\nLegacy next step\n", encoding="utf-8")
    (workflow_root / "TASKS.md").write_text(
        "# Tasks\n\n## Completed / inferred\n\n## In progress\n- [ ] Legacy in-progress task\n\n## Next up\n- [ ] Legacy next step\n\n## Known unknowns\n- [ ] Legacy unknown\n",
        encoding="utf-8",
    )

    result = _run_in(python_repo, ["open"])
    assert result.exit_code == 0
    current_text = (workflow_root / "state" / "current.json").read_text(encoding="utf-8")
    tasks_text = (workflow_root / "views" / "TASKS.md").read_text(encoding="utf-8")
    assert "Legacy next step" in current_text
    assert "Legacy in-progress task" in tasks_text


def test_sync_preserves_explicit_next_action_from_state(python_repo: Path):
    _run_in(python_repo, ["adopt"])
    _run_in(python_repo, ["start", "--task", "Keep auth stable", "--next", "Custom next step"])

    result = _run_in(python_repo, ["sync"])
    assert result.exit_code == 0

    current_text = (python_repo / ".autorunne" / "state" / "current.json").read_text(encoding="utf-8")
    next_text = (python_repo / ".autorunne" / "views" / "NEXT_ACTION.md").read_text(encoding="utf-8")
    assert "Custom next step" in current_text
    assert "Custom next step" in next_text


def test_sync_renders_haopay_style_monorepo_from_packages(haopay_style_monorepo: Path):
    result = _run_in(haopay_style_monorepo, ["sync"])
    assert result.exit_code == 0

    state_root = haopay_style_monorepo / ".autorunne" / "state"
    views_root = haopay_style_monorepo / ".autorunne" / "views"
    current = json.loads((state_root / "current.json").read_text(encoding="utf-8"))
    start_here = (views_root / "START_HERE.md").read_text(encoding="utf-8")
    project_context = (views_root / "PROJECT_CONTEXT.md").read_text(encoding="utf-8")
    commands = (views_root / "COMMANDS.md").read_text(encoding="utf-8")

    assert current["stack"] == ["multi-package Node/TypeScript"]
    assert "generic" not in current["stack"]
    assert "Vite frontend" in current["framework"]
    assert "Node.js backend" in current["framework"]
    assert "Hardhat smart contracts" in current["framework"]
    assert current["commands"]["frontend:build"] == "cd frontend && npm run build"
    assert current["commands"]["backend:test"] == "cd backend && npm test"
    assert current["commands"]["contracts:compile"] == "cd contracts && npm run compile"
    assert current["commands"]["contracts:test"] == "cd contracts && npm test"

    assert "Stack: generic" not in start_here
    assert "Stack: multi-package Node/TypeScript" in start_here
    assert "Vite frontend" in project_context
    assert "Package manager: npm per package" in project_context
    assert "frontend/package.json" in project_context
    assert "backend/package.json" in project_context
    assert "contracts/package.json" in project_context
    assert "No reliable run/test/build commands detected yet" not in commands
    assert "cd frontend && npm run build" in commands
    assert "cd backend && npm test" in commands
    assert "cd contracts && npm run compile" in commands


def test_render_uses_packages_when_existing_current_summary_is_generic(haopay_style_monorepo: Path):
    _run_in(haopay_style_monorepo, ["sync"])
    state_file = haopay_style_monorepo / ".autorunne" / "state" / "current.json"
    current = json.loads(state_file.read_text(encoding="utf-8"))
    packages = current["packages"]
    current["stack"] = ["generic"]
    current["framework"] = ["generic"]
    current["package_manager"] = ["unknown"]
    current["commands"] = {}
    current["packages"] = packages
    state_file.write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    result = _run_in(haopay_style_monorepo, ["render"])
    assert result.exit_code == 0

    commands = (haopay_style_monorepo / ".autorunne" / "views" / "COMMANDS.md").read_text(encoding="utf-8")
    start_here = (haopay_style_monorepo / ".autorunne" / "views" / "START_HERE.md").read_text(encoding="utf-8")
    assert "Stack: generic" not in start_here
    assert "Stack: multi-package Node/TypeScript" in start_here
    assert "No reliable run/test/build commands detected yet" not in commands
    assert "cd frontend && npm run build" in commands


def test_checkpoint_records_validation_details(python_repo: Path):
    _run_in(python_repo, ["adopt"])
    result = _run_in(
        python_repo,
        ["checkpoint", "--summary", "Saved progress", "--next", "Continue slice", "--validate", "pytest -q"],
    )
    assert result.exit_code == 0
    assert "Validation: passed" in result.stdout

    sessions_text = (python_repo / ".autorunne" / "state" / "sessions.json").read_text(encoding="utf-8")
    assert "Validation command" in sessions_text
    assert "pytest -q" in sessions_text


def test_finish_records_structured_state_details(python_repo: Path):
    _run_in(python_repo, ["adopt"])
    (python_repo / "src" / "app.py").write_text("print('state changed')\n", encoding="utf-8")

    result = _run_in(
        python_repo,
        ["finish", "--summary", "Recorded state detail", "--validate", "pytest -q", "--next", "Ship docs"],
    )
    assert result.exit_code == 0

    state_root = python_repo / ".autorunne" / "state"
    sessions_text = (state_root / "sessions.json").read_text(encoding="utf-8")
    events_text = (state_root / "events.jsonl").read_text(encoding="utf-8")
    current_text = (state_root / "current.json").read_text(encoding="utf-8")

    assert "Recorded state detail" in sessions_text
    assert "git_status" in sessions_text
    assert "diff_stat" in sessions_text
    assert "validation" in sessions_text
    assert "task_finished" in events_text
    assert "Ship docs" in current_text


def test_finish_keeps_session_log_validation_output_concise_and_status_visible(python_repo: Path):
    _run_in(python_repo, ["adopt"])
    long_script = "for i in range(30): print('line %s' % i)"

    result = _run_in(
        python_repo,
        [
            "finish",
            "--summary",
            "Recorded concise validation",
            "--validate",
            f'python -c "{long_script}"',
            "--next",
            "Continue product slice",
        ],
    )
    assert result.exit_code == 0

    session_log = (python_repo / ".autorunne" / "SESSION_LOG.md").read_text(encoding="utf-8")
    status = (python_repo / ".autorunne" / "views" / "STATUS.md").read_text(encoding="utf-8")
    assert "Validation command:" in session_log
    assert "validation_output:" in session_log
    assert "line 0" in session_log
    assert "line 29" not in session_log
    assert "more lines omitted" in session_log
    assert "验证命令：`python -c" in status
    assert "验证结果摘要：line 0" in status


def test_repeated_open_does_not_duplicate_identical_resume_or_integration_logs(python_repo: Path):
    _run_in(python_repo, ["open"])
    _run_in(python_repo, ["open"])

    # Simulate a real agent handoff where an integration refresh/noise entry can
    # sit between two otherwise identical open auto-resume events. Existing
    # repo-local agent skill files should not be silently rewritten by open.
    skill_path = python_repo / ".agents" / "skills" / "autorunne-workflow" / "SKILL.md"
    older_skill_text = skill_path.read_text(encoding="utf-8").replace(f"version: {__version__}", "version: 0.6.0")
    skill_path.write_text(older_skill_text, encoding="utf-8")
    _run_in(python_repo, ["open"])
    _run_in(python_repo, ["open"])

    log_text = (python_repo / ".autorunne" / "SESSION_LOG.md").read_text(encoding="utf-8")
    assert log_text.count("| workspace open auto-resume") == 1
    assert log_text.count("integration updated") <= 1
    assert skill_path.read_text(encoding="utf-8") == older_skill_text


def test_finish_handoff_uses_one_product_next_action_for_new_agents(python_repo: Path):
    _run_in(python_repo, ["adopt"])
    _run_in(
        python_repo,
        [
            "start",
            "--task",
            "Lesson 09/10 real development",
            "--next",
            "Old Lesson 08 workflow note",
        ],
    )
    _run_in(python_repo, ["task", "add", "--text", "Lesson 11 mobile polish"])

    result = _run_in(
        python_repo,
        [
            "finish",
            "--summary",
            "Lesson 09/10 completed",
            "--task",
            "Lesson 09/10",
            "--validate",
            "pytest -q",
            "--next",
            "Lesson 11 mobile polish",
        ],
    )
    assert result.exit_code == 0

    state_root = python_repo / ".autorunne" / "state"
    views_root = python_repo / ".autorunne" / "views"
    current = json.loads((state_root / "current.json").read_text(encoding="utf-8"))
    tasks = json.loads((state_root / "tasks.json").read_text(encoding="utf-8"))
    events = [json.loads(line) for line in (state_root / "events.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    start_here = (views_root / "START_HERE.md").read_text(encoding="utf-8")
    next_action = (views_root / "NEXT_ACTION.md").read_text(encoding="utf-8")
    status_result = _run_in(python_repo, ["status"])

    assert current["active_task"] is None
    assert current["last_action"] == "task_finished"
    assert current["next_action"] == "Lesson 11 mobile polish"
    assert current["next_product_task"] == "Lesson 11 mobile polish"
    assert tasks["next_up"][0]["text"] == "Lesson 11 mobile polish"
    assert current["last_validation"]["command"] == "pytest -q"
    assert current["last_validation"]["status"] == "passed"
    assert current["last_validation"]["timestamp"]
    assert "task_finished" in [event["type"] for event in events]
    assert "Next product task：Lesson 11 mobile polish" in start_here
    assert "- 下一步：Lesson 11 mobile polish" in start_here
    assert "- Next action: Lesson 11 mobile polish" in start_here
    assert "## Next product task\nLesson 11 mobile polish" in next_action
    assert "## Legacy combined next action\nLesson 11 mobile polish" in next_action
    assert status_result.exit_code == 0
    assert "Next action" in status_result.stdout
    assert "Lesson 11 mobile polish" in status_result.stdout


def test_finish_workflow_follow_up_does_not_override_product_next_action(python_repo: Path):
    _run_in(python_repo, ["adopt"])
    _run_in(python_repo, ["start", "--task", "Lesson 09/10 real development", "--next", "Lesson 11 mobile polish"])

    result = _run_in(
        python_repo,
        [
            "finish",
            "--summary",
            "Lesson 09/10 completed",
            "--task",
            "Lesson 09/10",
            "--no-validate",
            "--next",
            "Workflow follow-up: review rendered STATUS and START_HERE",
        ],
    )
    assert result.exit_code == 0

    current = json.loads((python_repo / ".autorunne" / "state" / "current.json").read_text(encoding="utf-8"))
    start_here = (python_repo / ".autorunne" / "views" / "START_HERE.md").read_text(encoding="utf-8")
    assert current["next_action"] == "Lesson 11 mobile polish"
    assert current["next_product_task"] == "Lesson 11 mobile polish"
    assert current["workflow_follow_up"] == "Workflow follow-up: review rendered STATUS and START_HERE"
    assert "- 下一步：Lesson 11 mobile polish" in start_here
    assert "Workflow follow-up：Workflow follow-up: review rendered STATUS and START_HERE" in start_here
