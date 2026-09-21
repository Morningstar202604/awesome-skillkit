让我先读取 prompt 配方，再为你定制图生视频的 prompt。

```bash
cat references/prompt-recipes.md
```

现在基于"雨夜霓虹街道"首帧，为你撰写一段完整的图生视频 prompt：

---

**🎬 图生视频 Prompt（雨夜霓虹街道）**

```
电影感雨夜都市街道，湿润的柏油路面反射着五彩霓虹灯的光晕——粉红、青色、暖黄交织流淌；细雨如丝持续飘落，偶尔有车辆驶过溅起水花；远处行人模糊轮廓撑伞掠过，背影融入薄雾般的蒸汽中；镜头缓慢向前推进，略带手持晃动，营造沉浸与疏离并存的氛围；色调偏冷蓝紫，高光处点缀霓虹暖色，整体情绪孤独、迷幻、赛博朋克风；低角度平视，景深虚化背景，突出前景水洼倒影；画面细腻，4K电影质感，无噪点，无水印。
```

---

**📐 参数建议**

| 参数 | 值 |
|---|---|
| aspect_ratio | `16:9` 横屏（电影感首选）；若发抖音/Reels 改 `9:16` |
| duration | `10` 秒（给足空间展现镜头推进与氛围沉淀） |
| size | `1080P`（霓虹光影细节需要更高码率） |
| reference_image_url | 提供你的首帧图 |

---

**🚫 负面提示（如网关支持）**

```
blurry, low quality, watermark, text, logo, overexposed, distorted faces, morphing, flickering, unnatural motion, static frame, cartoon, anime, oversaturated, noise, grainy
```

---

现在确认一下你的使用方式——是否已有首帧图 URL？以及期望的比例和时长？确认后我直接调用网关提交任务。