from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import time
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from autorunne.core.dream import scrub_secrets, CORRECTION_TRIGGERS, ARCH_TRIGGERS


VERTEX_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "skillful-air-513105-k2")
VERTEX_MODEL_ID = "gemini-4-argon"
VERTEX_TIMEOUT_SECONDS = 12

DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "graphics_3d": [
        "three", "webgl", "webgpu", "shader", "render", "mesh", "frame",
        "spline", "optics", "gimbal", "motor", "cad", "3d", "scene", "camera",
        "material", "canvas", "geometry", "lighting", "blender",
    ],
    "reverse_engineering": [
        "reverse", "decompile", "ast", "parser", "ebnf", "grammar", "wasm",
        "rust", "binary", "crate", "radar", "sniff", "hook", "disassemble",
        "eazyopc", "opc", "token", "lexer",
    ],
    "video_multimodal": [
        "video", "multimodal", "gemini", "argon", "diffusion", "cinema",
        "frame", "audio", "tts", "animation", "storyboard", "cinematic",
        "ffmpeg", "veo", "sora", "motion",
    ],
    "business_growth": [
        "growth", "business", "roi", "pricing", "conversion", "first-principles",
        "first_principles", "rational", "efficiency", "charter", "strategy",
        "revenue", "profit", "monetization", "retention", "decision",
    ],
}


@dataclass
class KnowledgeDossier:
    title: str
    domain: str
    project_source: str
    agent_source: str
    summary: str
    hua_decisions: list[str]
    technical_solution: str
    reusable_rules: list[str]
    tags: list[str] = field(default_factory=list)


def resolve_hua_brain(repo_root: Path | None = None) -> Path | None:
    """
    Resolves the centralized hua-brain repository location seamlessly:
    1. Direct local link (repo_root / "brain")
    2. Explicit environment variable HUA_BRAIN_PATH
    3. Standard user Desktop location (~/Desktop/program/hua-brain)
    4. Standard user program location (~/program/hua-brain)
    """
    candidates: list[Path] = []

    if repo_root is not None:
        local_brain = repo_root / "brain"
        if local_brain.exists():
            candidates.append(local_brain.resolve())

    env_path = os.getenv("HUA_BRAIN_PATH")
    if env_path:
        candidates.append(Path(env_path).expanduser().resolve())

    home = Path.home()
    candidates.append((home / "Desktop" / "program" / "hua-brain").resolve())
    candidates.append((home / "program" / "hua-brain").resolve())

    for c in candidates:
        if c.exists() and (c / "core" / "HUA_CHARTER.md").exists():
            return c
        if c.exists() and (c / "index" / "MASTER_INDEX.json").exists():
            return c

    return None


def link_hua_brain(repo_root: Path) -> Path | None:
    """
    Ensures the target project repository has a symlink `brain -> hua-brain`
    and ignores it in .git/info/exclude, enabling any coding agent to instantly
    read and autonomously learn the First-Principles Charter & master index.
    """
    brain_root = resolve_hua_brain(repo_root)
    if not brain_root or brain_root.resolve() == repo_root.resolve():
        return None

    brain_link = repo_root / "brain"
    if not brain_link.exists() and not brain_link.is_symlink():
        try:
            brain_link.symlink_to(brain_root)
        except Exception:
            pass

    # Exclude brain from git tracking in this repository
    git_exclude = repo_root / ".git" / "info" / "exclude"
    if git_exclude.parent.exists():
        try:
            current_excludes = git_exclude.read_text(encoding="utf-8") if git_exclude.exists() else ""
            if "brain" not in current_excludes.splitlines():
                with open(git_exclude, "a", encoding="utf-8") as f:
                    f.write("\nbrain\n")
        except Exception:
            pass

    return brain_root


def classify_domain(text: str) -> str:
    """Classifies content into one of hua-brain's 4 core knowledge domains."""
    lower = text.lower()
    scores: dict[str, int] = {domain: 0 for domain in DOMAIN_KEYWORDS}

    for domain, kws in DOMAIN_KEYWORDS.items():
        for kw in kws:
            if kw in lower:
                scores[domain] += 1

    best_domain, best_score = max(scores.items(), key=lambda item: item[1])
    if best_score > 0:
        return best_domain
    return "business_growth" if any(k in lower for k in ["rule", "原则", "规范", "不要", "必须"]) else "graphics_3d"


