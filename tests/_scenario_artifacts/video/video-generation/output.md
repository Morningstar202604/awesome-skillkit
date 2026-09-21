[步骤 2：撰写 prompt]

读取 prompt 配方...

[工具调用] reading-file: /home/user/.cache/Superpowers/skills/video-generation/references/prompt-recipes.md

[返回] file_read: references/prompt-recipes.md 内容已读取

---

基于配方公式，为你撰写图生视频 prompt：

---

## 🎬 图生视频 Prompt

### 正向描述

> **镜头运动**：缓慢推近 + 低角度平移，模拟行人视角穿行于狭窄巷道
> **氛围**：赛博朋克式雨夜，霓虹灯在湿漉漉的柏油路面上折射出蓝紫与品红的倒影，远处高楼隐没于雨幕中，空气中弥漫着潮湿与蒸汽感
> **时长建议**：6 秒（适合展示环境氛围，若需更长叙事可选 10 秒）
> **画面比例**：16:9 横屏（电影感），或 9:16 竖屏（社交媒体风格）

**完整 prompt**：

```
A slow dolly-in combined with a low-angle lateral track, following a narrow alleyway at night during heavy rain. Neon signs in cyan, magenta, and amber cast shimmering reflections on the wet asphalt, ripples distorting the light with each raindrop impact. Distant skyscrapers fade into the misty rain curtain, creating depth and mystery. The atmosphere is moody and cinematic, evoking a cyberpunk noir aesthetic with volumetric lighting piercing through the downpour.
```

### 负面描述（Negative Prompt）

```
bright daylight, sunny, clear sky, static camera, overly saturated colors, cartoon style, low resolution, blurry, distorted faces, people walking randomly, text overlay, watermark, ugly, deformed, noisy, grainy, flat lighting, empty street without atmosphere
```

---

## 📋 生成参数建议

| 参数 | 推荐值 | 说明 |
|---|---|---|
| `aspect_ratio` | `16:9` 或 `9:16` | 根据发布平台选择 |
| `duration` | `6` 秒 | 首轮测试；若效果满意可重投 10 秒 |
| `size` | `720P` | 首版渲染，速度快；满意后再提 1080P |
| `reference_image_url` | *用户提供* | 必传首帧图片 URL |

---

需要我直接帮你提交生成任务吗？请提供：
1. **首帧图片 URL**（必需）
2. 期望的比例/时长（可选，默认 16:9 + 6 秒）