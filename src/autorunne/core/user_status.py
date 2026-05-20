from __future__ import annotations

from typing import Any

WORKFLOW_FLOW = "open/sync → start/ingest → checkpoint → finish/validate"


def _latest_validation(current: dict[str, Any], sessions: dict[str, Any]) -> dict[str, str]:
    structured = current.get("last_validation") or {}
    if structured:
        raw_status = str(structured.get("status") or "").strip().lower()
        status = "通过" if raw_status == "passed" else "失败" if raw_status == "failed" else raw_status or "未记录"
        return {
            "status": status,
            "command": str(structured.get("command") or "未记录"),
            "time": str(structured.get("timestamp") or "未记录"),
            "output": str(structured.get("output_summary") or "未记录"),
        }
    for session in reversed(sessions.get("items", [])):
        command = "未记录"
        status = "未记录"
        output = "未记录"
        for line in session.get("lines", []):
            if line.startswith("Validation command:"):
                command = line.split(":", 1)[1].strip() or "未记录"
            if line.startswith("Validation result:"):
                raw = line.split(":", 1)[1].strip().lower()
                if raw == "passed":
                    status = "通过"
                elif raw == "failed":
                    status = "失败"
                else:
                    status = raw or "未记录"
            if line.startswith("Validation output:") or line.startswith("validation_output:"):
                output = line.split(":", 1)[1].strip() or "未记录"
        if command != "未记录" or status != "未记录":
            return {
                "status": status,
                "command": command,
                "time": session.get("timestamp") or "未记录",
                "output": output,
            }
    return {"status": "未记录", "command": "未记录", "time": "未记录", "output": "未记录"}


def build_user_summary(state: dict[str, Any], *, missing: list[str] | None = None) -> dict[str, str]:
    """Return a plain-language status snapshot for non-technical users."""
    current = state.get("current", {})
    sessions = state.get("sessions", {})
    active_task = (current.get("active_task") or "").strip()
    last_action = (current.get("last_action") or "").strip()
    missing_files = [item for item in (missing or []) if item]

    if missing_files:
        project_state = "需要补齐上下文入口"
    elif active_task:
        project_state = "正在开发中"
    elif last_action == "task_finished":
        project_state = "可继续开发"
    else:
        project_state = "已准备，可开始任务"

    context_entry = "已准备好" if not missing_files else f"缺少 {len(missing_files)} 个入口文件"
    validation = _latest_validation(current, sessions)
    validation_status = validation["status"]
    next_action = current.get("next_action") or "确认下一个具体任务"
    if current.get("next_product_task"):
        next_product_task = current["next_product_task"]
    elif "next_product_task" in current:
        next_product_task = "无"
    else:
        next_product_task = next_action
    workflow_follow_up = current.get("workflow_follow_up") or "无"

    return {
        "project_state": project_state,
        "validation_status": validation_status,
        "validation_command": validation["command"],
        "validation_time": validation["time"],
        "validation_output": validation.get("output", "未记录"),
        "next_action": next_action,
        "next_product_task": next_product_task,
        "workflow_follow_up": workflow_follow_up,
        "context_entry": context_entry,
        "workflow_flow": WORKFLOW_FLOW,
        "one_line": f"当前项目状态：{project_state}；上次验证：{validation_status}；验证命令：{validation['command']}；下一步产品任务：{next_product_task}；流程跟进：{workflow_follow_up}；上下文入口：{context_entry}",
    }
