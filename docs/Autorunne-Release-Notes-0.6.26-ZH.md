# Autorunne 0.6.26 发布说明

0.6.26 是一个真实开发复测后补上的交接一致性修复。

这次问题不是“状态完全没写”，而是更隐蔽：上一个 agent 已经完成任务，验证通过，`tasks.json` 也知道下一个产品任务；但 `current.next_action`、`START_HERE.md` 的“下一步 / Current focus”、以及 `autorunne status` 仍然可能显示旧任务或流程备注。

这会直接影响下一个 agent：它打开项目后可能被旧 Lesson 带偏。

## 修复内容

- `finish --next` 后，主下一步统一写入：
  - `current.next_action`
  - `current.next_product_task`
  - `tasks.next_up[0]`
  - `.autorunne/views/NEXT_ACTION.md`
  - `.autorunne/views/START_HERE.md`
  - `autorunne status`
- `workflow_follow_up` 只保留流程备注，不再覆盖主下一步。
- `current.json` 新增结构化 `last_validation`：记录验证命令、状态、时间和输出摘要。
- `autorunne open` 不再静默刷新已有 repo-local integration 文件版本，避免 `.agents/skills/...`、`.claude/skills/...` 等文件污染业务 diff。
- 如果确实要同步 integration 文件，继续显式运行：

```bash
autorunne integrate --tool all --scope repo
```

## 为什么有用

这版解决的是 AI 开发里很真实的“交接错位”问题：

- 上一个 agent 做完了，但下一个 agent 读到的下一步还是旧任务；
- JSON 状态和 Markdown 视图不一致；
- 状态文件正确，但 `autorunne status` 展示旧信息；
- 只是恢复项目，却顺手改了 integration 文件，导致业务 diff 变脏。

0.6.26 让“主下一步”只有一个来源，各入口显示一致。这样下一轮 AI 接手时更可靠。

## 更新

```bash
pipx upgrade autorunne --pip-args="--no-cache-dir -i https://pypi.org/simple"
```

新安装：

```bash
pipx install autorunne --pip-args="--no-cache-dir -i https://pypi.org/simple"
```

检查版本：

```bash
autorunne --version
```

PyPI：`autorunne==0.6.26`

GitHub Release：`v0.6.26`
