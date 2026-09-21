#!/usr/bin/env python3
"""Content Editor — 文章润色/校对/风格统一。

用法:
  python3 editor.py --draft draft.json
  python3 editor.py --text "原文" --style technical
"""
import argparse
import json
import sys
from pathlib import Path

STYLE_RULES = {
    "technical": {
        "tone": "precise, objective",
        "ban": ["我觉得", "应该", "可能", "大概"],
        "use": ["根据", "分析表明", "实测", "结论是"],
        "max_sentence_len": 40,
    },
    "casual": {
        "tone": "friendly, conversational",
        "ban": ["综上所述", "由此可见"],
        "use": ["简单来说", "说白了", "你看"],
        "max_sentence_len": 25,
    },
    "news": {
        "tone": "factual, neutral",
        "ban": ["震惊", "炸了", "绝了"],
        "use": ["据悉", "报道称", "数据显示"],
        "max_sentence_len": 30,
    },
}


def edit_text(text: str, style: str = "technical") -> dict:
    """Edit/proofread text."""
    rules = STYLE_RULES.get(style, STYLE_RULES["technical"])
    issues = []
    suggestions = []

    for word in rules["ban"]:
        if word in text:
            issues.append({"type": "banned_word", "word": word, "line": text.find(word)})

    for word in rules["use"]:
        if word not in text and len(text) > 200:
            suggestions.append(f"Consider using '{word}' for {style} tone")

    # Check sentence length
    sentences = text.split("。")
    long_sentences = [s for s in sentences if len(s) > rules["max_sentence_len"]]

    return {
        "style": style,
        "issues": issues,
        "suggestions": suggestions,
        "long_sentences": len(long_sentences),
        "total_sentences": len(sentences),
        "word_count": len(text),
        "score": max(0, 100 - len(issues) * 5 - len(long_sentences) * 2),
        "edited": text,
        "status": "reviewed",
    }


def edit_article(article: dict, style: str = "technical") -> dict:
    """Edit full article."""
    all_text = " ".join(
        s.get("draft", "") for s in article.get("sections", [])
    )
    result = edit_text(all_text, style)
    result["title"] = article.get("title", "")
    result["sections_edited"] = len(article.get("sections", []))
    return result


def main():
    parser = argparse.ArgumentParser(description="Edit/proofread content")
    parser.add_argument("--draft", help="Draft JSON file")
    parser.add_argument("--text", help="Raw text to edit")
    parser.add_argument("--style", default="technical", choices=list(STYLE_RULES.keys()))
    parser.add_argument("--output", help="Output file")
    args = parser.parse_args()

    if args.draft:
        p = Path(args.draft)
        if not p.exists():
            # 旧版直接抛 FileNotFoundError traceback（rc=1 无 JSON）；改为干净错误
            print(json.dumps({"status": "error",
                              "error": f"--draft 文件不存在: {args.draft}"},
                             ensure_ascii=False))
            return 2
        try:
            article = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(json.dumps({"status": "error",
                              "error": f"--draft 不是合法 JSON: {e}"},
                             ensure_ascii=False))
            return 2
        result = edit_article(article, args.style)
    elif args.text:
        result = edit_text(args.text, args.style)
    else:
        parser.error("Need --draft or --text")
        return 2

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
