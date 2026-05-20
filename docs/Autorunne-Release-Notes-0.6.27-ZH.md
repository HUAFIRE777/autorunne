# Autorunne 0.6.27 发布说明

0.6.27 是在 0.6.26 真实交接一致性修复上的继续加固。

这版重点不是新增大功能，而是让多 agent 接手项目时更稳定、更干净。

## 这版解决什么

### 1. doctor 会检查交接一致性

`autorunne doctor` 现在会检查这些入口是不是看到同一个主下一步：

- `current.next_action`
- `current.next_product_task`
- `tasks.next_up[0]`
- `START_HERE.md` 的 Current focus / 下一步
- `NEXT_ACTION.md` legacy / product task
- `STATUS.md` 下一步

不一致时会明确报出字段和值，方便马上定位旧状态漂移。

### 2. 新增 repair-handoff

如果旧 workspace 已经被历史版本写乱，可以运行：

```bash
autorunne repair-handoff
```

它会从最近一次 `task_finished.next_action` 或当前 product task 推导主下一步，然后修复：

- `current.next_action`
- `current.next_product_task`
- `tasks.next_up[0]`
- `START_HERE.md`
- `NEXT_ACTION.md`
- `STATUS.md`

同时会清掉进入主 backlog 的 workflow follow-up 项。

### 3. workflow follow-up 不再进主待办第一项

旧状态里如果有类似 “review START_HERE / STATUS / render” 的流程备注，sync/finish/repair 都不会再把它放到 `tasks.next_up[0]`。

主下一步应该是产品任务，不是流程备注。

### 4. changed_files 更干净

`finish` 现在会把改动分成：

- business：业务文件
- autorunne_state：Autorunne 状态文件
- integration：`.agents`、`.claude`、Cursor rule、Copilot instructions 等集成文件

这样 `.agents/.claude` 旧 version diff 不会混进业务 changed_files。

## 推荐升级

```bash
pipx upgrade autorunne --pip-args="--no-cache-dir -i https://pypi.org/simple"
```

检查版本：

```bash
autorunne --version
```

应显示：

```bash
AutoRunne 0.6.27
```

PyPI：`autorunne==0.6.27`

GitHub Release：`v0.6.27`
