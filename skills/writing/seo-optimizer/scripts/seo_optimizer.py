#!/usr/bin/env python3
"""SEO Optimizer — article SEO optimization (keywords, meta, tags, platform adaptation).

Usage:
  python3 seo_optimizer.py --title "FastAPI performance tuning" --content article.md
  python3 seo_optimizer.py --title "a title" --content "body text" --platform juejin --output seo_result.json

Platforms: csdn (default) / juejin / wechat / baijiahao / toutiao
"""
import argparse
import json
import re
import sys
from pathlib import Path

PLATFORM_META = {
    "csdn": {"title_max": 50, "desc_max": 150, "tags_max": 5},
    "juejin": {"title_max": 60, "desc_max": 200, "tags_max": 3},
    "wechat": {"title_max": 30, "desc_max": 120, "tags_max": 0},
    "baijiahao": {"title_max": 30, "desc_max": 100, "tags_max": 3},
    "toutiao": {"title_max": 30, "desc_max": 100, "tags_max": 3},
}


def extract_keywords(text: str, top_n: int = 5) -> list:
    """Extract top keywords from text (frequency-based)."""
    # Remove common stop words
    stop_words = set("the a an of to in is and on for".split() if False else [])
    # Simple frequency count
    words = re.findall(r"[\u4e00-\u9fa5]{2,4}|[a-zA-Z]{3,}", text)
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    sorted_words = sorted(freq.items(), key=lambda x: -x[1])
    return [w for w, c in sorted_words[:top_n] if c > 1]


def optimize_title(title: str, keywords: list, platform: str = "csdn") -> dict:
    """Optimize title for SEO."""
    meta = PLATFORM_META.get(platform, PLATFORM_META["csdn"])
    issues = []
    suggestions = []

    if len(title) > meta["title_max"]:
        issues.append(f"Title too long ({len(title)} > {meta['title_max']})")
        title = title[:meta["title_max"]]

    if not keywords:
        suggestions.append("Add 1-2 keywords to title")
    elif keywords and keywords[0] not in title:
        new_title = f"{title[:20]} | {keywords[0]}"
        suggestions.append(f"Try: '{new_title}'")

    # Add number or year for CTR
    if not re.search(r"\d|202[0-9]", title):
        suggestions.append("Consider adding a number or year for higher CTR")

    return {"title": title, "issues": issues, "suggestions": suggestions}


def generate_meta(content: str, platform: str = "csdn") -> dict:
    """Generate meta description and tags."""
    meta = PLATFORM_META.get(platform, PLATFORM_META["csdn"])
    keywords = extract_keywords(content)
    desc = content[:meta["desc_max"]] if len(content) > meta["desc_max"] else content
    tags = keywords[:meta["tags_max"]]

    return {
        "meta_description": desc,
        "tags": tags,
        "keywords": keywords,
        "platform": platform,
        "score": _seo_score(content, keywords, platform),
    }


def _seo_score(content: str, keywords: list, platform: str) -> int:
    """Calculate SEO score (0-100)."""
    score = 50
    word_count = len(content)
    if word_count > 500:
        score += 10
    if word_count > 2000:
        score += 10
    if keywords and len(keywords) >= 3:
        score += 10
    # Check keyword density
    if keywords and content:
        density = sum(content.count(k) for k in keywords[:3]) / max(word_count, 1)
        if 0.01 < density < 0.08:
            score += 10
        elif density >= 0.08:
            score -= 10  # keyword stuffing
    # Headings
    headings = len(re.findall(r"^#{1,6}\s", content, re.MULTILINE))
    if headings >= 3:
        score += 5
    # Links
    links = len(re.findall(r"\[.*?\]\(.*?\)", content))
    if links >= 1:
        score += 5
    return min(100, score)


def main():
    parser = argparse.ArgumentParser(description="SEO optimizer")
    parser.add_argument("--title", default="")
    parser.add_argument("--content", help="Content file or text")
    parser.add_argument(
        "--platform",
        default="csdn",
        choices=sorted(PLATFORM_META),
        help="target platform (determines title/desc/tag length rules)",
    )
    parser.add_argument("--output", help="Output JSON file")
    args = parser.parse_args()

    content = ""
    if args.content:
        p = Path(args.content)
        if p.exists():
            content = p.read_text(encoding="utf-8")
        elif re.search(r"\.(md|txt|markdown|rst|html?)$", args.content) \
                or "/" in args.content or "\\" in args.content:
            # looks like a path but does not exist -> hard error. The old version treated
            # the path string itself as body text and produced a fake SEO report from the
            # seven characters of "article.md" while still returning 0.
            print(json.dumps({"status": "error",
                              "error": f"--content file does not exist: {args.content}"},
                             ensure_ascii=False))
            return 2
        else:
            content = args.content  # only plain text (no path features) may be treated as literal body

    result = {
        "title": optimize_title(args.title, extract_keywords(content), args.platform),
        "meta": generate_meta(content, args.platform),
    }

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
