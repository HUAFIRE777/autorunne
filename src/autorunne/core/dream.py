from __future__ import annotations

import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_MAX_INDEX_LINES = 200

SECRET_PATTERNS = [
    re.compile(r"bearer\s+[a-zA-Z0-9_\-\.]{15,}", re.IGNORECASE),
    re.compile(r"ghp_[a-zA-Z0-9]{36}"),
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),
    re.compile(r"AIza[0-9A-Za-z-_]{35}"),
    re.compile(r"(?:api_key|apikey|secret|password|token)\s*[:=]\s*[\"']?([a-zA-Z0-9_\-\.]{10,})[\"']?", re.IGNORECASE),
    re.compile(r"-----BEGIN [A-Z ]+ PRIVATE KEY-----[\s\S]*?-----END [A-Z ]+ PRIVATE KEY-----"),
]

CORRECTION_TRIGGERS = [
    re.compile(r"不是|不对|换成|必须用|不要用|改成|注意规范|规矩|铁律", re.IGNORECASE),
    re.compile(r"fix:|wrong|instead of|must use|do not use|should be|never use", re.IGNORECASE),
]

ARCH_TRIGGERS = [
    re.compile(r"架构|规范|wasm|three\.js|webgl|webgpu|ebnf|ast|byok|cloudflare|rust|compiler|parser", re.IGNORECASE),
]


def scrub_secrets(text: str) -> str:
    cleaned = text
    for pat in SECRET_PATTERNS:
        cleaned = pat.sub("[REDACTED_SECRET]", cleaned)
    return cleaned


def resolve_memory_dir(repo_root: Path) -> Path:
    # Support both .agent/memory/ and .autorunne/memory/ seamlessly
    agent_mem = repo_root / ".agent" / "memory"
    if agent_mem.exists():
        return agent_mem
    autorunne_mem = repo_root / ".autorunne" / "memory"
    autorunne_mem.mkdir(parents=True, exist_ok=True)
    return autorunne_mem


def resolve_index_file(repo_root: Path) -> Path:
    agent_index = repo_root / ".agent" / "memory" / "MEMORY.md"
    if agent_index.exists():
        return agent_index
    autorunne_index = repo_root / ".autorunne" / "memory" / "MEMORY.md"
    return autorunne_index


def check_index_budget(index_path: Path, max_lines: int = DEFAULT_MAX_INDEX_LINES) -> dict[str, Any]:
    if not index_path.exists():
        return {
            "valid": True,
            "lines": 0,
            "max_lines": max_lines,
            "path": str(index_path),
            "exceeded_by": 0,
        }
    lines = len(index_path.read_text(encoding="utf-8").splitlines())
    return {
        "valid": lines <= max_lines,
        "lines": lines,
        "max_lines": max_lines,
        "path": str(index_path),
        "exceeded_by": max(0, lines - max_lines),
    }


def compact_index(content: str, max_lines: int = DEFAULT_MAX_INDEX_LINES) -> str:
    raw_lines = content.splitlines()
    if len(raw_lines) <= max_lines:
        return content

    header_lines: list[str] = []
    entry_lines: list[str] = []
    is_header = True

    for line in raw_lines:
        trimmed = line.strip()
        if trimmed.startswith("#") or trimmed.startswith(">") or not trimmed:
            if is_header:
                header_lines.append(line)
        else:
            is_header = False
            if trimmed.startswith("- [") or trimmed.startswith("* ["):
                entry_lines.append(trimmed)

    remaining_budget = max_lines - len(header_lines) - 3
    kept_entries = entry_lines[-max(10, remaining_budget):]

    compacted = [
        *header_lines,
        "",
        f"> [!NOTE] Compacted automatically by AutoRunne 2.0 Dream Guard at {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        "",
        *kept_entries,
    ]
    return "\n".join(compacted) + "\n"


