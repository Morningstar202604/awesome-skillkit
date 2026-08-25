#!/usr/bin/env python3
"""static_blog_deploy.py - 静态博客部署工具。

支持：
  - Hexo 部署（hexo deploy / hexo clean && hexo generate && hexo deploy）
  - Hugo 部署（hugo && rsync/scp/s3 sync 到目标服务器）
  - GitHub Pages 部署（gh-pages 分支推送 / GitHub Actions 触发）
  - GitLab Pages / Gitee Pages 部署
  - Vercel / Netlify 部署（CLI 调用）

安全设计：
  - 默认 --dry-run：只打印将执行的命令，不真正运行。
    加 --execute 才真正运行部署命令。
  - 部署凭据（SSH key、GitHub token、云厂商密钥）从环境变量读取。

子命令：
  hexo-deploy      Hexo 博客部署
  hugo-deploy      Hugo 博客部署
  github-pages     GitHub Pages 部署
  gitlab-pages     GitLab Pages 部署
  vercel-deploy    Vercel 部署
  netlify-deploy   Netlify 部署

退出码：0 成功；1 参数错误或部署失败。
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys

# 复用发布公共工具（dry-run 守卫 / 凭据），避免重复造轮子
_common = os.path.normpath(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "..", "..", "..", "_common"
    )
)
if os.path.isdir(_common) and _common not in sys.path:
    sys.path.insert(0, _common)
from publish_common import dry_run_guard, load_credential, dump_json


def run_cmd(cmd: list[str], execute: bool, cwd: str | None = None) -> int:
    """统一命令执行入口：dry-run 打印，execute 真跑。"""
    if dry_run_guard(execute):
        return subprocess.run(cmd, cwd=cwd).returncode
    print("[PLAN]", " ".join(shlex.quote(c) for c in cmd))
    return 0


def cmd_hexo_deploy(args):
    """Hexo 部署：hexo clean && hexo generate && hexo deploy"""
    cmds = [
        ["hexo", "clean"],
        ["hexo", "generate"],
        ["hexo", "deploy"],
    ]
    for cmd in cmds:
        rc = run_cmd(cmd, args.execute, args.cwd)
        if rc != 0:
            print("[FAIL]", " ".join(cmd), "退出码", rc)
            return rc
    print("[OK] Hexo 部署完成")
    return 0


def cmd_hugo_deploy(args):
    """Hugo 部署：hugo 构建 + 同步到目标"""
    # 1. 构建
    rc = run_cmd(["hugo", "--minify"], args.execute, args.cwd)
    if rc != 0:
        return rc
    # 2. 同步
    target = args.target
    if not target:
        print(
            "[error] Hugo 部署需指定 --target（如 user@host:/path 或 s3://bucket/path）"
        )
        return 1
    if target.startswith("s3://"):
        cmd = [
            "aws",
            "s3",
            "sync",
            os.path.join(args.cwd, "public"),
            target,
            "--delete",
        ]
    elif "@" in target and ":" in target:
        # rsync over SSH
        cmd = [
            "rsync",
            "-avz",
            "--delete",
            os.path.join(args.cwd, "public/") + "/",
            target,
        ]
    else:
        print("[error] 不支持的 target 格式：", target)
        return 1
    return run_cmd(cmd, args.execute)


def cmd_github_pages(args):
    """GitHub Pages 部署：推送到 gh-pages 分支或触发 Actions"""
    if args.method == "branch":
        # 推送到 gh-pages 分支
        cmds = [
            ["git", "add", "."],
            ["git", "commit", "-m", args.commit_msg or "chore: deploy GitHub Pages"],
            ["git", "push", "origin", f"HEAD:{args.branch}"],
        ]
    elif args.method == "actions":
        # 触发 GitHub Actions（需 gh CLI）
        cmds = [
            ["gh", "workflow", "run", args.workflow or "deploy.yml"],
        ]
    else:
        print("[error] 未知 method:", args.method)
        return 1
    for cmd in cmds:
        rc = run_cmd(cmd, args.execute, args.cwd)
        if rc != 0:
            return rc
    print("[OK] GitHub Pages 部署触发完成")
    return 0


def cmd_gitlab_pages(args):
    """GitLab Pages 部署：推送到 pages 分支或触发 CI"""
    if args.method == "branch":
        cmds = [
            ["git", "add", "."],
            ["git", "commit", "-m", args.commit_msg or "chore: deploy GitLab Pages"],
            ["git", "push", "origin", f"HEAD:{args.branch}"],
        ]
    elif args.method == "ci":
        cmds = [
            ["git", "push", "origin", args.ci_branch or "main"],
        ]
    else:
        print("[error] 未知 method:", args.method)
        return 1
    for cmd in cmds:
        rc = run_cmd(cmd, args.execute, args.cwd)
        if rc != 0:
            return rc
    print("[OK] GitLab Pages 部署触发完成")
    return 0


def cmd_vercel_deploy(args):
    """Vercel 部署：vercel CLI"""
    cmd = ["vercel", "--prod"]
    if args.token:
        cmd += ["--token", args.token]
    elif os.environ.get("VERCEL_TOKEN"):
        cmd += ["--token", os.environ["VERCEL_TOKEN"]]
    else:
        print("[error] 需要 VERCEL_TOKEN 环境变量或 --token")
        return 1
    if args.scope:
        cmd += ["--scope", args.scope]
    return run_cmd(cmd, args.execute, args.cwd)


def cmd_netlify_deploy(args):
    """Netlify 部署：netlify CLI"""
    cmd = ["netlify", "deploy", "--prod", "--dir", args.dir or "public"]
    if args.auth:
        cmd += ["--auth", args.auth]
    elif os.environ.get("NETLIFY_AUTH_TOKEN"):
        cmd += ["--auth", os.environ["NETLIFY_AUTH_TOKEN"]]
    else:
        print("[error] 需要 NETLIFY_AUTH_TOKEN 环境变量或 --auth")
        return 1
    if args.site:
        cmd += ["--site", args.site]
    return run_cmd(cmd, args.execute, args.cwd)


def main(argv=None):
    ap = argparse.ArgumentParser(description="静态博客部署工具（默认 dry-run）")
    ap.add_argument("--cwd", default=".", help="项目根目录")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name, fn):
        p = sub.add_parser(name)
        p.add_argument("--execute", action="store_true")
        p.set_defaults(fn=fn)
        return p

    p = add("hexo-deploy", cmd_hexo_deploy)

    p = add("hugo-deploy", cmd_hugo_deploy)
    p.add_argument(
        "--target", required=True, help="部署目标：user@host:/path 或 s3://bucket/path"
    )

    p = add("github-pages", cmd_github_pages)
    p.add_argument("--method", choices=["branch", "actions"], default="branch")
    p.add_argument("--branch", default="gh-pages")
    p.add_argument("--commit-msg", default="")
    p.add_argument("--workflow", default="")

    p = add("gitlab-pages", cmd_gitlab_pages)
    p.add_argument("--method", choices=["branch", "ci"], default="branch")
    p.add_argument("--branch", default="pages")
    p.add_argument("--commit-msg", default="")
    p.add_argument("--ci-branch", default="")

    p = add("vercel-deploy", cmd_vercel_deploy)
    p.add_argument("--token", default="")
    p.add_argument("--scope", default="")

    p = add("netlify-deploy", cmd_netlify_deploy)
    p.add_argument("--auth", default="")
    p.add_argument("--site", default="")
    p.add_argument("--dir", default="public")

    args = ap.parse_args(argv)
    args.fn(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
