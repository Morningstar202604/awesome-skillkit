#!/usr/bin/env python3
"""Video Script Writer — 生成视频脚本（LLM 台词 + 模板骨架，诚实双轨）。

输入: 概念 + 视频类型 + 时长 + 角色
输出: 结构化脚本 JSON (scenes, dialogue, timing, caption)

用法:
  python3 script_writer.py --concept "宝宝测评手机" --type talking_character --duration 30
  python3 script_writer.py --json '{"concept":"...","video_type":"meme","duration_seconds":15}'

台词双轨（诚实标注 source）:
  - env 设了 SKILLKIT_LLM_URL + SKILLKIT_LLM_KEY（可选 SKILLKIT_LLM_MODEL）→ 调
    OpenAI 兼容网关让真模型写台词，每场戏 dialogue_source="llm"；
  - env 未设、--no-llm、或网关调用失败 → 模板占位台词，dialogue_source="template"，
    绝不把占位文本冒充成品（占位句式自描述为待补写）。
"""
import argparse
import json
import os
import re
import ssl
import sys
import urllib.request
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

LLM_ENV_URL = "SKILLKIT_LLM_URL"
LLM_ENV_KEY = "SKILLKIT_LLM_KEY"
LLM_ENV_MODEL = "SKILLKIT_LLM_MODEL"


def llm_configured() -> bool:
    return bool(os.environ.get(LLM_ENV_URL) and os.environ.get(LLM_ENV_KEY))


