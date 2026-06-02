# Autorunne 0.6.31 发布说明

0.6.31 的主题是：**summary 自动生成，不再让用户写流程说明**。

这版修的是一次真实课程仓库 dogfood 暴露的问题：新版 `checkpoint` 要求 summary，虽然能让记录更清楚，但如果 agent / wrapper 没自动填写，就会打断“用户只派任务”的自动化体验。

## 解决的问题

用户不应该负责写：

```bash
autorunne checkpoint --summary "..."
```

这句话应该由 agent 或 Autorunne 自己完成。

0.6.31 之后，下面的旧式调用也可以继续工作：

```bash
autorunne checkpoint
autorunne finish --next "继续下一个切片"
```

如果没有传 `--summary`，Autorunne 会根据当前任务和改动文件自动生成说明。

## 更新内容

- `autorunne checkpoint` 支持省略 `--summary`。
- `autorunne finish` 支持省略 `--summary`。
- 有明确 `--summary` 时仍然优先使用用户/agent 给出的说明。
- 没有 `--summary` 时，自动从 changed files、active task、next action 生成本地 summary。
- 生成的 agent handoff 文案会提醒 agent 自主记录，不要让用户写 workflow summary。
- 继续兼容 0.6.30 的自动长期记忆压缩。

## 推荐使用方式

用户仍然只需要直接给任务：

> 帮我给课程仓库加一个 smoke 检查。

agent 内部可以直接收口：

```bash
autorunne checkpoint --no-validate
autorunne finish --validate "python3 scripts/course_repo_smoke.py" --next "继续选择下一个课程交付切片"
```

不需要问用户：“summary 应该写什么？”

## 兼容性

- 新写法：`autorunne checkpoint --summary "已完成初步修改"` 继续可用。
- 旧写法：`autorunne checkpoint` 现在也可用。
- `finish --summary ...` 继续可用。
- `finish` 省略 summary 时会自动生成完成总结。

## PyPI / GitHub

PyPI：`autorunne==0.6.31`

GitHub Release：`v0.6.31`
