# Autorunne 0.6.30 发布说明

0.6.30 的主题是：**自动长期记忆压缩**。

0.6.29 已经提供了手动 `compact / memory-report / export-session`。0.6.30 往前走一步：项目长期反复迭代时，Autorunne 会在常用写入流程后自动检查记忆规模，达到阈值后自动归档旧记录。

## 解决什么问题

用户不应该每天盯着 `.autorunne/` 有多少条记录。

真实项目会一直发生：

- open / sync 恢复项目
- ingest / start 记录新任务
- checkpoint 记录中间进展
- finish 记录验证和下一步

时间久了，session/event 会越来越多。0.6.30 的策略是：**平时自动写入；记录太多时自动收纳旧历史。**

## 默认策略

默认配置：

```json
{
  "auto_compact_enabled": true,
  "auto_compact_threshold": 1000,
  "auto_compact_keep_sessions": 200
}
```

含义：

- 默认超过 1000 条 session/event 后触发自动 compact
- 自动 compact 后保留最近 200 条详细记录
- 更早的记录归档到 `.autorunne/archive/YYYY-MM.md`
- 同时生成 / 更新 `.autorunne/SUMMARY.md`
- 旧历史不是删除，而是月度归档成可读 Markdown

## 为什么不是 500 条

500 条也可以，但默认用 1000 条更稳：

- 对重度 AI 开发项目更宽松
- 不会太早改写历史文件
- 仍然能避免长期无限膨胀
- 最近 200 条详细上下文足够让 agent 接上最近 20～40 个小任务

如果项目很小，或者你想更积极整理，可以自己改成 500：

```json
{
  "auto_compact_threshold": 500,
  "auto_compact_keep_sessions": 200
}
```

如果暂时不想自动压缩，也可以关闭：

```json
{
  "auto_compact_enabled": false
}
```

配置文件位置：

```text
.autorunne/config.json
```

## 会在哪些流程自动检查

0.6.30 已接入常用写入路径：

- `autorunne open`
- `autorunne sync`
- `autorunne ingest`
- `autorunne hermes-task`
- `autorunne start`
- `autorunne checkpoint`
- `autorunne finish`

这些命令完成正常写入后，会轻量检查当前 session/event 数量。没超过阈值时不会做任何压缩。

## 手动命令仍然保留

你仍然可以随时查看和手动控制：

```bash
autorunne memory-report
autorunne compact --dry-run
autorunne compact
autorunne export-session --last 20
```

推荐排查顺序：

1. `autorunne memory-report` 看当前大小和数量
2. `autorunne compact --dry-run` 预览会归档什么
3. `autorunne compact` 手动执行

## 一句话总结

0.6.30 之后，Autorunne 更像一个能长期陪伴项目的本地项目记忆层：

- 近期记录详细保留
- 旧历史自动归档
- handoff 入口保持短而清楚
- 项目不用担心 `.autorunne/` 一路无限膨胀

## 安装 / 更新

```bash
pipx upgrade autorunne --pip-args="--no-cache-dir -i https://pypi.org/simple"
```

检查版本：

```bash
autorunne --version
```

PyPI：`autorunne==0.6.30`

GitHub Release：`v0.6.30`