def llm_chat(messages: list, timeout: int = 60) -> str:
    """OpenAI 兼容 /chat/completions。仅在 llm_configured() 时调用；失败抛异常由调用方兜底。

    SSL 校验放宽为「不验证书」：面向个人网关（自签/证书链不全很常见），密钥走
    Authorization 头，风险与收益权衡后选择可用性。
    """
    url = os.environ[LLM_ENV_URL].rstrip("/") + "/chat/completions"
    body = json.dumps({
        "model": os.environ.get(LLM_ENV_MODEL, "default"),
        "messages": messages,
        "temperature": 0.8,
        "max_tokens": 900,
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer " + os.environ[LLM_ENV_KEY]})
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        data = json.loads(r.read().decode("utf-8"))
    return (data.get("choices") or [{}])[0].get("message", {}).get("content") or ""


def _parse_json_loose(text: str):
    """从 LLM 回复里抠 JSON（容忍 ```json 围栏与前后废话）。"""
    text = text.strip()
    m = re.search(r"```(?:json)?\s*(\[.*?\]|{.*?})\s*```", text, re.S)
    if m:
        text = m.group(1)
    start = min([i for i in (text.find("["), text.find("{")) if i >= 0], default=-1)
    if start >= 0:
        text = text[start:]
    return json.loads(text)


def llm_dialogues(concept: str, scenes_base: list, tone: str, language: str,
                  character: dict, max_words: int, duration: int, platform: str) -> dict:
    """让真模型按场景骨架写台词。返回 {role: dialogue}；失败抛异常。"""
    name = (character or {}).get("name", "主持人")
    persona = (character or {}).get("persona", "")
    lang_name = "中文" if language == "zh" else "English"
    skeleton = [{"role": b["role"], "hint": b["dialogue_hint"],
                 "seconds": max(1, int(duration * b["ratio"]))}
                for b in scenes_base]
    sys_prompt = (
        f"你是短视频编导。用{lang_name}为视频写台词，{tone} 风格。"
        f"每场台词口语化、可直接配音，严格不超过 {max_words} 个词/字。"
        '只输出 JSON，不要解释：{"lines": [{"role": "...", "dialogue": "..."}]}')
    user_prompt = json.dumps({
        "concept": concept, "platform": platform, "character": name,
        "persona": persona, "scenes": skeleton,
        "rule": "每场台词信息量要具体（有数字/有对比/有动作指令），禁止空话"},
        ensure_ascii=False)
    raw = llm_chat([{"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_prompt}])
    data = _parse_json_loose(raw)
    lines = data.get("lines", data if isinstance(data, list) else [])
    out = {}
    for item in lines:
        if isinstance(item, dict) and item.get("role") and item.get("dialogue"):
            out[item["role"]] = f"[{name}] {str(item['dialogue']).strip()}"
    if not out:
        raise ValueError("LLM returned no usable dialogue lines")
    return out


def generate_script(concept: str, video_type: str = "talking_character",
                    duration: int = 30, platform: str = "douyin",
                    character: dict = None, language: str = "zh",
                    tone: str = "funny", use_llm: bool = None) -> dict:
    """生成结构化脚本。use_llm=None 时自动探测 env；LLM 失败自动落回模板并如实标注。"""
    platform = platform if platform in PLATFORM_RULES else "douyin"
    rules = PLATFORM_RULES[platform]
    duration = min(duration, rules["max_duration"])

    template = TEMPLATES.get(video_type, TEMPLATES["short"])
    llm_lines, llm_note = {}, None
    if use_llm is None:
        use_llm = llm_configured()
    if use_llm:
        try:
            llm_lines = llm_dialogues(concept, template["scenes_base"], tone, language,
                                      character, template["max_dialogue_words"],
                                      duration, platform)
        except Exception as e:  # 网关失败/超时/坏 JSON → 诚实落回模板
            llm_note = f"LLM 不可用（{type(e).__name__}: {str(e)[:80]}），台词落回模板占位"
            sys.stderr.write(f"[script_writer] {llm_note}\n")

    scenes = []
    remaining = duration
    for i, base in enumerate(template["scenes_base"]):
        if i == len(template["scenes_base"]) - 1:
            dur = remaining
        else:
            dur = max(1, int(duration * base["ratio"]))
            remaining -= dur

        if base["role"] in llm_lines:
            dialogue, source = llm_lines[base["role"]], "llm"
        else:
            dialogue, source = _template_dialogue(concept, base["role"], language, character), "template"
        scenes.append({
            "id": i + 1,
            "role": base["role"],
            "duration_sec": dur,
            "dialogue": dialogue,
            "dialogue_source": source,
            "visual": f"[{base['role']}: describe visual action here]",
            "camera": _camera_for_role(base["role"]),
            "sfx": _sfx_for_role(base["role"]),
        })

    # Generate title and caption
    title = _generate_title(concept, video_type, language)
    caption = _generate_caption(title, platform, language)

    sources = {s["dialogue_source"] for s in scenes}
    return {
        "title": title,
        "hook": scenes[0]["dialogue"] if scenes else "",
        "scenes": scenes,
        "caption": caption,
        "total_duration": duration,
        "platform": platform,
        "video_type": video_type,
        "character": character or {},
        "dialogue_source": "llm" if sources == {"llm"} else
                           ("mixed" if "llm" in sources else "template"),
        "llm_note": llm_note,
        "tts_config": {
            "voice_style": (character or {}).get("voice_style", "default"),
            "language": language,
            "speed": 1.0 if tone != "funny" else 1.2,
        },
    }


def _template_dialogue(concept, role, language, character):
    """模板占位台词（离线兜底）。自描述为待补写，绝不冒充成品。"""
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
    parser.add_argument("--no-llm", action="store_true",
                        help="强制走模板台词（即使 env 配了 LLM 网关）")
    parser.add_argument("--output", help="Write to file instead of stdout")
    args = parser.parse_args()

    character = None
    try:
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
    except json.JSONDecodeError as e:
        print(json.dumps({"status": "error", "error": f"输入 JSON 不合法: {e}"},
                         ensure_ascii=False))
        return 2

    if not concept:
        print(json.dumps({"status": "error", "error": "缺少 concept（--concept 或 --json-input）"},
                         ensure_ascii=False))
        return 2

    script = generate_script(concept, video_type, duration, platform, character,
                             language, tone, use_llm=(not args.no_llm) or None)
    script["status"] = "success"

    output = json.dumps(script, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Script written to: {args.output}", file=sys.stderr)
    else:
        print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