def infer_topic(text: str) -> str:
    lower = text.lower()
    if any(k in lower for k in ["three", "webgl", "webgpu", "shader", "render", "mesh", "frame"]):
        return "graphics_rendering"
    if any(k in lower for k in ["wasm", "rust", "crate", "c++", "simd"]):
        return "wasm_core_algorithms"
    if any(k in lower for k in ["ebnf", "ast", "parser", "grammar", "compiler", "3d-language"]):
        return "3d_language_spec"
    if any(k in lower for k in ["byok", "cloudflare", "kv", "d1", "r2", "api", "auth", "secret"]):
        return "backend_infra"
    return "general_rules"


def gather_signals(repo_root: Path) -> list[dict[str, Any]]:
    signals: list[dict[str, Any]] = []
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # 1. Read recent AutoRunne events from .autorunne/state/events.jsonl
    events_file = repo_root / ".autorunne" / "state" / "events.jsonl"
    if events_file.exists():
        try:
            lines = events_file.read_text(encoding="utf-8").splitlines()
            for line in lines[-100:]:  # Last 100 events
                if not line.strip():
                    continue
                import json
                event = json.loads(line)
                payload = event.get("payload", {})
                summary = payload.get("summary") or payload.get("decision") or payload.get("task") or ""
                if not summary:
                    continue

                cleaned = scrub_secrets(str(summary))
                if any(t.search(cleaned) for t in CORRECTION_TRIGGERS):
                    signals.append({
                        "kind": "user_correction",
                        "topic": infer_topic(cleaned),
                        "timestamp": now_iso,
                        "summary": cleaned[:160].replace("\n", " "),
                        "source": "autorunne_events",
                    })
                elif any(t.search(cleaned) for t in ARCH_TRIGGERS):
                    signals.append({
                        "kind": "arch_decision",
                        "topic": infer_topic(cleaned),
                        "timestamp": now_iso,
                        "summary": cleaned[:160].replace("\n", " "),
                        "source": "autorunne_events",
                    })
        except Exception:
            pass

    # 2. Read session transcripts if present
    transcripts_dir = repo_root / ".agent" / "transcripts"
    if transcripts_dir.exists():
        for file_p in transcripts_dir.glob("*.jsonl"):
            try:
                for line in file_p.read_text(encoding="utf-8").splitlines():
                    if not line.strip():
                        continue
                    import json
                    entry = json.loads(line)
                    text = entry.get("content") or entry.get("message") or ""
                    if text and isinstance(text, str):
                        cleaned = scrub_secrets(text)
                        if any(t.search(cleaned) for t in CORRECTION_TRIGGERS):
                            signals.append({
                                "kind": "user_correction",
                                "topic": infer_topic(cleaned),
                                "timestamp": now_iso,
                                "summary": cleaned[:160].replace("\n", " "),
                                "source": file_p.name,
                            })
            except Exception:
                pass

    return signals


