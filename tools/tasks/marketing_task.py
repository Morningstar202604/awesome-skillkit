# -*- coding: utf-8 -*-
"""marketing · 成文 + 可运行交付物：真实可运行的营销文案生成器（多渠道变体 + 字数控制）。"""
SKILL = "product-copywriter"
DOMAIN = "marketing"


def run(ctx, ffmpeg):
    ctx.think(
        "marketing 域挑 product-copywriter。任务：生成一个**真实可运行**的文案生成器——"
        "输入产品核心卖点，按渠道（微博/知乎/短信）出**字数受控**的变体，真实输出文本。"
        "边界：短信渠道 ≤ 70 字（超出截断 + 标记）、空卖点拒绝。"
    )
    import os
    code = r'''
import sys

HOOKS = {
    "weibo": "限时开抢！",
    "zhihu": "一个被低估的解决方案。",
    "sms": "【通知】",
}
LIMITS = {"weibo": 140, "zhihu": 400, "sms": 70}

def make(product, benefit, channel="weibo"):
    if not product or not benefit:
        raise ValueError("product and benefit required")
    hook = HOOKS.get(channel, HOOKS["weibo"])
    body = f"{hook} {product}：{benefit}。"
    limit = LIMITS.get(channel, 140)
    if len(body) > limit:
        body = body[: limit - 1] + "…"
        return body, True
    return body, False

if __name__ == "__main__":
    for ch in ["weibo", "zhihu", "sms"]:
        text, cut = make("AI 笔记 App", "3 秒把长视频变成结构化笔记", ch)
        print(f"[{ch}] len={len(text)} cut={cut} :: {text}")
    assert len(make('x' * 200, 'y' * 200, 'sms')[0]) <= 70
    print("OK")
'''
    p = os.path.join(ctx.d, "copy_gen.py")
    ctx.write_file("copy_gen.py", code, "可运行营销文案生成器（多渠道字数控制）")
    r = ctx.run("python", [p])
    ok = r and r.returncode == 0 and "OK" in r.stdout
    ctx.think(r.stdout.strip() if r else "n/a")
    ctx.result("pass" if ok else "warn", "可运行文案生成器：3 渠道变体 + 短信字数截断全验证" if ok else "文案生成器自测未过")
    ctx.better("可接 LLM 出真正个性化文案；当前规则模板足以验证多渠道字数纪律可运行。")


if __name__ == "__main__":
    from full_skill_test import Recorder, get_ffmpeg, ARTIFACTS
    import os
    os.makedirs(ARTIFACTS, exist_ok=True)
    c = Recorder(SKILL, DOMAIN)
    run(c, get_ffmpeg())
    c.dump()
