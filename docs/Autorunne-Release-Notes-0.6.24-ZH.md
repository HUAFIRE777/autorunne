# Autorunne 0.6.24 发布说明

发布日期：2026-05-12

0.6.24 是一个新手上手体验补丁：**新项目不再需要用户先手动运行 `git init`**。

## 这版解决什么

以前新项目第一次使用时，用户需要先：

```bash
git init
autorunne open
```

这对开发者来说合理，但对课程学员、非程序员或第一次试用的人来说，多一步就容易卡住。

从 0.6.24 开始，直接运行：

```bash
autorunne open
```

如果当前目录还不是 Git 仓库，Autorunne 会自动执行本地 `git init`，然后继续创建 `.autorunne/` 工作区和 agent 入口文件。

## 影响范围

自动初始化适用于常见首次入口：

- `autorunne open`
- `autorunne init`
- `autorunne adopt`
- `autorunne ingest`
- `autorunne hermes-task`

已有 Git 仓库不受影响，仍然使用原来的 repo root。

## 用户能看到什么

在全新普通文件夹中运行：

```bash
autorunne open
```

会看到类似：

```text
Git repository initialized automatically (no manual `git init` needed).
Autorunne bootstrapped: /path/to/project
```

也就是说，新用户不用理解 Git 初始化这一步，先把项目打开即可。

## 仍然保留的原则

Autorunne 仍然是 repo-local 项目记忆层，内部仍依赖 Git 来判断项目根目录、变更和交接状态。

区别只是：

- 0.6.23：忘记 `git init` 时提醒用户去做。
- 0.6.24：Autorunne 直接帮用户做。

## 验证

本版增加了 CLI 回归测试：

- 新目录运行 `autorunne open` 会自动创建 `.git/` 和 `.autorunne/`。
- 新目录运行 `autorunne ingest --task ...` 也会自动初始化 Git 并记录任务。
- 输出不再出现 traceback。

PyPI：`autorunne==0.6.24`

GitHub Release：`v0.6.24`