def execute_dream_cycle(repo_root: Path, *, explicit_rule: str | None = None) -> dict[str, Any]:
    """
    Executes the 4-Phase Auto-Dream Protocol natively inside AutoRunne:
    Phase 1: Orient (Check line budget and ensure index exists)
    Phase 2: Gather (Extract corrections & decisions from autorunne events & git)
    Phase 3: Consolidate (Merge into topic markdown files)
    Phase 4: Prune & Index (Re-index MEMORY.md and strictly enforce <200 lines)
    """
    mem_dir = resolve_memory_dir(repo_root)
    index_path = resolve_index_file(repo_root)
    project_name = repo_root.name

    # Phase 1: Orient & Auto-Initialize if missing
    if not index_path.exists():
        mem_dir.mkdir(parents=True, exist_ok=True)
        init_content = f"""# {project_name} - Agent Cognitive Memory Index

> [!IMPORTANT]
> **Strict Claude Code Budget Rule**: This file MUST stay under 200 lines.
> All detailed knowledge is modularized into topic files under `{mem_dir.relative_to(repo_root)}/`.
> Any agent entering this repository MUST read this file first.

## 1. Project Essence & Core Missions
- **Description**: AutoRunne 2.0 Cognitive Workspace for {project_name}
- **Last Dream Consolidation**: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}

## 2. Topic Index & Knowledge Anchors
- [Architecture & Governance](./architecture_rules.md) - Core technology stack and performance boundaries.
- [User Preferences & Corrections](./user_preferences.md) - Active developer habits, style guides, and non-negotiable rules.
- [Active Roadmap & Status](./project_status.md) - Ongoing tasks, milestones, and verified deliverables.

## 3. Seamless Agent Handover Protocol
- When starting any task, verify current state from the topic files above.
- In-context model reflection: The active model writing code distills rules directly.
"""
        index_path.write_text(init_content, encoding="utf-8")

        for topic in ["architecture_rules.md", "user_preferences.md", "project_status.md"]:
            tp = mem_dir / topic
            if not tp.exists():
                tp.write_text(f"# {topic.replace('.md', '').replace('_', ' ').title()}\n\n- Baseline established.\n", encoding="utf-8")

    budget_status = check_index_budget(index_path)

    # Phase 2: Gather Signals
    signals = gather_signals(repo_root)
    if explicit_rule:
        cleaned_rule = scrub_secrets(explicit_rule)
        signals.append({
            "kind": "user_correction",
            "topic": infer_topic(cleaned_rule),
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "summary": cleaned_rule[:160].replace("\n", " "),
            "source": "explicit_record",
        })

    # Phase 3: Consolidate
    modified_topics: list[str] = []
    for sig in signals:
        topic_file = mem_dir / f"{sig['topic']}.md"
        entry = f"\n- **[{sig['timestamp']}] ({sig['kind']})**: {sig['summary']}\n  - *Action*: Follow this rule in future sessions.\n"
        if topic_file.exists():
            topic_file.write_text(topic_file.read_text(encoding="utf-8") + entry, encoding="utf-8")
        else:
            topic_file.write_text(f"# Topic: {sig['topic']}\n\nConsolidated knowledge extracted during Auto-Dream.\n" + entry, encoding="utf-8")
        if topic_file.name not in modified_topics:
            modified_topics.append(topic_file.name)

    # Phase 4: Prune & Index
    current_index_text = index_path.read_text(encoding="utf-8")
    for topic_f in mem_dir.glob("*.md"):
        if topic_f.name == "MEMORY.md":
            continue
        link = f"- [{topic_f.stem.replace('_', ' ')}]({topic_f.name})"
        if link not in current_index_text and topic_f.name not in current_index_text:
            current_index_text += f"\n{link}"

    final_index_text = compact_index(current_index_text, DEFAULT_MAX_INDEX_LINES)
    index_path.write_text(final_index_text, encoding="utf-8")

    final_budget = check_index_budget(index_path)

    # 扩展挂载: 若存在 3D-language 或特定项目的专有生长引擎，无缝联动驱动
    custom_hook = repo_root / "autodream_3d.py"
    if custom_hook.exists():
        try:
            import subprocess
            subprocess.run([sys.executable, str(custom_hook), "--grow"], cwd=repo_root, capture_output=True, timeout=10)
        except Exception:
            pass

    # 终身认知大脑挂载: 自动确保软链接桥接，并将高价值认知信号静默蒸馏入库并同步
    hua_brain_report = None
    try:
        from autorunne.core.hua_brain import link_hua_brain, sync_signals_to_hua_brain
        link_hua_brain(repo_root)
        hua_brain_report = sync_signals_to_hua_brain(repo_root, signals)
    except Exception:
        pass

    return {
        "status": "ok" if final_budget["valid"] else "warning",
        "index_lines": final_budget["lines"],
        "max_lines": final_budget["max_lines"],
        "signals_gathered": len(signals),
        "modified_topics": modified_topics,
        "index_path": str(index_path),
        "hua_brain": hua_brain_report,
    }