def harvest_recent_git_signals(repo_root: Path, max_commits: int = 5) -> list[dict[str, Any]]:
    """Extracts recent commit messages that contain corrections or architectural choices."""
    signals: list[dict[str, Any]] = []
    try:
        res = subprocess.run(
            ["git", "-C", str(repo_root), "log", f"-n{max_commits}", "--pretty=format:%h|%s|%b"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        if res.returncode != 0 or not res.stdout.strip():
            return []

        for line in res.stdout.splitlines():
            parts = line.split("|", 2)
            if not parts:
                continue
            commit_hash = parts[0]
            subject = parts[1] if len(parts) > 1 else ""
            body = parts[2] if len(parts) > 2 else ""
            full_text = f"{subject} {body}".strip()

            cleaned = scrub_secrets(full_text)
            if any(t.search(cleaned) for t in CORRECTION_TRIGGERS):
                signals.append({
                    "kind": "user_correction",
                    "topic": classify_domain(cleaned),
                    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                    "summary": cleaned[:160].replace("\n", " "),
                    "source": f"git_commit_{commit_hash}",
                })
            elif any(t.search(cleaned) for t in ARCH_TRIGGERS):
                signals.append({
                    "kind": "arch_decision",
                    "topic": classify_domain(cleaned),
                    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                    "summary": cleaned[:160].replace("\n", " "),
                    "source": f"git_commit_{commit_hash}",
                })
    except Exception:
        pass
    return signals


def read_file_tail_lines(file_path: Path, max_bytes: int = 65536) -> list[str]:
    """Reads the last max_bytes of a file and splits into lines safely and instantly."""
    try:
        size = file_path.stat().st_size
        with open(file_path, "rb") as f:
            if size > max_bytes:
                f.seek(size - max_bytes)
            raw = f.read().decode("utf-8", errors="ignore")
            lines = raw.splitlines()
            return lines[1:] if size > max_bytes else lines
    except Exception:
        return []


def harvest_claude_history(project_name: str, limit_count: int = 25) -> list[dict[str, Any]]:
    """Pulls recent user directions from Claude Code history if present."""
    history_file = Path.home() / ".claude" / "history.jsonl"
    if not history_file.exists():
        return []
    signals: list[dict[str, Any]] = []
    try:
        lines = read_file_tail_lines(history_file, max_bytes=32768)
        for line in lines[-limit_count:]:
            if not line.strip():
                continue
            data = json.loads(line)
            disp = data.get("display", "")
            proj = data.get("project", "")
            if len(disp) > 15 and not disp.startswith("/") and (proj == project_name or not proj):
                cleaned = scrub_secrets(disp)
                if any(t.search(cleaned) for t in CORRECTION_TRIGGERS) or any(t.search(cleaned) for t in ARCH_TRIGGERS):
                    signals.append({
                        "kind": "user_correction" if any(t.search(cleaned) for t in CORRECTION_TRIGGERS) else "arch_decision",
                        "topic": classify_domain(cleaned),
                        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                        "summary": cleaned[:160].replace("\n", " "),
                        "source": "claude_history",
                    })
    except Exception:
        pass
    return signals


def harvest_antigravity_history(limit_count: int = 15) -> list[dict[str, Any]]:
    """Pulls recent user directions from Antigravity transcripts if present."""
    gemini_brain = Path.home() / ".gemini" / "antigravity" / "brain"
    if not gemini_brain.exists():
        return []
    signals: list[dict[str, Any]] = []
    try:
        sessions = sorted(
            gemini_brain.glob("*/.system_generated/logs/transcript.jsonl"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        for s_file in sessions[:2]:
            lines = read_file_tail_lines(s_file, max_bytes=65536)
            for line in lines[-limit_count * 2:]:
                if "USER_EXPLICIT" in line or "USER_INPUT" in line:
                    try:
                        data = json.loads(line)
                        content = data.get("content", "")
                        if len(content) > 15:
                            cleaned = scrub_secrets(content)
                            if any(t.search(cleaned) for t in CORRECTION_TRIGGERS) or any(t.search(cleaned) for t in ARCH_TRIGGERS):
                                signals.append({
                                    "kind": "user_correction" if any(t.search(cleaned) for t in CORRECTION_TRIGGERS) else "arch_decision",
                                    "topic": classify_domain(cleaned),
                                    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                                    "summary": cleaned[:160].replace("\n", " "),
                                    "source": "antigravity_transcript",
                                })
                    except Exception:
                        pass
    except Exception:
        pass
    return signals[:limit_count]


def harvest_grok_history(limit_count: int = 15) -> list[dict[str, Any]]:
    """Pulls recent user directions from Grok session prompt histories if present."""
    grok_sessions = Path.home() / ".grok" / "sessions"
    if not grok_sessions.exists():
        return []
    signals: list[dict[str, Any]] = []
    try:
        histories = sorted(
            grok_sessions.glob("*/prompt_history.jsonl"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        for h_file in histories[:2]:
            lines = read_file_tail_lines(h_file, max_bytes=65536)
            for line in lines[-limit_count:]:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    prompt = data.get("prompt", "")
                    if len(prompt) > 15:
                        cleaned = scrub_secrets(prompt)
                        if any(t.search(cleaned) for t in CORRECTION_TRIGGERS) or any(t.search(cleaned) for t in ARCH_TRIGGERS):
                            signals.append({
                                "kind": "user_correction" if any(t.search(cleaned) for t in CORRECTION_TRIGGERS) else "arch_decision",
                                "topic": classify_domain(cleaned),
                                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                                "summary": cleaned[:160].replace("\n", " "),
                                "source": "grok_session",
                            })
                except Exception:
                    pass
    except Exception:
        pass
    return signals[:limit_count]


def distill_signal_with_argon(
    signal: dict[str, Any],
    project_name: str,
    use_vertex: bool = True,
) -> KnowledgeDossier:
    """
    Distills raw cognitive signals into a high-grade knowledge dossier.
    First attempts company Google Cloud Vertex AI (gemini-4-argon) with zero-cost corporate quota.
    Falls back gracefully to deterministic rule extraction if offline or timed out.
    """
    raw_text = signal.get("summary", "")
    domain = signal.get("topic") or classify_domain(raw_text)

    # 1. Attempt Vertex AI gemini-4-argon distillation
    if use_vertex:
        try:
            token_res = subprocess.run(
                ["gcloud", "auth", "print-access-token"],
                capture_output=True,
                text=True,
                timeout=4,
            )
            token = token_res.stdout.strip()
            if token and not token.startswith("ERROR"):
                endpoint = (
                    f"https://aiplatform.googleapis.com/v1/projects/{VERTEX_PROJECT_ID}/"
                    f"locations/global/publishers/google/models/{VERTEX_MODEL_ID}:generateContent"
                )
                prompt = f"""你现在是华哥统一认知中枢 (hua-brain) 终身认知蒸馏器。
请对以下来自项目 [{project_name}] 的 Agent 交互与工程实践信号进行深度提炼：
1. 提取华哥在此次操作中展现的第一性原理、决策边界或绝对禁忌；
2. 提炼核心技术方案与避坑逻辑；
3. 输出纯正 JSON 格式，严禁包含 markdown 代码块包裹标记：
{{
  "title": "档案标题（20字内）",
  "domain": "{domain}",
  "summary": "一句话核心结论（50字内）",
  "hua_decisions": ["华哥明确要求/纠偏点"],
  "technical_solution": "技术本质解决方案与核心逻辑",
  "reusable_rules": ["通用规则1"],
  "tags": ["{project_name}", "{domain}"]
}}

原始信号内容：
{raw_text}
"""
                req_body = {
                    "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.2,
                        "maxOutputTokens": 1024,
                        "responseMimeType": "application/json",
                    },
                }
                req = urllib.request.Request(
                    endpoint,
                    data=json.dumps(req_body).encode("utf-8"),
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=VERTEX_TIMEOUT_SECONDS) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    raw_json = data["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = json.loads(raw_json)

                    return KnowledgeDossier(
                        title=parsed.get("title", f"{project_name} 关键实践"),
                        domain=parsed.get("domain", domain),
                        project_source=project_name,
                        agent_source=signal.get("source", "autorunne_ambient"),
                        summary=parsed.get("summary", raw_text[:60]),
                        hua_decisions=parsed.get("hua_decisions", [raw_text]),
                        technical_solution=parsed.get("technical_solution", f"在项目 {project_name} 中验证通过的工程决策。"),
                        reusable_rules=parsed.get("reusable_rules", [raw_text]),
                        tags=parsed.get("tags", [project_name, domain]),
                    )
        except Exception:
            pass

    # 2. Resilient Deterministic Fallback
    clean_title = raw_text.split("：")[-1].split(":")[-1].strip()
    if len(clean_title) > 25:
        clean_title = clean_title[:25] + "..."

    return KnowledgeDossier(
        title=f"{project_name} 研学: {clean_title}",
        domain=domain,
        project_source=project_name,
        agent_source=signal.get("source", "autorunne_ambient"),
        summary=raw_text[:80],
        hua_decisions=[raw_text],
        technical_solution=f"在项目 `{project_name}` 中实战沉淀的工程技术结论与规矩。\n\n- 触发来源: `{signal.get('source', 'autorunne')}`\n- 记录时间: `{signal.get('timestamp')}`",
        reusable_rules=[raw_text],
        tags=[project_name, domain, signal.get("kind", "rule")],
    )


def compute_signal_fingerprint(text: str) -> str:
    """Computes a stable hash fingerprint for deduplication."""
    normalized = re.sub(r"\s+", "", text.lower())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:12]


def is_already_recorded(brain_root: Path, domain: str, fingerprint: str, text: str) -> bool:
    """Checks whether the signal is already present in domain index or recent dossiers."""
    idx_file = brain_root / "index" / f"{domain}.json"
    if idx_file.exists():
        try:
            data = json.loads(idx_file.read_text(encoding="utf-8"))
            for rec in data.get("records", []):
                rec_summary = rec.get("summary", "")
                if fingerprint in rec.get("id", "") or rec.get("fingerprint") == fingerprint:
                    return True
                if text and rec_summary and (text in rec_summary or rec_summary in text):
                    return True
        except Exception:
            pass

    domain_dir = brain_root / "dossiers" / domain
    if domain_dir.exists():
        for d in domain_dir.glob(f"*{fingerprint}*.md"):
            return True
    return False


def persist_dossier_to_brain(
    brain_root: Path,
    dossier: KnowledgeDossier,
    fingerprint: str,
) -> Path:
    """Writes knowledge dossier markdown file and updates index files."""
    domain_dir = brain_root / "dossiers" / dossier.domain
    domain_dir.mkdir(parents=True, exist_ok=True)

    slug = re.sub(r"[^\w\-_]+", "_", dossier.title.lower().strip())
    card_id = f"DOSSIER-{dossier.domain.upper()[:3]}-{fingerprint}"
    filename = f"DOSSIER_autorunne_{dossier.project_source}_{slug}_{fingerprint}.md"
    file_path = domain_dir / filename

    decisions_md = "\n".join([f"- **决策**: {d}" for d in dossier.hua_decisions]) or "- 无特定新规则"
    rules_md = "\n".join([f"- {r}" for r in dossier.reusable_rules]) or "- 无"

    content = f"""# 🧠 认知全案：{dossier.title}

- **档案编号**: `{card_id}`
- **智能体来源**: `{dossier.agent_source}`
- **项目来源**: `{dossier.project_source}`
- **归属领域**: `{dossier.domain}`
- **核心结论**: {dossier.summary}
- **标签**: `{'`, `'.join(dossier.tags)}`

---

## 一、 华哥决策与第一性原理指示
{decisions_md}

---

## 二、 技术本质解决方案
{dossier.technical_solution}

---

## 三、 未来跨项目复用守则
{rules_md}
"""
    file_path.write_text(content, encoding="utf-8")

    # Update domain index
    index_file = brain_root / "index" / f"{dossier.domain}.json"
    if index_file.exists():
        try:
            idx_data = json.loads(index_file.read_text(encoding="utf-8"))
        except Exception:
            idx_data = {"domain": dossier.domain, "name": dossier.domain, "records": []}
    else:
        idx_data = {"domain": dossier.domain, "name": dossier.domain, "records": []}

    idx_data.setdefault("records", []).append({
        "id": card_id,
        "fingerprint": fingerprint,
        "topic": dossier.title,
        "project": dossier.project_source,
        "tags": dossier.tags,
        "summary": dossier.summary,
        "path": f"dossiers/{dossier.domain}/{file_path.name}",
    })

    index_file.write_text(json.dumps(idx_data, ensure_ascii=False, indent=2), encoding="utf-8")

    # Re-compile master index
    compile_master_index(brain_root)

    return file_path


def compile_master_index(brain_root: Path) -> dict[str, Any]:
    """Compiles the master index across all 4 domains."""
    index_dir = brain_root / "index"
    master_path = index_dir / "MASTER_INDEX.json"
    total_records = 0
    domain_counts: dict[str, int] = {}

    for p in index_dir.glob("*.json"):
        if p.name == "MASTER_INDEX.json":
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            count = len(data.get("records", []))
            domain_counts[data.get("domain", p.stem)] = count
            total_records += count
        except Exception:
            pass

    master_data = {
        "system": "Hua Brain Master Index",
        "last_compacted": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_active_records": total_records,
        "domains": domain_counts,
    }
    master_path.write_text(json.dumps(master_data, ensure_ascii=False, indent=2), encoding="utf-8")
    return master_data


def commit_and_push_brain(brain_root: Path, project_name: str) -> None:
    """Silently commits hua-brain changes and triggers non-blocking background push."""
    if not (brain_root / ".git").exists():
        return
    try:
        status_res = subprocess.run(
            ["git", "-C", str(brain_root), "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        if not status_res.stdout.strip():
            return

        subprocess.run(
            ["git", "-C", str(brain_root), "add", "-A"],
            capture_output=True,
            timeout=3,
        )
        msg = f"feat(ambient): autorunne dream auto-distill from {project_name} [skip ci]"
        subprocess.run(
            ["git", "-C", str(brain_root), "commit", "-m", msg],
            capture_output=True,
            timeout=5,
        )

        # Non-blocking background push to GitHub
        subprocess.Popen(
            ["git", "-C", str(brain_root), "push", "origin", "main"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass


def sync_signals_to_hua_brain(
    repo_root: Path,
    signals: list[dict[str, Any]],
    use_vertex: bool = True,
) -> dict[str, Any]:
    """
    Core Entrypoint: Automatically harvested signals from autorunne are synced
    directly into hua-brain with zero human typing required.
    """
    brain_root = resolve_hua_brain(repo_root)
    if not brain_root:
        return {"synced": False, "reason": "hua_brain_not_found"}

    project_name = repo_root.name

    # Expand signals with ambient multi-agent collectors
    all_signals = list(signals)
    all_signals.extend(harvest_recent_git_signals(repo_root))
    all_signals.extend(harvest_claude_history(project_name))
    all_signals.extend(harvest_antigravity_history())
    all_signals.extend(harvest_grok_history())

    saved_dossiers: list[str] = []

    for sig in all_signals:
        summary = sig.get("summary", "").strip()
        if not summary or len(summary) < 8:
            continue

        domain = sig.get("topic") or classify_domain(summary)
        fingerprint = compute_signal_fingerprint(summary)

        if is_already_recorded(brain_root, domain, fingerprint, summary):
            continue

        # High-grade distillation
        dossier = distill_signal_with_argon(sig, project_name, use_vertex=use_vertex)
        saved_path = persist_dossier_to_brain(brain_root, dossier, fingerprint)
        saved_dossiers.append(str(saved_path.name))

    if saved_dossiers:
        commit_and_push_brain(brain_root, project_name)

    return {
        "synced": True,
        "brain_root": str(brain_root),
        "dossiers_created": saved_dossiers,
        "signals_processed": len(all_signals),
    }
