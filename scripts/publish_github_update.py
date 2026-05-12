#!/usr/bin/env python3
"""Publish a version update post to GitHub Discussions.

Usage:
  python scripts/publish_github_update.py --version 0.6.20
  python scripts/publish_github_update.py --version 0.6.20 --dry-run

The script uses the GitHub CLI (`gh`) for authentication. It never stores tokens.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str], *, input_text: str | None = None) -> str:
    result = subprocess.run(
        cmd,
        input=input_text,
        text=True,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip()
        raise SystemExit(f"Command failed: {' '.join(cmd)}\n{message}")
    return result.stdout.strip()


def detect_owner_repo() -> tuple[str, str]:
    url = run(["git", "remote", "get-url", "origin"])
    match = re.search(r"github\.com[:/]([^/]+)/([^/.]+)(?:\.git)?$", url)
    if not match:
        raise SystemExit(f"Cannot detect GitHub owner/repo from origin: {url}")
    return match.group(1), match.group(2)


def graphql(query: str, variables: dict) -> dict:
    args = ["gh", "api", "graphql", "-f", f"query={query}"]
    for key, value in variables.items():
        args.extend(["-F", f"{key}={value}"])
    return json.loads(run(args))


def repo_and_category(owner: str, repo: str, category: str) -> tuple[str, str]:
    query = """
    query($owner:String!, $repo:String!) {
      repository(owner:$owner, name:$repo) {
        id
        discussionCategories(first: 50) { nodes { id name slug } }
      }
    }
    """
    data = graphql(query, {"owner": owner, "repo": repo})["data"]["repository"]
    repo_id = data["id"]
    categories = data["discussionCategories"]["nodes"]
    wanted = category.lower()
    for item in categories:
        if item["name"].lower() == wanted or item["slug"].lower() == wanted:
            return repo_id, item["id"]
    available = ", ".join(item["name"] for item in categories) or "none"
    raise SystemExit(f"Discussion category not found: {category}. Available: {available}")


def existing_discussion(owner: str, repo: str, title: str) -> str | None:
    query = """
    query($owner:String!, $repo:String!) {
      repository(owner:$owner, name:$repo) {
        discussions(first: 50, orderBy: {field: CREATED_AT, direction: DESC}) {
          nodes { title url }
        }
      }
    }
    """
    nodes = graphql(query, {"owner": owner, "repo": repo})["data"]["repository"]["discussions"]["nodes"]
    for item in nodes:
        if item["title"].strip() == title.strip():
            return item["url"]
    return None


def changelog_section(version: str) -> str:
    path = ROOT / "CHANGELOG.md"
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    pattern = rf"(^##\s+{re.escape(version)}\b.*?)(?=^##\s+\d+\.\d+\.\d+\b|\Z)"
    match = re.search(pattern, text, flags=re.M | re.S)
    return match.group(1).strip() if match else ""


def default_body(version: str) -> str:
    section = changelog_section(version)
    release_url = f"https://github.com/HUAFIRE777/autorunne/releases/tag/v{version}"
    pypi_url = f"https://pypi.org/project/autorunne/{version}/"

    if version == "0.6.23":
        intro = """Autorunne 0.6.23 发布了。

这版补了一个新手最容易忘的小提醒：新项目要先 `git init`，再运行 Autorunne。"""
        bullets = """
- 非 Git 目录运行 autorunne open/init 等命令时，会直接提醒先执行 git init
- CLI 会干净退出，不再给新手看一大段 traceback
- README 30 秒上手里也明确写了 git init → autorunne open
- 继续保留 0.6.22 的状态安全和 open 日志洁净度
""".strip()
        why = """简单说：第一次用 Autorunne 时更不容易卡住。"""
        return f"""{intro}\n\n{bullets}\n\n{why}\n\n安装或更新：\n\n```bash\npipx upgrade autorunne --pip-args=\"--no-cache-dir -i https://pypi.org/simple\"\n```\n\n新安装：\n\n```bash\npipx install autorunne --pip-args=\"--no-cache-dir -i https://pypi.org/simple\"\n```\n\n检查版本：\n\n```bash\nautorunne --version\n```\n\nRelease: {release_url}\nPyPI: {pypi_url}\n""".strip()

    if version == "0.6.22":
        intro = """Autorunne 0.6.22 发布了。

这版是在 0.6.21 核心状态修复通过真实项目验证后，继续打磨日志洁净度：重复打开工作区时，SESSION_LOG 更安静、更容易读。"""
        bullets = """
- 多次 autorunne open 触发的 workspace open auto-resume 会更稳地去重
- 即使中间夹着 integration refresh/noise，相同 auto-resume 也只更新时间，不继续刷屏
- start task / checkpoint / finish summary 仍会切开不同开发阶段，保留真正进展
- 0.6.21 的 finish next_product_task 安全修复继续保留
""".strip()
        why = """简单说：状态继续安全，日志更干净，下一轮 AI 打开项目时更容易接手。"""
        return f"""{intro}\n\n{bullets}\n\n{why}\n\n安装或更新：\n\n```bash\npipx upgrade autorunne --pip-args=\"--no-cache-dir -i https://pypi.org/simple\"\n```\n\n新安装：\n\n```bash\npipx install autorunne --pip-args=\"--no-cache-dir -i https://pypi.org/simple\"\n```\n\n检查版本：\n\n```bash\nautorunne --version\n```\n\nRelease: {release_url}\nPyPI: {pypi_url}\n""".strip()

    if version == "0.6.21":
        intro = """Autorunne 0.6.21 发布了。

