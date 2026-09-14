#!/usr/bin/env python3
"""scene_lint.py — validate a storyboard/ directory produced by storyboard-designer.

Checks (per SKILL.md 交付标准):
  1. scene-NN.md files exist, two-digit numbering, no gaps, starts at 01
  2. every scene file contains all 9 required fields
  3. duration lines parse as seconds within 1-10s per scene

Exit codes: 0 = all OK; 1 = violations found (listed on stdout).
"""
import argparse
import re
import sys
from pathlib import Path

REQUIRED_FIELDS = [
    ("时长", r"时长:\s*\S+"),
    ("画幅", r"画幅:\s*\S+"),
    ("景别", r"景别:\s*\S+"),
    ("画面", r"画面:\s*\S+"),
    ("运镜", r"运镜:\s*\S+"),
    ("光影", r"光影:\s*\S+"),
    ("声音", r"声音:\s*\S+"),
    ("视频 prompt", r"视频 prompt:\s*\S+"),
    ("转场", r"转场:\s*\S+"),
]

SCENE_RE = re.compile(r"^scene-(\d{2})\.md$")
DURATION_RE = re.compile(r"时长:\s*(\d+(?:\.\d+)?)\s*s", re.I)


def lint(directory: Path) -> list[str]:
    problems: list[str] = []
    scene_files = sorted(p for p in directory.glob("scene-*.md") if SCENE_RE.match(p.name))
    if not scene_files:
        return [f"NO-SCENES: {directory} 下没有任何 scene-NN.md"]

    nums = [int(SCENE_RE.match(p.name).group(1)) for p in scene_files]
    if nums[0] != 1:
        problems.append(f"START: 场景编号从 {nums[0]:02d} 开始，必须从 01 起")
    for a, b in zip(nums, nums[1:]):
        if b != a + 1:
            problems.append(f"GAP: {a:02d} -> {b:02d} 跳号")

    for p in scene_files:
        text = p.read_text(encoding="utf-8")
        for name, pattern in REQUIRED_FIELDS:
            if not re.search(pattern, text):
                problems.append(f"FIELD: {p.name} 缺少字段「{name}」")
        m = DURATION_RE.search(text)
        if m:
            sec = float(m.group(1))
            if not (1 <= sec <= 10):
                problems.append(f"DURATION: {p.name} 时长 {sec}s 超出 1-10s 生成安全区")
    return problems


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="storyboard 目录校验器（scene_lint）")
    ap.add_argument("directory", help="storyboard 目录路径（含 scene-NN.md）")
    args = ap.parse_args(argv[1:])

    d = Path(args.directory)
    if not d.is_dir():
        print(f"ERROR: 目录不存在: {d}")
        return 1

    problems = lint(d)
    if problems:
        print(f"FAIL: {len(problems)} 处问题")
        for x in problems:
            print(" -", x)
        return 1
    print("ALL OK: 场景编号连续、9 字段齐全、时长在安全区")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
