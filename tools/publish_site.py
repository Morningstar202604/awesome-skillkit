#!/usr/bin/env python3
"""publish_site.py — 把 site/ 发布成 Pages 分支（孤儿分支，只装站点）。

用途:
  - GitCode Pages：项目设置 → Pages → 模板 html → 分支选 gh-pages → 路径 /
  - GitHub 备用：不想用 Actions 时也可 `python3 tools/publish_site.py --remote github`

流程: 在临时目录建一个孤儿 git 仓库 → 拷入 site/ 全部内容 → 强推到 <remote> 的 <branch>。
main 分支因此保持干净（dist/ 与站点副本都不进主仓库）。

用法:
  python3 tools/publish_site.py                       # 默认 origin / gh-pages
  python3 tools/publish_site.py --remote github
  python3 tools/publish_site.py --branch pages --dry-run
"""
import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent


def run(cmd: list[str], cwd: Path | None = None, capture: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None,
                          capture_output=capture, text=True)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="发布 site/ 到 Pages 分支")
    ap.add_argument("--remote", default="origin", help="git remote 名（默认 origin）")
    ap.add_argument("--branch", default="gh-pages", help="目标分支（默认 gh-pages）")
    ap.add_argument("--site", default=str(SCRIPT_DIR / "site"), help="站点目录")
    ap.add_argument("--no-build", action="store_true", help="跳过 build_site.py")
    ap.add_argument("--dry-run", action="store_true", help="只准备内容不推送")
    args = ap.parse_args(argv[1:])

    site_dir = Path(args.site)
    if not args.no_build:
        r = run([sys.executable, str(SCRIPT_DIR / "tools" / "build_site.py")])
        print(r.stdout.strip())
        if r.returncode != 0:
            print(r.stderr.strip(), file=sys.stderr)
            return 1
    if not (site_dir / "index.html").is_file():
        print(f"error: 站点目录缺少 index.html: {site_dir}", file=sys.stderr)
        return 1

    url = run(["git", "remote", "get-url", args.remote], cwd=SCRIPT_DIR).stdout.strip()
    if not url:
        print(f"error: 找不到 remote '{args.remote}'", file=sys.stderr)
        return 1
    safe_url = url.split("@")[-1] if "@" in url else url
    print(f"target: {safe_url} -> {args.branch}")

    tmp = Path(tempfile.mkdtemp(prefix="skillkit-pages-"))
    try:
        for item in site_dir.iterdir():
            src, dst = item, tmp / item.name
            shutil.copytree(src, dst) if item.is_dir() else shutil.copy2(src, dst)
        n_files = sum(1 for _ in tmp.rglob("*") if _.is_file())
        total_mb = sum(f.stat().st_size for f in tmp.rglob("*") if f.is_file()) / 1e6
        print(f"staged: {n_files} files, {total_mb:.1f} MB")

        run(["git", "init", "-q", "-b", args.branch], cwd=tmp)
        run(["git", "add", "-A"], cwd=tmp)
        run(["git", "-c", "user.name=skillkit-bot", "-c", "user.email=bot@local",
             "commit", "-q", "-m", f"site: publish ({n_files} files, {total_mb:.1f} MB)"], cwd=tmp)

        if args.dry_run:
            print(f"dry-run: 内容已就绪于 {tmp}，未推送")
            return 0
        r = run(["git", "push", "--force", url, f"{args.branch}:{args.branch}"], cwd=tmp)
        if r.returncode != 0:
            print(r.stderr.strip(), file=sys.stderr)
            return 1
        print(r.stderr.strip())
        print(f"pushed: {args.branch} -> {safe_url}")
        print("next: GitCode 项目设置 → Pages → 模板 html → 分支 " +
              f"{args.branch} → 路径 / → 保存")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
