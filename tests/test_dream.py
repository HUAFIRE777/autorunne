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


def test_hua_brain_integration(tmp_path: Path):
    from autorunne.core.hua_brain import (
        classify_domain,
        resolve_hua_brain,
        sync_signals_to_hua_brain,
    )

    # 1. Domain classification tests
    assert classify_domain("Three.js WebGL WebGPU rendering pipeline") == "graphics_3d"
    assert classify_domain("Reverse engineering AST parser EBNF grammar") == "reverse_engineering"
    assert classify_domain("Video multimodal ffmpeg cinematic camera") == "video_multimodal"
    assert classify_domain("ROI conversion business growth strategy") == "business_growth"

    # 2. Mock hua-brain workspace
    mock_brain = tmp_path / "mock-brain"
    (mock_brain / "core").mkdir(parents=True)
    (mock_brain / "core" / "HUA_CHARTER.md").write_text("# Charter\n", encoding="utf-8")
    (mock_brain / "index").mkdir(parents=True)
    (mock_brain / "dossiers" / "graphics_3d").mkdir(parents=True)

    # Test resolution via link
    mock_repo = tmp_path / "mock-repo"
    mock_repo.mkdir()
    (mock_repo / "brain").symlink_to(mock_brain)

    resolved = resolve_hua_brain(mock_repo)
    assert resolved == mock_brain

    # Test sync execution
    signals = [{
        "kind": "user_correction",
        "topic": "graphics_3d",
        "timestamp": "2026-11-02",
        "summary": "不是硬编码颜色，必须使用第一性原理进行设计",
        "source": "test_signal",
    }]
    report = sync_signals_to_hua_brain(mock_repo, signals, use_vertex=False)
    assert report["synced"] is True
    assert len(report["dossiers_created"]) >= 1

    # Verify dossier created
    dossiers = list((mock_brain / "dossiers" / "graphics_3d").glob("*.md"))
    assert len(dossiers) >= 1
    content = dossiers[0].read_text(encoding="utf-8")
    assert "华哥决策与第一性原理指示" in content
    assert "第一性原理" in content

    # 3. Test full execute_dream_cycle auto-sync
    cycle_res = execute_dream_cycle(mock_repo, explicit_rule="必须使用第一性原理，拒绝凭空臆想")
    assert "hua_brain" in cycle_res
    assert cycle_res["hua_brain"] is not None
    assert cycle_res["hua_brain"]["synced"] is True
