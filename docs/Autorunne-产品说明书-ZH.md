# Autorunne 产品说明书

## 1. 产品定义

Autorunne 是一个本地优先的 AI 开发工作流层。它把任意 Git 仓库整理成一个可恢复、可交接、可被多个 coding agent 共同使用的开发工作区。

一句话说：

> Hermes、Codex、Claude Code、Cursor、Copilot 负责干活；Autorunne 负责让项目不断档。

## 2. 用户真正遇到的问题

现在很多人已经会用 AI 写代码，但项目做久了会遇到更实际的问题：

- 过一天再打开，忘了上次做到哪里
- 一个模型做过的事，另一个模型不知道
- 新窗口需要重新解释项目背景
- 任务完成后没有验证记录
- 下一步只在聊天里说过，仓库里没有留下来
- 客户项目和课程项目需要交接，但资料散在各处

Autorunne 的价值不是“让 AI 多写一段代码”，而是让项目能够持续推进。

## 3. 核心功能

### repo-local 项目记忆

Autorunne 在仓库内维护 `.autorunne/`：

```text
.autorunne/
├── state/   # 机器可读状态
├── views/   # 人和 agent 都能读的 Markdown
└── bin/     # 可选 wrapper
```

主要记录：项目背景、任务、决策、命令、会话、验证结果、下一步。

### 多 agent 共享同一套入口

支持 Codex、Claude Code、Hermes、Cursor、GitHub Copilot、Gemini 等入口。不同工具不需要各自保存一套上下文，进入项目后都先读 `.autorunne/views/START_HERE.md`。

### 任务闭环

支持清晰的开发节奏：

```text
open / sync → ingest / start → checkpoint → finish / validate
```

这套节奏让任务不是“聊完就散”，而是能留下项目记录。

### 项目扫描和命令派生

Autorunne 会识别常见项目结构，并生成推荐命令：

- Node / TypeScript / 前端项目
- frontend/backend/contracts 多包项目
- Python / FastAPI / Django / Flask / Streamlit
- 轻量 Python 教学 demo，如 `app.py` + `tests/`
- Go、Rust、C、C++、CMake

### 状态可读

0.6.20 起，`autorunne status` 和 `.autorunne/views/STATUS.md` 会给出更适合人看的项目状态：当前是否可继续、上次验证怎样、下一步是什么。

## 4. 典型用户

- 独立开发者：多个 AI 工具配合做项目
- AI 编程课程讲师：让学员学会持续推进项目
- 外包和顾问服务：把每轮开发、验证、交接记录清楚
- 小团队：不想引入重型平台，但需要项目记忆
- 开源维护者：让贡献者更快理解项目当前状态

## 5. 使用方式

安装：

```bash
pipx install autorunne
```

接入项目：

```bash
cd your-project
autorunne open --with-vscode
```

日常任务：

```bash
autorunne ingest --source codex --task "修复订单筛选" --next "先补测试"
# agent 开发并运行验证
autorunne finish --summary "订单筛选修复完成" --validate "pytest -q" --next "整理发布说明"
```

## 当前版本定位：0.6.22

## 6. 当前版本定位

当前公开版本：**0.6.22**。

这个版本已经适合：

- 公开 GitHub 展示
- AI 编程课程演示
- 个人真实项目使用
- 顾问交付流程验证
- 早期客户试用

它还不是最终企业版平台。更准确的定位是：可持续使用的 Beta 工作流层。

## 7. 边界

现在不承诺：

- 自动替代完整研发管理
- 覆盖所有语言和所有复杂 monorepo
- 不经人工验证就自动发布业务系统
- 自动理解所有团队内部流程

Autorunne 的产品路线会保持轻量：先把 repo-local 记忆、交接、验证、收尾做好，再逐步补团队协作、可视化和商业版能力。

## 8. 产品结论

Autorunne 最适合成为 AI 时代的软件项目“持续开发操作层”。它不替代模型，而是让不同模型、不同会话、不同人能围绕同一个仓库连续工作。

## 商业稳定性结论

0.6.22 是可商用验证的 Beta 工作流层，适合教学 + 交付 + 顾问服务里的早期验证。
