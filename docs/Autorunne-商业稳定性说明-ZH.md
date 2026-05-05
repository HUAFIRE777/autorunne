# Autorunne 商业稳定性说明（0.6.19）

## 结论

Autorunne 0.6.19 可以对外开源展示，也可以用于教学、顾问交付流程和早期客户验证。

更准确的说法是：

> 它是一个可商用验证的 Beta 工作流层，已经能在真实项目里跑通“接入、开发、验证、收尾”。

## 已经验证的部分

- GitHub Release：`v0.6.19`
- PyPI：`autorunne==0.6.19`
- 安装方式：`pipx install autorunne`
- 服务器运行环境已确认可用
- 真实课程开发项目已跑通 `open → sync → start/ingest → test → finish`
- Codex、Claude、Hermes、Cursor、Copilot 的 repo 入口说明已打通
- `.autorunne/views/STATUS.md` 可以给用户看当前项目是否可继续

## 现在可以对外承诺什么

可以承诺：

1. **本地项目记忆**  
   项目上下文、任务、决策、命令、会话、下一步可以留在 `.autorunne/`。

2. **多 agent 接力**  
   Codex、Claude Code、Hermes、Cursor、Copilot 可以围绕同一套仓库状态工作。

3. **项目恢复**  
   新窗口、新会话、新模型进入项目后，可以先读 `START_HERE.md` 恢复上下文。

4. **安装链路清楚**  
   主路径是 PyPI / pipx，GitHub Release 是可验证的发布记录。

5. **常见项目可演示**  
   轻量 Python demo、多包 Node/TypeScript、常见 Web 项目都已经具备可展示路径。

## 暂时不要过度承诺什么

不要说：

- 已经是完整企业级研发平台
- 可以完全替代项目经理或开发者
- 所有语言、所有 monorepo、所有 CI/CD 场景都深度覆盖
- 不需要人工验证就能自动发布业务系统

更稳的说法是：

> Autorunne 让 AI 开发项目更容易接续、交接和收尾；它不是替代研发流程，而是补上 AI 编程最容易断档的那一层。

## 推荐成交场景

### AI 编程课程

作为课程里的项目持续推进工具，让学员看到：AI 编程不是只问一次，而是每轮都能留下任务、验证和下一步。

### 小型交付项目

用于客户项目内部推进。每次做了什么、怎么验证、下一步是什么，都能留下记录。

### 顾问服务

作为客户 AI coding workflow 的标准件：安装一次，每个 repo 接入一次，后面直接用 Codex / Claude / Hermes / Cursor / Copilot 分配任务。

## 对外一句话

Autorunne 0.6.19 已适合公开开源展示和早期商业验证：用户只管给 agent 分配任务，Autorunne 在仓库里保存项目记忆、任务状态、验证结果和下一步。

## 商业稳定性说明补充

对外保持克制：可商用验证的 Beta 工作流层，不夸成最终企业平台。
