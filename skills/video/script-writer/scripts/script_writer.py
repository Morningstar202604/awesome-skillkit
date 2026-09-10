#!/usr/bin/env python3
"""Video Script Writer — 生成视频脚本。

输入: 概念 + 视频类型 + 时长 + 角色
输出: 结构化脚本 JSON (scenes, dialogue, timing, caption)

用法:
  python3 script_writer.py --concept "宝宝测评手机" --type talking_character --duration 30
  python3 script_writer.py --json '{"concept":"...","video_type":"meme","duration_seconds":15}'
"""
import argparse
import json
import sys
from pathlib import Path

# Platform constraints
PLATFORM_RULES = {
    "douyin": {"max_duration": 60, "caption_limit": 50, "tags_max": 3},
    "bilibili": {"max_duration": 900, "caption_limit": 100, "tags_max": 5},
    "tiktok": {"max_duration": 600, "caption_limit": 220, "tags_max": 5},
}

# Script type templates
TEMPLATES = {
    "talking_character": {
        "scenes_base": [
            {"role": "hook", "ratio": 0.15, "dialogue_hint": "Grab attention in first line"},
            {"role": "setup", "ratio": 0.35, "dialogue_hint": "Build the scenario"},
            {"role": "punchline", "ratio": 0.30, "dialogue_hint": "Deliver the joke/insight"},
            {"role": "outro", "ratio": 0.20, "dialogue_hint": "CTA or loop back"},
        ],
        "max_dialogue_words": 10,
    },
    "meme": {
        "scenes_base": [
            {"role": "setup", "ratio": 0.4, "dialogue_hint": "Set up the expectation"},
            {"role": "punchline", "ratio": 0.5, "dialogue_hint": "Subvert expectation"},
            {"role": "tag", "ratio": 0.1, "dialogue_hint": "Quick tag/CTA"},
        ],
        "max_dialogue_words": 8,
    },
    "tutorial": {
        "scenes_base": [
            {"role": "intro", "ratio": 0.1, "dialogue_hint": "What you will learn"},
            {"role": "steps", "ratio": 0.8, "dialogue_hint": "Step-by-step instructions"},
            {"role": "outro", "ratio": 0.1, "dialogue_hint": "Summary + CTA"},
        ],
        "max_dialogue_words": 20,
    },
    "vlog": {
        "scenes_base": [
            {"role": "intro", "ratio": 0.15, "dialogue_hint": "Day/theme intro"},
            {"role": "content", "ratio": 0.7, "dialogue_hint": "Main events"},
            {"role": "reflection", "ratio": 0.15, "dialogue_hint": "What did I learn"},
        ],
        "max_dialogue_words": 15,
    },
    "short": {
        "scenes_base": [
            {"role": "hook", "ratio": 0.2, "dialogue_hint": "Hook in 2s"},
            {"role": "content", "ratio": 0.6, "dialogue_hint": "Core content"},
            {"role": "punchline", "ratio": 0.2, "dialogue_hint": "End with impact"},
        ],
        "max_dialogue_words": 12,
    },
}


def generate_script(concept: str, video_type: str = "talking_character",
                    duration: int = 30, platform: str = "douyin",
                    character: dict = None, language: str = "zh",
                    tone: str = "funny") -> dict:
    """Generate a structured video script."""
    platform = platform if platform in PLATFORM_RULES else "douyin"
    rules = PLATFORM_RULES[platform]
    duration = min(duration, rules["max_duration"])

    template = TEMPLATES.get(video_type, TEMPLATES["short"])
    scenes = []
    remaining = duration

    for i, base in enumerate(template["scenes_base"]):
        if i == len(template["scenes_base"]) - 1:
            dur = remaining
        else:
            dur = max(1, int(duration * base["ratio"]))
            remaining -= dur

        scene = {
            "id": i + 1,
            "role": base["role"],
            "duration_sec": dur,
            "dialogue": _generate_dialogue(concept, base["role"], tone, language, character),
            "visual": f"[{base['role']}: describe visual action here]",
            "camera": _camera_for_role(base["role"]),
            "sfx": _sfx_for_role(base["role"]),
        }
        scenes.append(scene)

    # Generate title and caption
    title = _generate_title(concept, video_type, language)
    caption = _generate_caption(title, platform, language)

    return {
        "title": title,
        "hook": scenes[0]["dialogue"] if scenes else "",
        "scenes": scenes,
        "caption": caption,
        "total_duration": duration,
        "platform": platform,
        "video_type": video_type,
        "character": character or {},
        "tts_config": {
            "voice_style": (character or {}).get("voice_style", "default"),
            "language": language,
            "speed": 1.0 if tone != "funny" else 1.2,
        },
    }


