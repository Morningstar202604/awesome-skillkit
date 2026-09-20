
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
