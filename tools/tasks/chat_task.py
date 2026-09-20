# -*- coding: utf-8 -*-
"""chat · 成文交付物：真实成文的高质量 system prompt 设计稿（结构化 + 可交付）。"""
SKILL = "chat-prompt-craft"
DOMAIN = "chat"


def run(ctx, ffmpeg):
    ctx.think(
        "chat 域挑 chat-prompt-craft（提示工程）。任务：真实产出一份**成文的 system prompt 设计稿**——"
        "为一个「客服助手」设计完整 system prompt（角色/边界/格式/拒答策略/示例），"
        "质量门槛：含 5 个必备小节、有 ≥2 个示例、有拒答条款。"
    )
    import os
    prompt_doc = """# 客服助手 · System Prompt 设计稿

## 1. 角色定义
你是「星河商城」高级客服，语气专业友好，单次回复 ≤ 3 句，先共情后给方案。

## 2. 能力边界
- 可答：订单查询、退换货政策、物流时效、优惠券使用
- 不可答（一律转人工）：退款到账、投诉升级、法律纠纷、账户安全

## 3. 输出格式
固定结构：`[共情] → [方案] → [下一步]`，用 markdown，不超 3 段。

## 4. 拒答与降级策略
- 命中「不可答」→ 固定话术："这部分我帮您转人工，工单号会在 1 分钟内发送。"
- 输入含辱骂/越权（改他人订单）→ 礼貌拒绝，不执行。

## 5. 示例
**用户**：我的订单 3 天没发货
**助手**：
[共情] 抱歉让您久等了。
[方案] 订单超过 48h 未发货可一键催发货。
[下一步] 我已为您催单，预计 2h 内更新物流。

**用户**：帮我改我同事的收货地址
**助手**：
[共情] 理解您想帮同事。
[方案] 出于账户安全，我只能操作您本人订单。
[下一步] 请让同事本人发起修改，或转人工协助。
"""
    p = os.path.join(ctx.d, "system_prompt_design.md")
    ctx.write_file("system_prompt_design.md", prompt_doc, "成文 system prompt 设计稿")
    text = open(p, encoding="utf-8").read()
    sections = sum(1 for s in ["角色", "边界", "格式", "拒答", "示例"] if s in text)
    examples = text.count("**用户**")
    ctx.think(f"小节命中 {sections}/5，示例数 {examples}")
    ok = sections == 5 and examples >= 2
    ctx.result("pass" if ok else "warn", "成文 system prompt 设计稿（5 小节 + ≥2 示例 + 拒答条款）" if ok else "设计稿未达结构门槛")


if __name__ == "__main__":
    from full_skill_test import Recorder, get_ffmpeg, ARTIFACTS
    import os
    os.makedirs(ARTIFACTS, exist_ok=True)
    c = Recorder(SKILL, DOMAIN)
    run(c, get_ffmpeg())
    c.dump()
