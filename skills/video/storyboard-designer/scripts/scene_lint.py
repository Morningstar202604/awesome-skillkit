#!/usr/bin/env python3
"""scene_lint.py — validate a storyboard/ directory produced by storyboard-designer.

Checks (per SKILL.md delivery standard):
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
    ("Duration", r"Duration:\s*\S+"),
    ("Aspect", r"Aspect:\s*\S+"),
    ("Shot", r"Shot:\s*\S+"),
    ("Frame", r"Frame:\s*\S+"),
    ("Camera", r"Camera:\s*\S+"),
    ("Lighting", r"Lighting:\s*\S+"),
    ("Sound", r"Sound:\s*\S+"),
    ("Video prompt", r"Video prompt:\s*\S+"),
    ("Transition", r"Transition:\s*\S+"),
]

SCENE_RE = re.compile(r"^scene-(\d{2})\.md$")
DURATION_RE = re.compile(r"Duration:\s*(\d+(?:\.\d+)?)\s*s", re.I)


def lint(directory: Path) -> list[str]:
    problems: list[str] = []
    scene_files = sorted(p for p in directory.glob("scene-*.md") if SCENE_RE.match(p.name))
    if not scene_files:
        return [f"NO-SCENES: no scene-NN.md under {directory}"]

    nums = [int(SCENE_RE.match(p.name).group(1)) for p in scene_files]
    if nums[0] != 1:
        problems.append(f"START: scene numbering starts at {nums[0]:02d}; it must start at 01")
    for a, b in zip(nums, nums[1:]):
        if b != a + 1:
            problems.append(f"GAP: {a:02d} -> {b:02d} skips a number")

    for p in scene_files:
        text = p.read_text(encoding="utf-8")
        for name, pattern in REQUIRED_FIELDS:
            if not re.search(pattern, text):
                problems.append(f"FIELD: {p.name} missing field '{name}'")
        m = DURATION_RE.search(text)
        if m:
            sec = float(m.group(1))
            if not (1 <= sec <= 10):
                problems.append(f"DURATION: {p.name} duration {sec}s is outside the 1-10s safe generation zone")
    return problems


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="storyboard directory validator (scene_lint)")
    ap.add_argument("directory", help="path to the storyboard directory (containing scene-NN.md)")
    args = ap.parse_args(argv[1:])

    d = Path(args.directory)
    if not d.is_dir():
        print(f"ERROR: directory does not exist: {d}")
        return 1

    problems = lint(d)
    if problems:
        print(f"FAIL: {len(problems)} problem(s)")
        for x in problems:
            print(" -", x)
        return 1
    print("ALL OK: scene numbering is continuous, all 9 fields present, duration within the safe zone")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
