# Autorunne 0.6.23 发布说明

发布日期：2026-05-12

## 这版解决什么

0.6.23 是一个很小的新手体验补丁：当用户在还没有执行 `git init` 的新项目里运行 Autorunne 时，不再只看到“不是 Git 仓库”或者一大段 traceback，而是直接提醒先初始化 Git。

## 用户会看到什么

如果在非 Git 目录里运行：

```bash
autorunne open
```

现在会提示：

```text
⚠️  autorunne open needs a Git repository first. ⏰ Run `git init` first, then rerun `autorunne open`.
```

也就是：先运行：

```bash
git init
```

然后再运行：

```bash
autorunne open
```

## 为什么要加

Autorunne 的定位是 repo-local 项目记忆层，依赖 Git 仓库来判断项目根目录、变更、任务交接和状态记录。新用户如果忘了先 `git init`，之前的错误提示不够直白。

这版把这个坑补成明确提醒，降低首次使用门槛。

## 验证

- 增加了非 Git 工作区 CLI 回归测试：确认输出包含 `git init`，且不再出现 traceback。
- 继续保留 0.6.22 的稳定状态：完成任务不会误显示为下一步，重复 open 日志保持干净。

PyPI：`autorunne==0.6.23`
GitHub Release：`v0.6.23`
