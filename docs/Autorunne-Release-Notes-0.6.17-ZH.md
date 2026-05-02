# Autorunne 0.6.17 发布说明

这版主要是账号迁移后的链接同步版本。

## 变化

- GitHub 仓库链接统一更新为：<https://github.com/HUAFIRE777/autorunne>
- README、安装脚本、使用说明、发布手册里的旧账号链接已替换。
- PyPI 包元数据里的 Homepage、Repository、Issues 会随 0.6.17 重新发布后指向新 GitHub 仓库。

## 客户安装

推荐：

```bash
pipx install autorunne
```

已经装过的用户升级：

```bash
pipx upgrade autorunne --pip-args="--no-cache-dir -i https://pypi.org/simple"
```

如果 pipx 缓存导致版本没刷新：

```bash
pipx uninstall autorunne
pipx install autorunne --pip-args="--no-cache-dir -i https://pypi.org/simple"
```

## 链接

- GitHub：<https://github.com/HUAFIRE777/autorunne>
- PyPI：<https://pypi.org/project/autorunne/>
- 版本页：<https://pypi.org/project/autorunne/0.6.17/>

## 验证

- `python -m pytest -q`
- `python -m build`
- PyPI 项目元数据检查
