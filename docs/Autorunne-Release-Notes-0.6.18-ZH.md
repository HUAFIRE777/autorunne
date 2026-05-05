# Autorunne 0.6.18 发布说明

0.6.18 是一次来自真实开发后的产品打磨版本。重点是让项目状态更像“可交接的证据面板”，而不是只显示一个模糊结论。

## 这次解决什么

真实开发验证后，两个问题变得很明确：

1. `finish --validate` 有用，能把项目从“未记录验证”推进到“验证通过”。
2. 但 `STATUS.md` / `START_HERE.md` 只写“上次验证：通过”还不够，用户更想直接看到验证命令和时间，比如：`cd frontend && npm run build`。
3. 单一 `NEXT_ACTION` 容易被“流程改进任务”覆盖原本的产品开发任务，所以 0.6.18 把下一步拆成两个槽位：
   - `Next product task`
   - `Workflow follow-up`

## 新增 / 改进

- `STATUS.md` 和 `START_HERE.md` 现在会渲染：
  - 上次验证状态
  - 验证命令
  - 验证时间
- `.autorunne/views/NEXT_ACTION.md` 现在会同时显示：
  - `Next product task`
  - `Workflow follow-up`
  - 兼容旧工具读取的 combined next action
- `autorunne status` 的用户摘要也会打印验证命令、验证时间、产品下一步和流程跟进。
- 如果下一步文本明显是 Autorunne / workflow / STATUS.md / 验证证据这类流程跟进，Autorunne 会尽量保留原来的产品下一步，不让流程任务覆盖产品任务。

## 升级方式

如果已经用 pipx 安装过：

```bash
pipx upgrade autorunne --pip-args="--no-cache-dir -i https://pypi.org/simple"
```

如果是第一次安装：

```bash
pipx install autorunne
```

查看版本：

```bash
autorunne --version
autorunne version
```

## 发布信息

- GitHub Release：`v0.6.18`
- PyPI：`autorunne==0.6.18`
- GitHub：<https://github.com/HUAFIRE777/autorunne>
- PyPI：<https://pypi.org/project/autorunne/>

## 商业稳定性判断

0.6.18 仍然是可商用验证的 Beta 工作流层。它不是完整企业平台，但更适合真实教学、顾问交付和早期客户演示：用户可以直接看到“验证过什么、什么时候验证、产品下一步是什么、流程还有什么要补”。
