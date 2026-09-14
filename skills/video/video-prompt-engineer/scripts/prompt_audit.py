#!/usr/bin/env python3
"""prompt_audit.py — audit a text-to-video prompt against the six-slot structure.

Slots (per video-prompt-engineer SKILL.md):
  subject / action / camera / lighting / style / duration

Heuristic keyword tables — structural check only (does the slot have plausible
content), not a quality judgement. Output: JSON with per-slot hit/miss.
Exit codes: 0 = all six slots hit; 1 = one or more slots missing.
"""
import argparse
import json
import re
import sys

CAMERA_WORDS = [
    r"wide", r"establishing", r"close[- ]?up", r"macro", r"medium shot",
    r"full shot", r"extreme", r"push[- ]?in", r"pull[- ]?back", r"pull[- ]?out",
    r"pan\b", r"tilt", r"tracking", r"dolly", r"follow", r"crane", r"orbit",
    r"arc shot", r"handheld", r"static", r"locked[- ]?off", r"zoom",
    r"特写", r"远景", r"全景", r"中景", r"推", r"拉", r"摇", r"移", r"跟", r"环绕", r"固定",
]
LIGHTING_WORDS = [
    r"light", r"lighting", r"backlight", r"neon", r"golden hour", r"blue hour",
    r"noir", r"soft light", r"rim light", r"high[- ]?contrast", r"overcast",
    r"glow", r"shadow", r"silhouette", r"阳光", r"逆光", r"霓虹", r"光影", r"柔光", r"轮廓光",
]
STYLE_WORDS = [
    r"cinematic", r"live[- ]?action", r"35mm", r"film", r"camcorder",
    r"stop[- ]?motion", r"anime", r"cel", r"documentary", r"commercial",
    r"gloss", r"photoreal", r"3d render", r"claymation", r"水彩", r"电影感", r"胶片", r"动画",
]
ACTION_WORDS = [
    r"\bwalk", r"\brun", r"\bturn", r"\bpick", r"\bignite", r"\bopen", r"\bclose",
    r"\bjump", r"\bfall", r"\blook", r"\breach", r"\bsit", r"\bstand", r"\bhold",
    r"\bdrive", r"\bfly", r"\bfloat", r"\bspin", r"\bpour", r"\bpress", r"\btype",
    r"\bshine", r"\bflow", r"\bmove", r"\brise", r"\bdrop", r"\bemerge",
    r"走", r"跑", r"拿", r"点燃", r"打开", r"关", r"跳", r"落", r"看", r"坐", r"站", r"转",
]
DURATION_RE = re.compile(r"\b\d+(?:\.\d+)?\s*(?:s\b|sec|seconds|秒)\b", re.I)
RATIO_RE = re.compile(r"\b(?:16[:/]9|9[:/]16|1[:/]1|4[:/]3|21[:/]9)\b", re.I)


def audit(prompt: str) -> dict:
    p = prompt.lower()
    camera = any(re.search(w, p) for w in CAMERA_WORDS)
    lighting = any(re.search(w, p) for w in LIGHTING_WORDS)
    style = any(re.search(w, p) for w in STYLE_WORDS)
    action = any(re.search(w, p) for w in ACTION_WORDS)
    duration = bool(DURATION_RE.search(p))
    # subject: heuristic — prompt has enough noun-ish content that is not only
    # camera/light/style words; a 4+ word prompt with a determiner phrase counts.
    subject = bool(re.search(r"\b(a|an|the)\s+\w[\w\-']*(\s+\w[\w\-']*){1,}", p)) or bool(
        re.search(r"[\u4e00-\u9fff]{4,}", prompt)
    )
    slots = {
        "subject": subject,
        "action": action,
        "camera": camera,
        "lighting": lighting,
        "style": style,
        "duration": duration or bool(RATIO_RE.search(p)),
    }
    missing = [k for k, v in slots.items() if not v]
    hits = sum(1 for v in slots.values() if v)
    return {"score": f"{hits}/6", "slots": {k: ("hit" if v else "miss") for k, v in slots.items()},
            "missing": missing}


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description="六槽位视频 prompt 结构审计（subject/action/camera/lighting/style/duration）"
    )
    ap.add_argument("--prompt", "-p", required=True, help="待审计的 prompt 文本")
    ap.add_argument("--mode", choices=["audit", "write"], default="audit",
                    help="audit=审计报告（默认）；write=写后自检（同一检查，输出措辞不同）")
    ap.add_argument("--json", action="store_true", help="仅输出 JSON")
    args = ap.parse_args(argv[1:])

    result = audit(args.prompt)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"score: {result['score']}")
        for k, v in result["slots"].items():
            print(f"  {k:<10} {v}")
        if result["missing"]:
            print(f"missing slots: {', '.join(result['missing'])}")
            print("fix hints: 见 SKILL.md 六槽位词典 — 缺啥补啥，一次一个槽位")
    return 0 if not result["missing"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
