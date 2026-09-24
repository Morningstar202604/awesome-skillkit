#!/usr/bin/env python3
"""channel_fit_check.py — audit marketing copy against channel constraints.

Built-in channel table (2026-09 snapshot) with hard physical constraints:
word budget, line limit, CTA count cap, hook requirement. Structural check
only (does the variant physically fit the channel), not a quality judgement.

Output: JSON report. Exit codes: 0 = all pass; 1 = one or more fail;
2 = usage error.
"""
import argparse
import json
import re
import sys

# channel: (max_chars, max_lines, max_cta, hook_required, note)
CHANNELS = {
    "xhs":           (1000, 0, 1, True,  "Xiaohongshu note: body <=1000 chars, title <=20 chars, CTA <=1"),
    "douyin-spoken": (240,  0, 1, True,  "Douyin spoken: ~60 chars/15s, default 4 segments / 240 chars, hook in first 3s"),
    "moments":       (300,  6, 1, True,  "WeChat Moments: <=6 lines, hook on the first line"),
    "email-subject": (30,   1, 0, False, "Email subject: <=30 chars, mobile truncation line"),
    "search-ad":     (30,   1, 1, False, "Search ad title: <=30 chars, include the core keyword"),
}

CTA_RE = re.compile(
    r"(click|place order|grab|purchase|link|comments|DM|follow|subscribe|now|right away|"
    r"hurry|while supplies last|click to lock|"
    r"shop now|buy now|click|order now|subscribe)", re.I,
)


def audit(text, channel):
    if channel not in CHANNELS:
        return {"error": f"unknown channel '{channel}'", "known": sorted(CHANNELS)}, 2
    max_chars, max_lines, max_cta, hook_required, note = CHANNELS[channel]
    body = text.strip()
    lines = [ln for ln in body.splitlines() if ln.strip()]
    n_chars = len(re.sub(r"\s", "", body))
    n_lines = len(lines)
    n_cta = len(CTA_RE.findall(body))
    first = lines[0] if lines else ""

    checks = []
    if max_chars:
        ok = n_chars <= max_chars
        checks.append({"check": "word_budget", "pass": ok,
                       "detail": f"{n_chars} chars vs limit {max_chars}",
                       "fix": None if ok else "trim to the channel's word budget; cut evidence only as last resort"})
    if max_lines:
        ok = n_lines <= max_lines
        checks.append({"check": "line_limit", "pass": ok,
                       "detail": f"{n_lines} non-empty lines vs limit {max_lines}",
                       "fix": None if ok else "merge lines; each line must carry its own point"})
    ok = n_cta <= max(1, max_cta) if max_cta else True
    checks.append({"check": "cta_count", "pass": ok,
                   "detail": f"{n_cta} CTA-ish tokens vs cap {max_cta or 0}",
                   "fix": None if ok else "keep exactly one CTA — two CTAs equal zero"})
    if hook_required:
        ok = len(first) >= 6 and not re.match(r"^(we|our company|dear)", first)
        checks.append({"check": "hook_first_line", "pass": ok,
                       "detail": f"first line: {first[:24]!r}",
                       "fix": None if ok else "first line must be a concrete hook, not a greeting"})
    if channel in ("email-subject", "search-ad"):
        ok = "！" not in body and "!" not in body
        checks.append({"check": "no_bang_spam", "pass": ok,
                       "detail": "exclamation marks in subject lines read as spam",
                       "fix": None if ok else "drop exclamation marks"})

    failed = [c["check"] for c in checks if not c["pass"]]
    return {
        "channel": channel, "note": note,
        "stats": {"chars": n_chars, "lines": n_lines, "cta_tokens": n_cta},
        "checks": checks, "missing": failed,
        "status": "pass" if not failed else "fail",
    }, (1 if failed else 0)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Channel fit audit for marketing copy.")
    ap.add_argument("--file", help="copy file")
    ap.add_argument("--text", help="copy text inline")
    ap.add_argument("--channel", required=True, choices=sorted(CHANNELS))
    args = ap.parse_args(argv)

    if args.file:
        text = open(args.file, encoding="utf-8").read()
    elif args.text is not None:
        text = args.text
    else:
        text = sys.stdin.read()
    if not text.strip():
        print(json.dumps({"error": "empty copy"}))
        return 2
    report, code = audit(text, args.channel)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
