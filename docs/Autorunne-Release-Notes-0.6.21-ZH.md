# Autorunne 0.6.21 发布说明

0.6.21 是一个很小但很关键的交接状态修复版本，来自 HaoPay 仓库里真实 Codex 开发切片。

## 修复了什么

在 0.6.20 中，`autorunne finish --task ... --next ...` 完成一个 active/matched task 后，任务本身已经会进入 completed，验证日志也正常记录。

但如果 `--next` 是类似“Review AutoRunne rendered STATUS and SESSION_LOG”的 workflow follow-up，`current.next_product_task` 有时仍会保留刚刚完成的 task。

0.6.21 修复了这个问题：

- 已完成任务不会继续显示为 Next product task。
- 如果还有 pending/next_up 产品任务，会回退到下一个产品任务。
- 如果没有 pending 产品任务，`next_product_task` 设为 `null`，视图里显示 `无`。
- `workflow_follow_up` 继续保留 `finish --next` 的内容。

## 为什么这个修复有用

它解决的是 AI 项目交接中一个很容易误导下一轮 agent 的问题：

> 上一个任务已经完成了，但状态页还告诉下一轮 AI “下一步继续做这个任务”。

修复后，下一轮 AI 打开 `.autorunne/views/STATUS.md` 或 `NEXT_ACTION.md`，不会再把已完成任务当成产品下一步。

## 更新

```bash
pipx upgrade autorunne --pip-args="--no-cache-dir -i https://pypi.org/simple"
```

检查：

```bash
autorunne --version
```

应显示：

```text
AutoRunne 0.6.21
```

## 验证

- 新增 HaoPay/Codex 风格回归测试
- `python -m pytest -q`
- `python -m build`
- `python -m twine check dist/*`

## 发布状态

- GitHub Release：`v0.6.21`
- PyPI：`autorunne==0.6.21`
