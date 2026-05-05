# Autorunne 0.6.19 发布说明

0.6.19 是一次来自真实 Codex dogfood 的稳定性修复版本。重点解决：用户直接打开 Codex 后，Autorunne 已经被 agent 读到，但在 Codex 沙盒模式下重写隐藏集成文件可能失败，导致后台状态记录被中断。

## 背景

真实课程开发项目验证时发现：

1. Codex 直接启动后会主动读取 `.autorunne/views/START_HERE.md` 和 `.agents/skills/autorunne-workflow/SKILL.md`。
2. Codex 会按说明尝试执行 `autorunne open` / `autorunne ingest`。
3. 但在部分 Codex 沙盒模式下，普通项目文件可以改，隐藏集成文件如 `.agents/skills/autorunne-workflow/SKILL.md` 可能是只读。
4. 旧版本 `autorunne open` 每次都会尝试重写这些集成文件，所以会因为 `Read-only file system` 中断，连后续任务记录也无法继续。

## 改进

0.6.19 让 repo integration 写入更适合 agent 沙盒：

- 如果集成文件已经存在，但当前环境不允许重写，Autorunne 会跳过这个文件。
- `autorunne open` 不会因为已存在的只读集成文件直接失败。
- `autorunne ingest` 这类会间接调用 `open` 的 direct-agent 入口，也能继续把任务写进 `.autorunne/` 状态。
- 新安装或缺失的集成文件仍然会正常生成；只有“已存在但当前沙盒不可重写”的文件会被安全跳过。

## 对用户的意义

这让产品体验更接近目标状态：

```text
已接入 Autorunne 的项目 → 直接打开 Codex / Claude / Hermes / Cursor → 给任务 → Autorunne 在后台记录状态
```

用户不需要先运行 wrapper，也不需要先手动操作 Autorunne。Autorunne 更像仓库里的项目记忆层，而不是新的聊天入口。

## 验证重点

本版本增加了回归测试，复现“已有 `.agents/skills/autorunne-workflow/SKILL.md`，但沙盒阻止重写”的情况，确认：

- `autorunne open` 仍然成功 resume；
- 原有集成文件内容不被破坏；
- Autorunne session log 仍然记录 integration update；
- direct Codex 后续可以继续 checkpoint / validate。

## 发布信息

- GitHub Release：`v0.6.19`
- PyPI：`autorunne==0.6.19`
- 安装/升级：

```bash
pipx upgrade autorunne --pip-args '--no-cache-dir -i https://pypi.org/simple'
```

如果是首次安装：

```bash
pipx install autorunne
```
