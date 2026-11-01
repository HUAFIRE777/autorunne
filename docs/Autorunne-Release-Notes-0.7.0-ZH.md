# Autorunne 0.7.0 发布说明：AutoRunne 2.0 认知自演化重大升级

**状态：正式发布**  
**发布版本：v0.7.0 (AutoRunne 2.0 认知内核)**  
**发布日期：2026-11-02**

- GitHub Release：<https://github.com/HUAFIRE777/autorunne/releases/tag/v0.7.0>
- PyPI：<https://pypi.org/project/autorunne/0.7.0/>

---

## 重大升级概述：从“项目状态记录层”跃升为“项目认知自演化大脑”

过去的 Autorunne 专注于在 Git 本地维护上下文、任务与验证记录。而 **0.7.0** 是一次里程碑式的飞跃：正式将 **Auto-Dream 认知睡眠循环与记忆图谱** 深度并入 AutoRunne 核心，让跨 Agent（Claude Code、Codex、Cursor、Antigravity、Copilot）在反复接力编码时不仅能“看清进度”，更能**“越写越聪明、自主反思进化”**。

---

## 核心新特性

### 1. 纯 Python 原生 4 阶段 Auto-Dream 认知状态图谱
在 `src/autorunne/core/dream.py` 中实现了完整的定向状态图：
- **Orient（定向节点）**：自动探测工作区 `.autorunne/memory/` 或 `.agent/memory/`，对齐最新记忆锚点；
- **Gather Signal（信号提取节点）**：精准捕捉未提取的变更事件、用户修正铁律（如“不是/改成/必须用/不要用”等敏感意图）与关键架构决策；
- **Synthesize（经验结晶节点）**：分类归纳至 `general_rules.md`、`architecture_rules.md`、`user_preferences.md` 等专题文件，并原生内置敏感 Token/密码/私钥过滤器；
- **Prune & Index（修剪与建索节点）**：**严格死守 < 200 行根索引预算**。超出预算时自动向深层历史归档，根目录索引永远短小精悍。

### 2. “谁开发谁提纯”机制（零 API 成本，拒绝强行锁死额度）
- 真正编写业务逻辑、调试 Bug 的模型拥有当前会话中最热、最准确的现场记忆。
- Autorunne 2.0 摒弃了强行绑定第三方外部 API 调用的繁琐方案，改为通过 Agent Repo Skill 指令，驱动当前模型在交付时自然进行上下文内（In-Context）自省提纯。
- 零额外 Token 费用，零外部额度依赖。

### 3. 全生命周期后台无感自动化（彻底告别手动 CLI）
用户与开发者无需在命令行反复输入 `autorunne dream`：
- **Git Commit 自动驱动**：`autorunne hooks` 已集成 `post-commit` Git 钩子，代码提交瞬间在后台自动完成一轮梦境沉淀；
- **任务交接自动驱动**：Agent 调用 `autorunne finish` 或 `autorunne auto-finish` 时，后台无感提取本轮开发经验；
- **新子命令支持**：提供 `autorunne dream --status`（查看健康度与行数预算）与 `autorunne dream --record "<rule>"`（显式沉淀铁律）。

---

## 升级指南

推荐使用 `pipx` 升级全局 CLI：

```bash
pipx upgrade autorunne --pip-args="--no-cache-dir -i https://pypi.org/simple"
```

或者一键重装：

```bash
pipx install --force autorunne
```

验证安装版本：

```bash
autorunne --version
# 输出: AutoRunne 0.7.0
```

在现有项目中激活认知钩子：

```bash
autorunne open --with-vscode
autorunne hooks
```
