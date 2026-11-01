from pathlib import Path
from typer.testing import CliRunner

from autorunne.cli import app
from autorunne.core.dream import (
    check_index_budget,
    compact_index,
    execute_dream_cycle,
    scrub_secrets,
)

runner = CliRunner()


def test_scrub_secrets():
    raw = "Bearer sk-1234567890abcdef123456 and token: AIzaSyD1234567890abcdef1234567890abc"
    scrubbed = scrub_secrets(raw)
    assert "sk-1234567890abcdef123456" not in scrubbed
    assert "AIzaSyD" not in scrubbed
    assert "[REDACTED_SECRET]" in scrubbed


def test_check_index_budget(tmp_path: Path):
    index = tmp_path / "MEMORY.md"
    assert check_index_budget(index)["valid"] is True
    assert check_index_budget(index)["lines"] == 0

    index.write_text("\n".join(f"line {i}" for i in range(100)), encoding="utf-8")
    status = check_index_budget(index, max_lines=50)
    assert status["valid"] is False
    assert status["exceeded_by"] == 50


def test_compact_index_under_budget():
    content = "# Header\n\n- [rule 1](rule1.md)\n- [rule 2](rule2.md)\n"
    compacted = compact_index(content, max_lines=10)
    assert compacted == content


def test_cli_dream_status_and_record(tmp_path: Path):
    status_res = runner.invoke(app, ["dream", "--path", str(tmp_path), "--status"], catch_exceptions=False)
    assert status_res.exit_code == 0
    assert "Memory Status: HEALTHY" in status_res.stdout

    record_res = runner.invoke(
        app,
        ["dream", "--path", str(tmp_path), "--record", "Strictly enforce 200 line budget."],
        catch_exceptions=False,
    )
    assert record_res.exit_code == 0
    assert "Auto-Dream cycle completed" in record_res.stdout

    # Verify MEMORY.md exists and is within budget
    mem_file = tmp_path / ".autorunne" / "memory" / "MEMORY.md"
    assert mem_file.exists()
    assert len(mem_file.read_text(encoding="utf-8").splitlines()) < 200
