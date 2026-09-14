#!/usr/bin/env python3
"""spec_audit.py — audit image dimensions against platform layout specs.

Checks: aspect-ratio match (1% tolerance), minimum resolution, file size
limit, and optional text-budget compliance. Reads the real image via Pillow
when --image is given and Pillow is installed; otherwise audits the declared
--width/--height (or --expect) values only.

Output: JSON report. Exit codes: 0 = all pass; 1 = one or more fail;
2 = usage error.
"""
import argparse
import json
import os
import sys

# platform: (width, height, max_file_mb, note, ratio)  — 2026-09 snapshot
# ratio: explicit aspect constraint for ratio-only platforms (w=h=0)
PLATFORM_SPECS = {
    "wechat-header":   (900, 383, 5, "公众号头图 2.35:1", None),
    "wechat-footer":   (200, 200, 2, "公众号次图 1:1", None),
    "xhs-portrait":    (1080, 1440, 32, "小红书竖图 3:4", None),
    "xhs-square":      (1080, 1080, 32, "小红书方图 1:1", None),
    "bilibili-cover":  (1146, 717, 5, "B站封面 1.6:1", None),
    "douyin-vertical": (1080, 1920, 0, "抖音竖版 9:16 (0=无限额)", None),
    "youtube-thumb":   (1280, 720, 2, "YouTube 缩略图 16:9", None),
    "zhihu-header":    (0, 0, 0, "知乎头图 16:9 横图（比例约束）", 16 / 9),
}

SAFE_MARGIN_RATIO = 0.08   # keep text >=8% from edges
BOTTOM_FLOAT_ZONE = 0.15   # bottom 15% is platform UI overlay area


def _ratio(w, h):
    if w <= 0 or h <= 0:
        return 0.0
    return w / h


def audit(width, height, platform=None, expect=None, file_mb=0.0, text_chars=0, text_budget=0):
    checks = []
    if platform:
        if platform not in PLATFORM_SPECS:
            return {"error": f"unknown platform '{platform}'",
                    "known": sorted(PLATFORM_SPECS)}, 2
        pw, ph, pmb, note, explicit_ratio = PLATFORM_SPECS[platform]
        target = (pw, ph) if pw and ph else None
        target_ratio = _ratio(pw, ph) if pw and ph else explicit_ratio
        limit_mb = pmb
    elif expect:
        try:
            ew, eh = (int(x) for x in expect.lower().split("x"))
        except ValueError:
            return {"error": "--expect expects WxH like 900x383"}, 2
        target, target_ratio, limit_mb = (ew, eh), _ratio(ew, eh), 0
    else:
        target = target_ratio = limit_mb = None

    if width <= 0 or height <= 0:
        return {"error": "width/height must be positive"}, 2

    if target_ratio:
        diff = abs(_ratio(width, height) - target_ratio) / target_ratio
        checks.append({
            "check": "aspect_ratio", "pass": diff <= 0.01,
            "detail": f"got {width}x{height} (r={_ratio(width, height):.3f}), "
                      f"target r={target_ratio:.3f}, deviation {diff*100:.2f}% (tol 1%)",
            "fix": "crop to target ratio, keep subject centered" if diff > 0.01 else None,
        })
    if target:
        checks.append({
            "check": "resolution", "pass": width >= target[0] and height >= target[1],
            "detail": f"got {width}x{height}, minimum {target[0]}x{target[1]}",
            "fix": "regenerate at target size; upscaling is banned" if (width < target[0] or height < target[1]) else None,
        })
    if limit_mb > 0:
        ok = file_mb <= limit_mb
        checks.append({
            "check": "file_size", "pass": ok,
            "detail": f"{file_mb:.2f}MB vs limit {limit_mb}MB",
            "fix": "re-export with stronger compression / better format" if not ok else None,
        })
    if text_budget > 0:
        ok = text_chars <= text_budget
        checks.append({
            "check": "text_budget", "pass": ok,
            "detail": f"{text_chars} chars on image vs budget {text_budget}",
            "fix": "trim on-image text back to the design spec" if not ok else None,
        })

    safe = {
        "safe_margin_ratio": SAFE_MARGIN_RATIO,
        "bottom_float_zone": BOTTOM_FLOAT_ZONE,
        "advice": "keep text away from bottom "
                  f"{BOTTOM_FLOAT_ZONE*100:.0f}% (platform overlay zone); "
                  f"margin >= {SAFE_MARGIN_RATIO*100:.0f}% of the short edge",
    }
    failed = [c["check"] for c in checks if not c["pass"]]
    report = {
        "width": width, "height": height,
        "platform": platform, "expect": expect,
        "checks": checks, "safe_area": safe,
        "missing": failed,
        "status": "pass" if not failed else "fail",
    }
    return report, (1 if failed else 0)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Platform layout spec audit.")
    ap.add_argument("--image", help="image file to audit (needs Pillow)")
    ap.add_argument("--width", type=int, help="declared width if no file")
    ap.add_argument("--height", type=int, help="declared height if no file")
    ap.add_argument("--platform", choices=sorted(PLATFORM_SPECS))
    ap.add_argument("--expect", help="custom target WxH, e.g. 900x383")
    ap.add_argument("--file-mb", type=float, default=0.0, help="file size in MB")
    ap.add_argument("--text-chars", type=int, default=0)
    ap.add_argument("--text-budget", type=int, default=0)
    args = ap.parse_args(argv)

    width, height = args.width, args.height
    file_mb = args.file_mb
    if args.image:
        if not os.path.isfile(args.image):
            print(json.dumps({"error": f"file not found: {args.image}"}), file=sys.stderr)
            return 2
        try:
            from PIL import Image
        except ImportError:
            print(json.dumps({"error": "Pillow not installed; use --width/--height"}), file=sys.stderr)
            return 2
        with Image.open(args.image) as im:
            width, height = im.size
        file_mb = os.path.getsize(args.image) / (1024 * 1024)

    if not width or not height:
        print(json.dumps({"error": "need --image or --width/--height"}), file=sys.stderr)
        return 2

    report, code = audit(width, height, args.platform, args.expect,
                         file_mb, args.text_chars, args.text_budget)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
