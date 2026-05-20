# Autorunne 0.6.28 发布说明

0.6.28 是一个很小但实际有用的“交接干净度”补丁。

0.6.27 的核心 handoff 已经通过真实复测：`current.next_action`、`current.next_product_task`、`tasks.next_up[0]`、`START_HERE`、`NEXT_ACTION`、`autorunne status` 都能指向同一个主下一步。

这次不大改这套核心逻辑，只修三个会误导新 agent 的噪音点。

## 主要变化

### 1. status 不再把 optional mirror 当核心缺失

如果 `.autorunne/views/START_HERE.md` 已经存在，根目录 mirror 缺失不再显示成核心 `Missing files`。

现在会单独显示为：

```text
Optional mirrors missing: START_HERE.md
```

意思是：核心 handoff 入口还在，缺的是可选镜像文件，不要误判为交接入口丢了。

### 2. 新增 `autorunne doctor --handoff`

只检查真正影响 agent 接手的 handoff consistency：

```bash
autorunne doctor --handoff
```

如果 handoff 一致，就退出 0。hooks、pre-commit、wrappers、package artifacts 这类增强安装项不会干扰这个判断。

### 3. 默认 doctor 区分阻断和可选

`autorunne doctor` 现在更清楚地区分：

- Blocking issues：真正会影响交接的状态缺失、视图漂移、handoff 不一致等
- Optional warnings：hooks、pre-commit、repo wrappers、repo integrations 等可选增强项

这样 pre-commit hook 运行 doctor 时，不会因为“hooks/pre-commit 还没装”这种非核心项误阻断提交。

### 4. 继续保持 integration diff 和业务 diff 分离

0.6.27 已经把 `.agents/.claude/.cursor/.github` 这类 workflow-only diff 分到 integration bucket。

0.6.28 保留这个行为，避免旧 skill version diff 被下一个 agent 误认为业务代码变更。

## 升级

```bash
pipx upgrade autorunne --pip-args="--no-cache-dir -i https://pypi.org/simple"
```

检查版本：

```bash
autorunne --version
```

应显示：

```text
AutoRunne 0.6.28
```

PyPI：`autorunne==0.6.28`

GitHub Release：`v0.6.28`
