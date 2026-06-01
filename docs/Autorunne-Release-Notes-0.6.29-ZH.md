# Autorunne 0.6.29 发布说明

0.6.29 的主题是：**长期项目记忆管理**。

前几个版本已经把 handoff、doctor、repair、status 的核心交接稳定性打稳；这一版解决另一个长期使用问题：项目反复迭代一年以后，`.autorunne/` 还能不能继续干净、可读、可交接。

## 核心变化

### 1. `autorunne compact`

新增长期记忆压缩命令：

```bash
autorunne compact
```

默认保留最近 200 条详细 session/event 记录，把更早历史整理到：

```text
.autorunne/archive/YYYY-MM.md
```

这不是把历史直接删掉，而是把老过程压缩成更适合长期阅读的阶段摘要。

### 2. 安全预览：`--dry-run`

```bash
autorunne compact --dry-run
```

先显示会归档多少 sessions/events、会写哪些 archive 文件、会保留多少近期记录，不直接修改状态。

### 3. `autorunne memory-report`

新增项目记忆体检：

```bash
autorunne memory-report
```

它会显示：

- `.autorunne` 总大小
- sessions / events 数量
- 最大的几个状态文件
- 是否建议运行 compact

### 4. `autorunne export-session`

新增会话导出：

```bash
autorunne export-session --last 20
autorunne export-session --since 2026-06-01
```

导出结果放在：

```text
.autorunne/exports/session-*.md
```

适合用于客户交付、课程复盘、团队同步、GitHub 更新说明。

### 5. `.autorunne/SUMMARY.md`

compact 会生成一个长期摘要文件：

```text
.autorunne/SUMMARY.md
```

它记录当前状态、最近完成、下一步、关键决策和长期记忆策略。

## 为什么默认保留 200 条？

30～50 条对真实项目偏少。一个正常任务可能包含 open、ingest、checkpoint、finish、sync、doctor 等多条记录。

0.6.29 默认保留 200 条近期详细记录，是为了让 agent 能追溯最近 20～40 个小任务的上下文；更早的记录则归档成月度摘要，避免主 handoff 入口被旧日志淹没。

## 产品定位

0.6.29 之后，Autorunne 更接近这个定位：

> 代码是产品本体，README 是给人看的说明，tests 是质量保障，`.autorunne/` 是给 AI 和后续开发者看的项目记忆层。

项目从创建、开发、上线到后期维护，Autorunne 可以一直跟着项目存在，但它保存的是“下一位 agent 继续开发所需的信息”，不是完整聊天记录垃圾堆。

## 更新

```bash
pipx upgrade autorunne --pip-args="--no-cache-dir -i https://pypi.org/simple"
```

检查版本：

```bash
autorunne --version
```

PyPI：`autorunne==0.6.29`

GitHub Release：`v0.6.29`
