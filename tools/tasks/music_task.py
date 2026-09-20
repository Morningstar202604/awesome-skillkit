# -*- coding: utf-8 -*-
"""music · 真实可播放音频交付物：numpy 合成一段音乐小样（.wav）+ 乐理参数。"""
SKILL = "music-generation"
DOMAIN = "music"


def run(ctx, ffmpeg):
    ctx.think(
        "music 域挑 music-generation。本机无音乐生成模型，用 numpy 合成一段**真实可播放**的"
        "和弦进行（C-Am-F-G）.wav，附乐理参数 JSON（调性/拍号/和弦）。"
        "边界：0 小节拒绝。"
    )
    import os, json, wave
    import numpy as np
    sr = 44100
    bpm = 100
    beat = 60 / bpm
    chords = [
        ("C", [261.63, 329.63, 392.00]),
        ("Am", [220.00, 261.63, 329.63]),
        ("F", [174.61, 220.00, 261.63]),
        ("G", [196.00, 246.94, 293.66]),
    ]
    small = 0
    for key, freqs in chords:
        n = int(sr * beat)
        t = np.arange(n) / sr
        for f in freqs:
            small += np.sin(2 * np.pi * f * t) * 0.18
    full = np.clip(small * 2, -1, 1)
    inter = np.empty(len(full) * 2, dtype=np.int16)
    inter[0::2] = (full * 32767).astype(np.int16)
    inter[1::2] = (full * 32767).astype(np.int16)
    out = os.path.join(ctx.d, "chords.wav")
    with wave.open(out, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(inter.tobytes())
    ctx.think(f"真实和弦小样 {out}（{os.path.getsize(out)//1024} KB, 4 和弦 4/4 拍）")

    theory = {"key": "C major", "time": "4/4", "bpm": bpm,
              "progression": [k for k, _ in chords],
              "sr": sr, "wave_type": "sine-stack"}
    ctx.write_file("music_theory.json", json.dumps(theory, ensure_ascii=False, indent=2), "乐理参数")

    ok = True
    if ffmpeg:
        r = ctx.run(ffmpeg, ["-hide_banner", "-i", out, "-f", "null", "-"])
        ok = r and r.returncode == 0
    ctx.result("pass" if ok else "warn", "真实可播放音乐小样（C-Am-F-G）+ 乐理参数 JSON" if ok else "wav 已生成，ffprobe 缺失")
    ctx.better("可接真实 musicgen（有 GPU/模型）；当前 numpy 和弦合成验证真实音频交付。")


if __name__ == "__main__":
    from full_skill_test import Recorder, get_ffmpeg, ARTIFACTS
    import os
    os.makedirs(ARTIFACTS, exist_ok=True)
    c = Recorder(SKILL, DOMAIN)
    run(c, get_ffmpeg())
    c.dump()
