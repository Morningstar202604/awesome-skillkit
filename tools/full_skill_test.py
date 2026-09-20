#!/usr/bin/env python3
"""
full_skill_test.py — 第一代全量"真实交付物"测试驱动器。

目标：对 awesome-skillkit 的 18 个领域各挑 1 个最具"复杂度+创新"代表性的 skill，
跑真实任务，产出**真实可验证的交付物**（视频 / 图片 / 可运行程序 / 成文文章 / 设计方案），
并把**思维链、执行过程、遇到的问题、缺失/更优方案**全量记录进日志。

设计原则（延续 skill 本质：固定步骤 + 可验证）：
- 每个任务 = 一个严格输入（边界/坏输入/真实参数），跑 skill 的入口脚本（或等价的
  LLM 提示 + 脚本组合），产出真实文件。
- 统一交付物落 `tests/_full_test_artifacts/<domain>/<skill>/`，**不删除**（迭代记录）。
- 每个 skill 产出一份 `process_log.md`（思维链 + 全过程 + 问题 + 更优方案），便于团队后续迭代。
- 离线可跑优先；需网络的 mock；生成视频用 imageio-ffmpeg 自带的 ffmpeg（已确认本机无系统 ffmpeg）。

输出：
  tests/_full_test_artifacts/report.md   全量报告（18 域 × 结果 × 交付物清单 × 问题记录）
  tests/_full_test_artifacts/<domain>/<skill>/...   真实交付物
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTIFACTS = os.path.join(REPO, "tests", "_full_test_artifacts")
FFMPEG = None


def get_ffmpeg() -> str:
    global FFMPEG
    if FFMPEG:
        return FFMPEG
    p = shutil.which("ffmpeg")
    if not p:
        try:
            import imageio_ffmpeg
            p = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            p = ""
    FFMPEG = p
    return p


def ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


class Recorder:
    """全量记录：思维链、执行过程、遇到的问题、缺失、更优方案。"""

    def __init__(self, skill: str, domain: str):
        self.skill = skill
        self.domain = domain
        self.d = os.path.join(ARTIFACTS, domain, skill)
        os.makedirs(self.d, exist_ok=True)
        self.lines = [f"# {skill} · 全量测试过程全量记录", "", f"- 域: {domain} | 时间: {ts()}", "- 结果: （未设置）"]
        self.problems = []
        self.better_ideas = []
        self.artifacts = []
        self._verdict = ""
        self._summary = ""

    def think(self, s: str):
        self.lines.append(f"\n### 思维链 / 过程\n{s}")

    def run(self, cmd: str, args: list, timeout=120):
        """跑一条命令，记录全过程与结果。"""
        self.lines.append(f"\n### 执行\n```\n$ {cmd} {' '.join(args)}\n```")
        try:
            r = subprocess.run([cmd] + args, capture_output=True, text=True, timeout=timeout, cwd=REPO)
            out = (r.stdout or "").strip()
            err = (r.stderr or "").strip()
            self.lines.append(f"\n**退出码**: {r.returncode}")
            if out:
                self.lines.append(f"\n**stdout**:\n```\n{out[:4000]}\n```")
            if err:
                self.lines.append(f"\n**stderr**:\n```\n{err[:4000]}\n```")
            if r.returncode != 0:
                self.problems.append(f"cmd `{cmd} {args}` exit {r.returncode}: {err[:200]}")
            return r
        except Exception as e:
            self.problems.append(f"cmd `{cmd} {args}` threw {e}")
            self.lines.append(f"\n**异常**: {e}")
            return None

    def write_file(self, name: str, content: str, note: str = ""):
        p = os.path.join(self.d, name)
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(content)
        self.artifacts.append(name)
        if note:
            self.lines.append(f"\n**产出文件**: `{name}` — {note}")
        return p

    def problem(self, s: str):
        self.problems.append(s)

    def better(self, s: str):
        self.better_ideas.append(s)

    def result(self, verdict: str, summary: str):
        self._verdict = verdict
        self._summary = summary
        # 替换第 3 行的"未设置"占位
        self.lines.insert(3, f"- 结果: **{verdict}** | {summary}")
        # 去掉原有占位（lines[3] 现在是占位，需删除）
        try:
            self.lines.remove("- 结果: （未设置）")
        except ValueError:
            pass

    def dump(self):
        self.lines += [
            "",
            "## 遇到的问题（全量记录）",
        ]
        self.lines += [f"- {p}" for p in self.problems] if self.problems else ["- （无）"]
        self.lines += ["", "## 缺失 / 更优方案备忘", ]
        self.lines += [f"- {b}" for b in self.better_ideas] if self.better_ideas else ["- （无）"]
        self.lines += ["", "## 交付物清单（全部保留，不删除）", ]
        self.lines += [f"- `{a}`" for a in self.artifacts] if self.artifacts else ["- （无文件产出）"]
        self.write_file("process_log.md", "\n".join(self.lines))
        return {
            "skill": self.skill,
            "domain": self.domain,
            "verdict": getattr(self, "_verdict", ""),
            "problems": self.problems,
            "better": self.better_ideas,
            "artifacts": self.artifacts,
        }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True, help="task module name under tools/tasks/ (no .py)")
    ap.add_argument("--domain", required=True)
    args = ap.parse_args()
    # 确保 tools/ 本身在 sys.path，让 `tasks.<name>` 可导入（Windows cwd 下）
    import sys
    if REPO not in sys.path:
        sys.path.insert(0, REPO)
    if os.path.join(REPO, "tools") not in sys.path:
        sys.path.insert(0, os.path.join(REPO, "tools"))
    mod = __import__(f"tasks.{args.task}", fromlist=[args.task])
    ctx = Recorder(mod.SKILL, args.domain)
    mod.run(ctx, get_ffmpeg())
    ctx.dump()
    print(json.dumps({
        "skill": mod.SKILL, "domain": args.domain, "verdict": getattr(ctx, "_verdict", ""),
        "artifacts": ctx.artifacts, "problems": ctx.problems, "better": ctx.better_ideas,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
