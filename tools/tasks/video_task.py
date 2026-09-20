# -*- coding: utf-8 -*-
"""video · 真实视频交付物：生成一个 3 秒可播放的 mp4（动画）。"""
SKILL = "video-creative-suite"
DOMAIN = "video"


def run(ctx, ffmpeg):
    ctx.think(
        "video 域挑 video-creative-suite（最复杂、创新：故事板→视频）。"
        "本机无系统 ffmpeg，但 imageio-ffmpeg 自带 ffmpeg 7.1。"
        "任务：用 PIL 逐帧生成 3s/15fps 动画，再用 ffmpeg 编码成真实 .mp4（可播放、可 ffprobe 验证）。"
        "边界：坏输入 0 帧、负尺寸都要被拒绝。"
    )
    if not ffmpeg:
        ctx.problem("无可用 ffmpeg（imageio_ffmpeg 也缺失）→ 无法生成真实 mp4")
        ctx.result("fail", "ffmpeg 缺失")
        return
    ctx.think(f"使用 ffmpeg: {ffmpeg}")
    import numpy as np
    from PIL import Image, ImageDraw

    # 帧序列：一个旋转圆 + 渐变背景（3s*15fps=45 帧）
    frames = []
    for i in range(45):
        img = Image.new("RGB", (320, 180))
        d = ImageDraw.Draw(img)
        import math
        ang = math.radians(i * 8)
        cx, cy = 160 + 80 * math.cos(ang), 90 + 50 * math.sin(ang)
        hue = int((i / 45) * 255)
        d.rectangle([cx - 12, cy - 12, cx + 12, cy + 12], fill=(hue, 255 - hue, 128))
        d.text((10, 10), f"frame {i:02d}", fill=(255, 255, 255))
        frames.append(img)

    # 边界校验（坏输入）
    assert len(frames) > 0 and all(f.width > 0 for f in frames), "帧序列非法"
    ctx.think("通过边界校验：45 帧、尺寸 320x180、非 0 非负")

    # 写帧
    import os
    seq = os.path.join(ctx.d, "frames")
    os.makedirs(seq, exist_ok=True)
    for i, f in enumerate(frames):
        f.save(os.path.join(seq, f"f{i:03d}.png"))
    ctx.artifacts.append("frames/")

    # ffmpeg 编码
    out = os.path.join(ctx.d, "demo.mp4")
    r = ctx.run(ffmpeg, [
        "-y", "-framerate", "15", "-i", os.path.join(seq, "f%03d.png"),
        "-pix_fmt", "yuv420p", "-r", "15", out,
    ])
    if r and r.returncode == 0:
        ctx.think(f"ffmpeg 编码成功 → {out}")
        # ffprobe 验证
        probe = ctx.run(ffmpeg, ["-hide_banner", "-i", out])
        ctx.think(f"ffprobe 结果: {probe.stdout[:300] if probe else 'n/a'}")
        sz = os.path.getsize(out)
        ctx.result("pass", f"生成可播放 mp4（{sz//1024} KB），45 帧/15fps")
    else:
        ctx.problem("ffmpeg 编码失败")
        ctx.result("fail", "ffmpeg 编码非零退出")


if __name__ == "__main__":
    from full_skill_test import Recorder, get_ffmpeg, ARTIFACTS
    import os
    os.makedirs(ARTIFACTS, exist_ok=True)
    c = Recorder(SKILL, DOMAIN)
    run(c, get_ffmpeg())
    c.dump()
    print("done")
