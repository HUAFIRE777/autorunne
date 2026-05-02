# Autorunne 0.6.17 发布说明

0.6.17 是一次面向正式开源传播的同步版本。重点不是堆新功能，而是把 GitHub 新地址、PyPI 包信息、README、使用手册、宣传材料和商业说明对齐，方便朋友、学员和早期用户直接安装升级。

## 这次解决什么

之前 0.6.16 已经能正常安装和使用，但 PyPI 上旧版本的包信息仍然指向旧 GitHub 用户名。PyPI 已发布版本不能原地改 metadata，所以这次发 0.6.17，用一个新的公开版本把项目主页、仓库地址和问题反馈地址全部同步到：

<https://github.com/HUAFIRE777/autorunne>

## 适合谁升级

- 已经装过 Autorunne，想跟朋友或学员演示最新公开版本的人
- 准备用 `pipx install autorunne` 给新机器安装的人
- 想看 README、使用手册、宣传手册、商业计划书是否已经统一的人
- 正在用 Codex、Claude Code、Hermes、Cursor、Copilot 接手老项目的人

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

## 当前定位

Autorunne 0.6.17 适合正式开源展示、教学演示、顾问交付流程和早期商业验证。

一句话介绍：

> Autorunne 给每个 Git 仓库加一层本地项目记忆，让不同 AI 编程工具都能知道这个项目上次做到哪、验证过什么、下一步该做什么。

## 已同步内容

- GitHub 仓库地址
- PyPI package metadata
- README
- GitHub 开源使用手册
- 安装与使用操作手册
- 产品说明书
- 开源宣传手册
- 商业计划书
- 对外定位与销售话术
- 商业稳定性说明

## 发布信息

- GitHub Release：`v0.6.17`
- PyPI：`autorunne==0.6.17`
- GitHub：<https://github.com/HUAFIRE777/autorunne>
- PyPI：<https://pypi.org/project/autorunne/>

## 商业稳定性判断

0.6.17 仍然是可商用验证的 Beta 工作流层。它不是完整企业平台，但已经适合拿来做真实项目里的“接入、继续开发、验证、收尾”和对外演示。
