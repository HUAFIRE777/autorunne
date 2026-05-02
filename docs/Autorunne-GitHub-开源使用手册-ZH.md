# Autorunne GitHub 开源使用手册

这份手册给第一次从 GitHub 看到 Autorunne 的用户。目标只有一个：让你尽快判断“这个工具是不是我需要的”，然后能装上、接入一个项目、跑通一次完整流程。

## 1. Autorunne 是做什么的

Autorunne 给 Git 仓库加一层本地项目记忆。

你继续使用 Codex、Claude Code、Hermes、Cursor、Copilot 等工具写代码。Autorunne 不抢它们的活，只负责把项目状态留在仓库里：

- 当前项目是什么
- 正在做什么任务
- 做过哪些决定
- 推荐跑什么命令
- 上次验证是否通过
- 下一步该做什么

这样新开一个 agent 窗口时，不用从头解释项目。

## 2. 最快安装

推荐方式：

```bash
pipx install autorunne
```

如果没有 `pipx`，先装：

```bash
python -m pip install --user pipx
python -m pipx ensurepath
```

也可以用一键脚本：

```bash
curl -fsSL https://raw.githubusercontent.com/keguihua/autorunne/main/scripts/install.sh | bash
```

查看是否安装成功：

```bash
autorunne --version
```

## 3. 给一个项目接入 Autorunne

进入任意 Git 仓库：

```bash
cd your-project
autorunne open --with-vscode
```

它会做几件事：

- 创建或恢复 `.autorunne/`
- 扫描项目技术栈
- 生成 `.autorunne/views/START_HERE.md`
- 生成 `COMMANDS.md`、`TASKS.md`、`STATUS.md` 等项目状态文件
- 生成给 Codex / Claude / Hermes / Cursor / Copilot 使用的 repo 入口说明

以后你再次打开这个仓库时，先运行：

```bash
autorunne open
```

如果你用了 `--with-vscode`，VS Code 可以在打开文件夹时自动触发。

## 4. 日常工作方式

最省事的流程是：

1. 打开项目
2. 启动你常用的 coding agent
3. 让它先读 `.autorunne/views/START_HERE.md`
4. 直接分配任务
5. 完成后运行验证命令
6. 用 `autorunne finish` 收尾

示例：

```bash
autorunne ingest --source codex --task "修复登录过期后跳转问题" --next "先补一个回归测试"
# 让 Codex / Claude Code 做实现
python -m pytest -q
autorunne finish --summary "修复登录过期跳转" --validate "python -m pytest -q" --next "继续整理订单页筛选"
```

## 5. 你应该把哪些文件提交到 GitHub

这取决于项目用途。

### 开源项目推荐提交

可以提交这些对协作者有帮助的文件：

```text
AGENTS.md
.github/copilot-instructions.md
.agents/skills/autorunne-workflow/SKILL.md
.claude/skills/autorunne-workflow/SKILL.md
.cursor/rules/autorunne-workflow.mdc
.autorunne/config.json
.autorunne/views/START_HERE.md
.autorunne/views/PROJECT_CONTEXT.md
.autorunne/views/COMMANDS.md
.autorunne/views/STATUS.md
```

这些文件能让后来的人知道怎么接手项目。

### 不建议提交

一般不建议把这些运行时文件直接公开：

```text
.autorunne/runtime/
.autorunne/state/events.jsonl
.autorunne/snapshots/
```

如果项目里有客户信息、私有路径、未公开业务计划，提交前一定先检查。

## 6. 常见命令

```bash
# 接管 / 恢复项目
autorunne open

# 刷新项目状态
autorunne sync

# 写入一个来自 agent 的任务
autorunne ingest --source claude --task "补齐支付回调" --next "先写测试"

# 开始任务
autorunne start --task "补齐支付回调" --next "先写测试"

# 中途记录进展
autorunne checkpoint --summary "已完成 payload 校验" --next "接入数据库写入"

# 完成并验证
autorunne finish --summary "支付回调完成" --validate "pytest -q" --next "补发布说明"

# 查看项目现在是否可继续
autorunne status

# 检查 repo 集成是否完整
autorunne doctor
```

## 7. 适合公开展示的 demo 流程

如果你要在 GitHub README、课程或视频里演示，建议用这个流程：

```bash
git clone https://github.com/keguihua/autorunne.git
cd autorunne
pipx install autorunne

autorunne open --with-vscode
autorunne status
```

然后打开 `.autorunne/views/STATUS.md`，展示它如何告诉用户：项目现在处于什么状态、上次验证怎样、下一步是什么。

## 8. 常见问题

### Q：我是不是每次都要先开 Autorunne？

不用。Autorunne 是仓库工作流底座。你平时还是直接打开 Codex、Claude Code、Hermes、Cursor 或 Copilot。只要这些工具先读 `.autorunne/views/START_HERE.md`，就能接上项目状态。

### Q：它会不会把我的项目上传到云端？

不会。Autorunne 是本地优先工具，状态文件在当前 Git 仓库里。是否提交到远程 GitHub，由你自己决定。

### Q：它和 Cursor / Copilot 冲突吗？

不冲突。Cursor / Copilot 是入口和执行工具，Autorunne 是仓库里的项目记忆层。

### Q：现在能不能商用？

0.6.16 适合公开演示、课程教学、顾问交付流程和早期商业验证。它还不是完整企业平台，但已经能在真实项目里跑通“接入、开发、验证、收尾”的流程。