def _generate_dialogue(concept, role, tone, language, character):
    """Generate placeholder dialogue (LLM would fill this in production)."""
    name = (character or {}).get("name", "Character")
    hints = {
        "hook": f"[{name}] Attention grabber about: {concept}",
        "setup": f"[{name}] Set up: {concept}",
        "punchline": f"[{name}] Payoff: {concept} (punchline here)",
        "outro": f"[{name}] CTA or loop back",
        "intro": f"[{name}] Intro to: {concept}",
        "steps": f"[{name}] Step 1 of: {concept}",
        "content": f"[{name}] Main content: {concept}",
        "reflection": f"[{name}] Reflection on: {concept}",
        "tag": f"[{name}] Quick tag/CTA",
    }
    return hints.get(role, f"[{name}] {concept}")


def _camera_for_role(role):
    cameras = {
        "hook": "close-up, front-facing",
        "setup": "medium shot",
        "punchline": "close-up, slight zoom in",
        "outro": "wide shot, character waving",
        "intro": "medium shot",
        "steps": "over-shoulder / screen capture",
        "content": "medium to close-up",
        "reflection": "medium shot, character looking at camera",
        "tag": "close-up",
    }
    return cameras.get(role, "medium shot")


def _sfx_for_role(role):
    sfx = {
        "hook": "whoosh / attention sound",
        "punchline": "buzzer / laugh / ding",
        "outro": "upbeat sting",
    }
    return sfx.get(role, "")


def _generate_title(concept, video_type, language):
    if language == "zh":
        prefixes = {
            "talking_character": "🍼",
            "meme": "🤣",
            "tutorial": "📚",
            "vlog": "📹",
            "short": "⚡",
        }
        return f"{prefixes.get(video_type, '📹')} {concept}"
    return f"{concept} - {video_type.replace('_', ' ').title()}"


def _generate_caption(title, platform, language):
    tags = {
        "douyin": f"#视频 #内容 #{title[:10]}",
        "bilibili": f"【{title}】 #视频",
        "tiktok": f"#video #content #{title[:15].lower().replace(' ', '')}",
    }
    return tags.get(platform, f"#{title}")


def main():
    parser = argparse.ArgumentParser(description="Generate video script")
    parser.add_argument("--concept", required=True, help="Video concept/idea")
    parser.add_argument("--type", default="talking_character", choices=list(TEMPLATES.keys()))
    parser.add_argument("--duration", type=int, default=30)
    parser.add_argument("--platform", default="douyin")
    parser.add_argument("--language", default="zh", choices=["zh", "en"])
    parser.add_argument("--tone", default="funny")
    parser.add_argument("--character", help="Character JSON string")
    parser.add_argument("--json-input", help="Full JSON input (overrides individual args)")
    parser.add_argument("--output", help="Write to file instead of stdout")
    args = parser.parse_args()

    if args.json_input:
        data = json.loads(args.json_input)
        concept = data.get("concept", args.concept)
        video_type = data.get("video_type", args.type)
        duration = data.get("duration_seconds", args.duration)
        platform = data.get("platform", args.platform)
        character = data.get("character")
        language = data.get("language", args.language)
        tone = data.get("tone", args.tone)
    else:
        concept = args.concept
        video_type = args.type
        duration = args.duration
        platform = args.platform
        character = json.loads(args.character) if args.character else None
        language = args.language
        tone = args.tone

    script = generate_script(concept, video_type, duration, platform, character, language, tone)

    output = json.dumps(script, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Script written to: {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
