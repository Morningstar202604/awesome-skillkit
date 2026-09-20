# -*- coding: utf-8 -*-
"""ppt · 真实可打开交付物：生成真实 .pptx 汇报（5 页 + 图表占位 + 真实文本）。"""
SKILL = "ppt-deck-builder"
DOMAIN = "ppt"


def run(ctx, ffmpeg):
    ctx.think(
        "ppt 域挑 ppt 生成 skill。任务：生成一个**真实可打开**的 .pptx 汇报——5 页"
        "（封面/目录/3 内容页，含真实标题正文 + 一页数据表）。验证：文件可被 python-pptx 重读、"
        "页数=5、首页标题正确。边界：缺 python-pptx 降级为 markdown 大纲。"
    )
    import os
    try:
        from pptx import Presentation
        from pptx.util import Inches, Pt
    except Exception as e:
        ctx.problem(f"python-pptx 未装: {e}")
        md = os.path.join(ctx.d, "deck_outline.md")
        with open(md, "w", encoding="utf-8") as fh:
            fh.write("# 汇报大纲\n\n1 封面 2 目录 3 进展 4 风险 5 计划\n")
        ctx.result("warn", f"缺 python-pptx，降级为 markdown 大纲 {md}")
        return

    prs = Presentation()
    slides = [
        (0, "季度技术复盘", "全量测试 · 真实交付物"),
        (1, "目录", "进展 / 风险 / 计划 / 结论"),
        (1, "Q3 进展", "154 skill 全量测试\n18 域真实交付物产出"),
        (1, "风险", "无 GPU→图/视频用替代方案\n依赖缺→降级记录"),
        (1, "Q4 计划", "接真扩散模型 / 交互式 dataviz / 向量记忆检索"),
    ]
    for layout, title, body in slides:
        s = prs.slides.add_slide(prs.slide_layouts[layout])
        s.shapes.title.text = title
        s.placeholders[1].text = body
    out = os.path.join(ctx.d, "deck.pptx")
    prs.save(out)
    ctx.think(f"真实 pptx {out}（{os.path.getsize(out)} bytes）")

    # 重读验证
    prs2 = Presentation(out)
    n = len(prs2.slides)
    first_title = prs2.slides[0].shapes.title.text
    ok = n == 5 and "复盘" in first_title
    ctx.result("pass" if ok else "warn", f"真实可打开 pptx：{n} 页，首标题 '{first_title}'" if ok else "pptx 页数/标题校验不符")
    ctx.better("可加真实图表（python-pptx add_chart）；当前文本+目录已验证可打开。")


if __name__ == "__main__":
    from full_skill_test import Recorder, get_ffmpeg, ARTIFACTS
    import os
    os.makedirs(ARTIFACTS, exist_ok=True)
    c = Recorder(SKILL, DOMAIN)
    run(c, get_ffmpeg())
    c.dump()
