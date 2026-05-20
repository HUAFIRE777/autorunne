# Autorunne 0.6.25 发布说明

0.6.25 是一个“小而稳”的交接洁净度补丁。

0.6.24 已经把新项目上手变简单：新目录直接 `autorunne open`，不需要先手动 `git init`。0.6.25 不改这条稳定入口，只继续打磨下一轮 AI/agent 接手项目时看到的状态。

## 这版解决什么

真实项目连续几轮交接后，状态里容易出现两类小误导：

1. 已经完成的任务，还残留在 `Next product task` 里。
2. “当前公开基线 / 发布后跟进 / 验证状态”这类流程备注，被误当成产品下一步。

这会让下一个 agent 打开项目时误以为还要继续做已经完成的事。

## 主要变化

- 渲染交接视图前，会自动清理 `next_product_task` 里的已完成任务残留。
- 如果下一步其实是流程/发布/验证类备注，会放到 `Workflow follow-up`，不再混到产品任务里。
- 如果还有真正的 pending 产品任务，会自动回退到那个任务作为 `Next product task`。
- `autorunne status` 里的 Git 跟踪提示更清楚：现在显示 `Autorunne state tracked by git`，并明确 `no (local-only handoff state)`。

## 没有改变什么

- 不改变 0.6.24 的自动 `git init` 行为。
- 不改变正常的 `autorunne open` / `init` / `adopt` / `ingest` 使用方式。
- 不默认把 `.autorunne/` 加入 Git 跟踪。
- 不重做任务系统结构，只在状态/渲染层做安全清理。

## 对用户的实际意义

更简单说：

> 下一轮 AI 打开项目时，看到的“下一步”更像真正要做的事，而不是旧任务残留或发布流程备注。

这版适合已经在真实项目里用 Autorunne 做持续交接的人升级。

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

PyPI：`autorunne==0.6.25`

GitHub Release：`v0.6.25`