这版只修一个很小但真实会误导下一轮 AI 的交接问题：finish 完成任务后，不再把刚完成的任务继续显示成 Next product task。"""
        bullets = """
- finish matched/active task 后，已完成任务不会再留在 next_product_task
- 如果还有 pending 产品任务，会自动回退到下一个产品任务
- 如果没有 pending 产品任务，状态视图会显示 Next product task：无
- workflow_follow_up 继续保留 finish --next 的流程跟进内容
""".strip()
        why = """简单说：下一轮 AI 打开项目时，不会再被“已经完成的任务”误导。"""
        return f"""{intro}\n\n{bullets}\n\n{why}\n\n安装或更新：\n\n```bash\npipx upgrade autorunne --pip-args=\"--no-cache-dir -i https://pypi.org/simple\"\n```\n\n新安装：\n\n```bash\npipx install autorunne --pip-args=\"--no-cache-dir -i https://pypi.org/simple\"\n```\n\n检查版本：\n\n```bash\nautorunne --version\n```\n\nRelease: {release_url}\nPyPI: {pypi_url}\n""".strip()

    if version == "0.6.20":
        intro = """Autorunne 0.6.20 发布了。\n\n这版主要修的是我自己在真实项目交接里遇到的几个小痛点：状态看不清、日志太长、项目里的 agent skill 版本没有跟着 CLI 更新。"""
        bullets = """
- repo skill front matter 会跟着当前 CLI 版本更新，不再长期停在旧版本号
- STATUS.md 直接显示最后一次验证命令、结果和摘要
- SESSION_LOG 不再把完整 build/test 输出铺进去，只保留关键摘要
- workspace open / integration updated 这类重复记录更少，交接阅读更干净
""".strip()
        why = """简单说：下一轮 AI 打开项目时，更容易知道上次做了什么、测没测过、下一步该干什么。"""
    else:
        intro = f"Autorunne {version} 发布了。"
        bullets = section or "这次更新的详细内容请看 release notes。"
        why = ""

    return f"""{intro}\n\n{bullets}\n\n{why}\n\n安装或更新：\n\n```bash\npipx upgrade autorunne --pip-args=\"--no-cache-dir -i https://pypi.org/simple\"\n```\n\n新安装：\n\n```bash\npipx install autorunne --pip-args=\"--no-cache-dir -i https://pypi.org/simple\"\n```\n\n检查版本：\n\n```bash\nautorunne --version\n```\n\nRelease: {release_url}\nPyPI: {pypi_url}\n""".strip()


def create_discussion(repo_id: str, category_id: str, title: str, body: str) -> str:
    mutation = """
    mutation($repositoryId:ID!, $categoryId:ID!, $title:String!, $body:String!) {
      createDiscussion(input: {repositoryId:$repositoryId, categoryId:$categoryId, title:$title, body:$body}) {
        discussion { url }
      }
    }
    """
    data = graphql(
        mutation,
        {
            "repositoryId": repo_id,
            "categoryId": category_id,
            "title": title,
            "body": body,
        },
    )
    return data["data"]["createDiscussion"]["discussion"]["url"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish an Autorunne version update to GitHub Discussions.")
    parser.add_argument("--version", required=True, help="Version without leading v, e.g. 0.6.20")
    parser.add_argument("--title", help="Custom discussion title")
    parser.add_argument("--body-file", type=Path, help="Markdown body file. Defaults to a generated post.")
    parser.add_argument("--category", default="Announcements", help="Discussion category name or slug")
    parser.add_argument("--repo", help="GitHub repo in owner/name form. Defaults to git origin.")
    parser.add_argument("--dry-run", action="store_true", help="Print the post without publishing")
    args = parser.parse_args()

    if args.repo:
        owner, repo = args.repo.split("/", 1)
    else:
        owner, repo = detect_owner_repo()

    version = args.version.removeprefix("v")
    default_titles = {
        "0.6.23": "Autorunne 0.6.23 发布：新项目先 git init 的友好提醒",
        "0.6.22": "Autorunne 0.6.22 发布：workspace open 日志更干净",
        "0.6.21": "Autorunne 0.6.21 发布：完成任务后不再把它当下一步",
        "0.6.20": "Autorunne 0.6.20 发布：更干净的 AI 项目交接",
    }
    title = args.title or default_titles.get(version, f"Autorunne {version} 发布：版本更新")
    body = args.body_file.read_text(encoding="utf-8") if args.body_file else default_body(version)

    if args.dry_run:
        print(f"# {title}\n")
        print(body)
        return 0

    existing = existing_discussion(owner, repo, title)
    if existing:
        print(f"Discussion already exists: {existing}")
        return 0

    repo_id, category_id = repo_and_category(owner, repo, args.category)
    url = create_discussion(repo_id, category_id, title, body)
    print(url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
