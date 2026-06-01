# Autorunne 安装与使用操作手册

这份手册给第一次使用 Autorunne 的人。照着做，先跑通一个项目，再慢慢看高级命令。

## 1. 先理解一句话

Autorunne 不是你每天都要打开的聊天窗口。

它是放在 Git 仓库里的工作流底座。你平时还是用 Codex、Claude Code、Hermes、Cursor、Copilot 写代码，Autorunne 负责把项目状态留在仓库里。

## 2. 安装

推荐：

```bash
pipx install autorunne
```

如果想一行脚本安装：

```bash
curl -fsSL https://raw.githubusercontent.com/HUAFIRE777/autorunne/main/scripts/install.sh | bash
```

检查版本：

```bash
autorunne --version
```

当前公开版本是 0.6.30。

## 3. 给一个仓库接入

进入你的项目目录：

```bash
cd your-project
autorunne open --with-vscode
```

这一步通常每个仓库只做一次。它会：

- 创建或恢复 `.autorunne/`
- 扫描项目结构
- 生成给 agent 看的 `START_HERE.md`
- 生成任务、决策、命令、状态等视图
- 配好 VS Code 打开文件夹时的自动接入任务

## 4. 日常怎么用

最简单流程：

1. 打开项目
2. 启动你常用的 agent
3. 让它读 `.autorunne/views/START_HERE.md`
4. 直接分配任务
5. 跑测试或验证命令
6. 用 `autorunne finish` 收尾

示例：

```bash
autorunne ingest --source codex --task "修复登录过期跳转" --next "先补一个回归测试"
python -m pytest -q
autorunne finish --summary "修复登录过期跳转" --validate "python -m pytest -q" --next "继续做订单页筛选"
```

## 5. 如果你用 Codex

先确保仓库接入过：

```bash
autorunne open --with-vscode
```

之后直接在项目终端启动 Codex。让 Codex 先读：

```text
.autorunne/views/START_HERE.md
```

如果你想强制走 Autorunne wrapper：

```bash
./.autorunne/bin/ar-codex
```

## 6. 如果你用 Claude Code

流程一样：

```text
.autorunne/views/START_HERE.md
```

或者：

```bash
./.autorunne/bin/ar-claude
```

## 7. 如果你用 Hermes

Hermes 可以作为远程任务入口。任务进入仓库后，建议记录成：

```bash
autorunne ingest --source hermes --task "继续支付回调" --next "先补 webhook 测试"
```

如果项目里已有 wrapper，也可以用：

```bash
./.autorunne/bin/ar-hermes
```

## 8. 常用命令表

```bash
# 接管或恢复项目
autorunne open

# 刷新扫描结果和视图
autorunne sync

# 查看当前项目状态
autorunne status

# 检查集成是否完整
autorunne doctor

# 记录自然语言任务
autorunne ingest --source codex --task "任务内容" --next "下一步"

# 明确开始任务
autorunne start --task "任务内容" --next "下一步"

# 中途记录进展
autorunne checkpoint --summary "当前进展" --next "下一步"

# 完成任务并验证
autorunne finish --summary "完成了什么" --validate "测试命令" --next "后续动作"
```

## 9. 什么时候用 daemon

如果你想让仓库在一个工作时段里持续监听文件变化，可以运行：

```bash
autorunne daemon --duration 300 --interval 2
```

普通用户不需要一开始就用 daemon。先把 `open → agent 开发 → finish` 跑通更重要。

## 10. 提交 GitHub 前检查

开源项目建议先看：

```bash
git status --short
autorunne doctor
autorunne status
```

确认没有把私密运行时文件、客户信息、token、个人路径提交上去。

## 11. 常见误区

### 每次都要先打开 Autorunne 吗？

不用。Autorunne 是仓库底座，不是聊天入口。你照常打开 agent。

### `.autorunne/` 全部都要提交吗？

不一定。开源项目可以提交人可读的 views 和 agent 入口文件，但 runtime、完整事件日志、私密状态要谨慎。

### 它会替我自动发布项目吗？

不会。它帮助记录和验证开发流程，发布仍然需要你确认。

## 12. 最推荐的新手练习

找一个小项目，跑下面这组命令：

```bash
autorunne open --with-vscode
autorunne status
autorunne ingest --source codex --task "整理 README" --next "先读现有文档"
# 手动或让 agent 修改一点文档
autorunne finish --summary "整理 README" --next "继续补使用示例"
autorunne status
```

你会看到 Autorunne 如何把任务、状态和下一步留在仓库里。

## 13. 升级 AutoRunne

如果已经安装过，推荐先走安全升级路径：

```bash
pipx upgrade autorunne --pip-args="--no-cache-dir -i https://pypi.org/simple"
pipx runpip autorunne show autorunne
autorunne version
autorunne --version
```

如果 pipx 缓存导致版本不对，可以先 `uninstall` 再安装：

```bash
pipx uninstall autorunne
pipx install autorunne --pip-args="--no-cache-dir -i https://pypi.org/simple"
```

最后 fallback 才考虑从 GitHub release wheel 或源码安装。普通用户优先用 PyPI，不要一上来就装 main 分支。

## 14. 多包项目 / Monorepo 支持

从 0.6.13 开始，根目录没有 `package.json` 也没关系。只要子目录里有这些文件，Autorunne 会尽量识别：

```text
frontend/package.json
backend/package.json
contracts/package.json
apps/*/package.json
packages/*/package.json
```

生成的命令会带子目录前缀，例如：

```bash
cd frontend && npm run build
cd backend && npm test
cd contracts && npm run compile
```

也就是说，`sync` 不应该再把项目误判成 generic。发布前可以用：

```bash
autorunne release --version 0.6.22
```

来整理版本材料和发布检查。

