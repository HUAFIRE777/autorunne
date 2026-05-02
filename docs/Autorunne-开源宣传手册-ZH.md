# Autorunne 开源宣传手册

## 一句话

Autorunne 让一个 Git 仓库有自己的项目记忆。你换 Codex、Claude Code、Hermes、Cursor 或 Copilot，项目都能接着往下做。

## 为什么需要它

AI 写代码越来越快，但真实项目不是一次问答就结束。

真实开发里经常遇到这些事：

- 今天修到一半，明天忘了从哪里继续
- Claude 做过的上下文，Codex 不知道
- 新开一个窗口，又要重新解释项目
- 任务做完了，验证结果和下一步没有留下来
- 客户项目、课程项目、开源项目混在一起，交接成本很高

Autorunne 把这些信息留在仓库里，让项目自己带着上下文走。

## 它怎么工作

在项目里运行一次：

```bash
autorunne open --with-vscode
```

项目会多出 `.autorunne/`。里面有给人看的 Markdown，也有给工具读取的状态文件。

以后任何 agent 进入这个仓库，都先看：

```text
.autorunne/views/START_HERE.md
```

它就能知道项目背景、任务、命令、最近状态和下一步。

## 最打动用户的点

### 1. 不用再重复解释项目

项目状态在仓库里，不在某一个聊天窗口里。

### 2. 不绑某个模型

今天用 Claude Code，明天用 Codex，后天用 Hermes，都能读同一套项目记忆。

### 3. 收尾更清楚

任务不是“感觉做完了”，而是有完成总结、验证命令和下一步。

### 4. 适合真实交付

课程 demo、客户项目、开源维护、小团队协作，都需要可恢复的项目状态。

## 推荐对外说法

短版：

> Autorunne 是一个 repo-local AI 开发工作流层，让多个 coding agent 能接着同一个项目往下做。

通俗版：

> 你可以把 Autorunne 理解成放在 Git 仓库里的项目交接本。Codex、Claude Code、Hermes、Cursor、Copilot 来干活前，先看这本交接本；做完后，再把结果写回去。

成交版：

> AI 已经能帮你写代码，但真实项目需要连续推进。Autorunne 把任务、决策、命令、验证结果和下一步留在仓库里，让不同 agent、不同会话、不同人都能接着同一个项目继续做。

## 适合用在哪些场景

- AI 编程课程：让学员学会持续推进项目，而不是只会问 prompt
- 独立开发：多个工具接力，不怕上下文断
- 客户交付：每轮开发有记录、有验证、有下一步
- 开源项目维护：新贡献者能更快理解项目状态
- 小团队协作：把项目工作流放回 Git 仓库，而不是散在聊天记录里

## 对外不要这样说

不要说：

- “全自动替代程序员”
- “所有项目都能自动完成”
- “无需测试即可发布”
- “又一个 AI 聊天工具”

更稳的说法是：

> Autorunne 不是替代开发者，而是让开发者和 coding agent 的交接更稳。

## 公开发布文案

### GitHub 简介

Local-first workflow layer for AI coding agents. Keep project context, tasks, decisions, commands, and next actions inside your Git repo.

### 中文简介

Autorunne 是一个本地优先的 AI 开发工作流层，把项目上下文、任务、决策、验证结果和下一步留在 Git 仓库里，让 Codex、Claude Code、Hermes、Cursor、Copilot 能接力开发。

### 社群短文案

我把 Autorunne 开源了。

它不是新的聊天机器人，也不是重型 IDE，而是给 Git 仓库加一层“项目记忆”。

你用 Codex、Claude Code、Hermes、Cursor 或 Copilot 做开发时，最痛的往往不是写不出代码，而是换窗口、换模型、隔天继续时上下文断掉。

Autorunne 会在仓库里维护任务、决策、推荐命令、验证结果和下一步。新的 agent 进来先读 `START_HERE.md`，就能知道项目该怎么继续。

适合独立开发、AI 编程课程、客户交付和开源项目维护。现在 0.6.16 已经可以用 `pipx install autorunne` 安装。

GitHub：<https://github.com/HUAFIRE777/autorunne>

## 版本状态

0.6.16 已完成 GitHub Release、PyPI、服务器运行环境和真实课程 demo 的基础验证。适合公开演示、教学和早期商业验证。
