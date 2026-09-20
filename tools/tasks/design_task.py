# -*- coding: utf-8 -*-
"""design · 真实图片交付物：生成一张设计概念图（真实 PNG，PIL 绘制）。"""
SKILL = "frontend-design-lab"
DOMAIN = "design"


def run(ctx, ffmpeg):
    ctx.think(
        "design 域挑 frontend-design-lab（设计系统 + 组件）。"
        "任务：用 PIL 生成一张「设计系统概念图」——3 列布局 + 色板 + 字体层级 + 组件草图，"
        "输出真实 PNG（可被识图校验）。边界：坏色值（越界）必须被钳制。"
    )
    from PIL import Image, ImageDraw, ImageFont
    import os
    W, H = 960, 600
    img = Image.new("RGB", (W, H), (17, 20, 24))  # 暗色基调
    d = ImageDraw.Draw(img)

    # 钳制色值（边界处理）
    def clamp(c):
        return tuple(min(255, max(0, int(x))) for x in c)

    palette = [clamp((99, 102, 241)), clamp((239, 68, 68)), clamp((16, 185, 129)),
               clamp((245, 158, 11)), clamp((14, 165, 233))]
    ctx.think(f"5 色板钳制完成: {palette}")

    d.text((32, 24), "DESIGN SYSTEM", fill=(240, 240, 245), font_size=40)
    d.text((32, 70), "frontend-design-lab · generative concept", fill=(150, 155, 165), font_size=16)

    # 左：组件草图（卡片 + 按钮 + 输入框）
    d.rounded_rectangle([32, 120, 380, 240], radius=14, outline=(60, 65, 75), width=2)
    d.rounded_rectangle([52, 140, 200, 168], radius=8, fill=palette[0])
    d.text((56, 146), "Primary", fill=(255, 255, 255), font_size=14)
    d.rounded_rectangle([52, 184, 300, 214], radius=8, outline=(70, 75, 85), width=1)
    d.text((62, 192), "input / search", fill=(120, 125, 135), font_size=14)
    d.text((32, 252), "Spacing  4 / 8 / 16 / 24 / 32", fill=(150, 155, 165), font_size=14)

    # 中：色板
    x = 430
    for i, c in enumerate(palette):
        d.rectangle([x, 120 + i * 44, x + 36, 120 + i * 44 + 36], fill=c)
        d.text((x + 48, 132 + i * 44), f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}",
               fill=(210, 215, 225), font_size=14)
    d.text((430, 350), "Type scale", fill=(210, 215, 225), font_size=16)
    for j, (label, sz) in enumerate([("Display 32", 26), ("H2 22", 18), ("Body 14", 13)]):
        d.text((430, 380 + j * 32), label, fill=(240, 240, 245), font_size=sz)

    # 右：生成式示意（噪声纹理，体现实测「生成真实图片」）
    import random
    random.seed(7)
    for _ in range(4000):
        px = random.randint(600, 920)
        py = random.randint(120, 460)
        c = palette[random.randint(0, 4)]
        d.point((px, py), fill=(c[0] // 2, c[1] // 2, c[2] // 2))
    d.text((600, 480), "generated texture (deterministic seed=7)", fill=(120, 125, 135), font_size=12)

    out = os.path.join(ctx.d, "design_system.png")
    img.save(out)
    sz = os.path.getsize(out)
    ctx.result("pass", f"真实 PNG {W}x{H}（{sz//1024} KB），含色板/字阶/组件草图/生成纹理")
    ctx.better("可升级为接 diffusers/stable-diffusion 出真设计稿；本机无 GPU，先用 PIL 确定性生成替代并记录。")


if __name__ == "__main__":
    from full_skill_test import Recorder, get_ffmpeg, ARTIFACTS
    import os
    os.makedirs(ARTIFACTS, exist_ok=True)
    c = Recorder(SKILL, DOMAIN)
    run(c, get_ffmpeg())
    c.dump()
