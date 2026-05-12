# Autorunne 0.6.22 发布说明

0.6.22 是一个小的稳定性和日志洁净度版本，来自 0.6.21 在真实 HaoPay/Codex 小切片通过后的继续打磨。

## 改进了什么

0.6.21 已经修好核心状态问题：任务完成后不会再被错误保留为 Next product task。

0.6.22 继续处理一个不影响状态判断、但会影响交接阅读体验的小瑕疵：

- 多次 `autorunne open` 触发的 `workspace open auto-resume` 不再因为中间夹着 integration refresh/noise 记录而重复增长。
- 对相同的 workspace auto-resume 记录，Autorunne 会更新时间，而不是追加多条几乎一样的 SESSION_LOG。
- 遇到真正的开发进展记录，例如 `start task`、`checkpoint`、`finish summary` 后，仍会保留后续新的 resume 记录，避免把不同开发阶段混在一起。

## 为什么这个版本有用

真实使用时，agent / 编辑器 / wrapper 可能会在很短时间内多次打开同一个仓库。以前即使状态是对的，`SESSION_LOG.md` 里也可能出现同一时间附近重复的 `workspace open auto-resume`。

0.6.22 的目标很简单：

> 状态继续安全，日志更干净，下一轮 AI 或人打开项目时更容易读。

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
AutoRunne 0.6.22
```

## 验证

- 新增非连续 `workspace open auto-resume` 去重回归测试
- 覆盖中间夹着 integration refresh 的真实 handoff 场景
- `python -m pytest -q`
- `python -m build`
- `python -m twine check dist/*`
- 发布后会继续用真实课程项目 smoke test 验证本机运行环境

## 发布状态

- GitHub Release：`v0.6.22`
- PyPI：`autorunne==0.6.22`
