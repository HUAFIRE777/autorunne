# Autorunne 使用说明（中文版）

## 1. 工具定位

Autorunne 用来给 Git 项目加一层本地 AI 开发工作流。它不替代 Codex、Claude Code、Hermes、Cursor 或 Copilot，而是让这些工具共享同一份项目状态。

适合：

- 新项目
- 半成品项目
- 从 GitHub 拉下来的开源项目
- AI 编程课程 demo
- 客户交付项目
- 多个 coding agent 接力开发的项目

## 2. 安装

```bash
pipx install autorunne
```

或：

```bash
curl -fsSL https://raw.githubusercontent.com/HUAFIRE777/autorunne/main/scripts/install.sh | bash
```

检查：

```bash
autorunne --version
```

## 3. 接入项目

```bash
cd your-project
autorunne open --with-vscode
```

生成后重点看：

```text
.autorunne/views/START_HERE.md
.autorunne/views/STATUS.md
.autorunne/views/COMMANDS.md
.autorunne/views/TASKS.md
.autorunne/views/NEXT_ACTION.md
```

## 4. 推荐工作流

```text
open / sync → ingest / start → checkpoint → finish / validate
```

示例：

```bash
autorunne open
autorunne ingest --source claude --task "补齐支付回调" --next "先写 webhook 测试"
# Claude Code / Codex / Hermes 做实现
pytest -q
autorunne finish --summary "支付回调完成" --validate "pytest -q" --next "整理发布说明"
```

## 5. 常用命令

### 恢复项目

```bash
autorunne open
autorunne sync
```

### 写入 agent 任务

```bash
autorunne ingest --source codex --task "继续订单筛选" --next "先补测试"
```

### 开始任务

```bash
autorunne start --task "继续订单筛选" --next "先补测试"
```

### 中途记录

```bash
autorunne checkpoint --summary "已完成筛选参数解析" --next "接数据库查询"
```

### 完成任务

```bash
autorunne finish --summary "订单筛选完成" --validate "python -m pytest -q" --next "补接口文档"
```

### 查看状态

```bash
autorunne status
autorunne doctor
```

## 6. 多 agent 使用方式

每个 agent 进入仓库后都先读：

```text
.autorunne/views/START_HERE.md
```

如果工具支持 repo skill 或指令文件，Autorunne 会尽量生成：

```text
AGENTS.md
.agents/skills/autorunne-workflow/SKILL.md
.claude/skills/autorunne-workflow/SKILL.md
.cursor/rules/autorunne-workflow.mdc
.github/copilot-instructions.md
```

用户不需要每次都说“先读 Autorunne”。入口文件应该替用户说明这件事。

## 7. 项目识别

Autorunne 会尽量从项目文件里推断技术栈和命令。

支持常见：

- React / Next.js / Vite / Vue / Nuxt / Svelte
- Node / Express / NestJS
- frontend/backend/contracts/apps/packages 多包项目
- Python / FastAPI / Django / Flask / Streamlit
- 轻量 Python demo：`app.py`、`main.py`、`tests/`
- Go / Rust / C / C++ / CMake

比如轻量 Python 项目可能生成：

```bash
python app.py
python -m pytest -q
```

多包项目可能生成：

```text
frontend:build -> cd frontend && npm run build
backend:test -> cd backend && npm test
contracts:test -> cd contracts && npm test
```

## 8. GitHub 开源项目建议

如果你准备公开仓库，建议提交对协作者有帮助的说明文件，例如 `AGENTS.md`、Copilot 指令、repo skill、部分 `.autorunne/views/*.md`。

不建议随手提交 runtime、完整事件日志、私密客户信息或本地路径。

公开前至少检查：

```bash
git status --short
autorunne doctor
autorunne status
```

## 9. 当前版本

0.6.16 是可公开演示、可教学、可早期交付验证的 Beta 版本。它已经跑通 GitHub Release、PyPI、真实项目 smoke test 和多 agent 入口说明。

## 10. 一句话总结

Autorunne 让 Git 仓库自己带着项目记忆走。coding agent 负责执行，Autorunne 负责让项目接得上。

## 11. 0.6.13 多包项目补充

0.6.13 修复了根目录没有 `package.json` 时的误判问题。下面这种项目现在应该被识别为多包项目：

```text
frontend/package.json
backend/package.json
contracts/package.json
```

常见派生命令：

```bash
cd frontend && npm run build
cd backend && npm test
cd contracts && npm run compile
```

发布包示例仍然保留：`autorunne-0.6.16-py3-none-any.whl`。发布整理命令：

```bash
autorunne release --version 0.6.16
```

## 12. 0.6.14 轻量 Python 项目补充

0.6.14 开始，只有 `app.py`、`tests/`、README 的教学 demo，也能生成实用命令：

```bash
python app.py
python -m pytest -q
```

同时，repo 入口会提示 agent 自动读取 Autorunne workflow，不需要用户每次提醒。

