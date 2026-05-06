# Autorunne 0.6.20 发布说明

0.6.20 是一次来自真实 HaoPay / 课程项目升级过程的体验修复版本。重点解决：CLI 已经升级到新版本，但 repo skill、SESSION_LOG 和 STATUS 这些给 agent / 用户看的交接层还显得旧、长、重复、不够直观。

## 这版修了什么

### 1. repo skill front matter 跟随当前 CLI 版本

`.agents/skills/autorunne-workflow/SKILL.md` 和 `.claude/skills/autorunne-workflow/SKILL.md` 的 front matter 现在由当前 Autorunne 包版本生成。

也就是说，升级到 0.6.20 后执行：

```bash
autorunne open --path .
autorunne sync --path .
```

repo skill 里的：

```yaml
version: 0.6.20
```

会随新版模板刷新，避免长期停在旧的 `0.6.17` / `0.6.19`。

### 2. SESSION_LOG 不再铺满完整 build 输出

`autorunne checkpoint --validate ...` 和 `autorunne finish --validate ...` 仍然会记录：

- 验证命令
- 验证状态
- 关键输出摘要

但不会把几十上百行 build/test 输出完整铺进 `SESSION_LOG.md`。完整结构化验证信息仍保留在 state/event payload 中，适合机器追踪；SESSION_LOG 更适合人读。

### 3. workspace open / integration updated 去重

重复执行 `autorunne open` 时，连续相同的 `workspace open auto-resume` 会折叠，不再反复刷屏。

集成文件没有真实变化时，也不会重复写一条 `integration updated`。只有模板实际更新、或者 Codex 沙盒只读导致跳过时，才留下有意义的记录。

### 4. STATUS.md 更直接显示验证证据

`.autorunne/views/STATUS.md` 现在除了显示：

- 上次验证：通过 / 失败
- 验证命令
- 验证时间

还会显示：

- 验证结果摘要

用户不用再翻 SESSION_LOG 才能确认最后一次验证到底跑了什么。

## 为什么发 0.6.20

0.6.19 已经补了 Codex 沙盒只读集成文件的问题，但真实项目升级时又暴露出显示层和交接层的问题：

- CLI 是新版，repo skill 还是旧版本号；
- SESSION_LOG 太长；
- open/resume/integration 记录重复；
- STATUS 对用户有用，但验证细节还不够显眼。

这些都属于 Autorunne 本体应该负责的“交接质量”，所以拆成 0.6.20 发布。

## 安装 / 更新

新安装：

```bash
pipx install autorunne --pip-args="--no-cache-dir -i https://pypi.org/simple"
```

已安装更新：

```bash
pipx upgrade autorunne --pip-args="--no-cache-dir -i https://pypi.org/simple"
```

检查版本：

```bash
autorunne --version
```

应显示：

```text
AutoRunne 0.6.20
```

## 发布状态

- GitHub Release：`v0.6.20`
- PyPI：`autorunne==0.6.20`
- 主要验证：`python -m pytest -q`
