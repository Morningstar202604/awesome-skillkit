为了将「在笔记本上跑本地大模型的赛博感封面」工程化，我需要补充几个关键设计决策。请先提供以下信息，或让我给出一个**推荐默认版**：

### 缺少的输入
1. **目标模型**：Midjourney v6? DALL-E 3? Stable Diffusion XL?（不同模型的负向词语法和参数完全不同）
2. **画面焦点**：笔记本屏幕特写？人物与笔记本同框？纯概念图？
3. **赛博感侧重**：硬核技术风（代码流、电路板）？霓虹都市风（粉蓝紫霓虹）？暗黑极客风（绿黑终端）？

---

### 推荐默认版（Midjourney v6 方言）
假设：**屏幕特写 + 硬核技术风 + 英文 UI 文字渲染**

#### Prompt 原文（直接粘贴）
```
3:4 vertical format, 1080x1440 --ar 3:4 --stylize 250 --v 6.0
[canvas] Vertical 3:4 portrait, 1080x1440 resolution
[subject] Close-up of a matte black gaming laptop on a dark wooden desk, screen glowing with cyan and magenta terminal code cascading, RGB keyboard backlit in purple, condensation droplets on the screen surface, shallow depth of field
[composition] Centered composition, rule of thirds on screen content, generous negative space at top for title, low-angle hero shot
[style] Cyberpunk technical aesthetic, cold blue and hot magenta color grading, volumetric lighting, 8k resolution, photorealistic, Unreal Engine 5 render style
[text] Bold condensed sans-serif title "LOCAL LLM" top-center, subtitle "RUNNING LOCALLY" bottom-center, both in bright cyan with subtle glow effect
[negative] blurry, watermark, extra fingers, garbled text, overexposed, plastic look, cheap costume
```

#### 五段标注版
| 段落 | 内容 |
|------|------|
| **Canvas** | `3:4 vertical format, 1080x1440` + `--ar 3:4 --stylize 250 --v 6.0` |
| **Subject** | `matte black gaming laptop, screen glowing with cyan and magenta terminal code, RGB keyboard backlit in purple, condensation droplets` |
| **Composition** | `Centered composition, generous negative space at top, low-angle hero shot` |
| **Style** | `Cyberpunk technical aesthetic, cold blue and hot magenta color grading, volumetric lighting, 8k resolution, photorealistic, Unreal Engine 5 render style` |
| **Text** | `Bold condensed sans-serif title "LOCAL LLM" top-center, subtitle "RUNNING LOCALLY" bottom-center, bright cyan with subtle glow effect` |

---

### 若改用 DALL-E 3（自然语言版）
```
A vertical poster (3:4 ratio) featuring a close-up of a black gaming laptop on a dark desk. The screen displays cascading cyan and magenta terminal code. The keyboard is backlit in purple with condensation droplets on the screen. Use cyberpunk aesthetics with cold blue and hot magenta color grading. Include bold condensed sans-serif text at the top reading "LOCAL LLM" and at the bottom reading "RUNNING LOCALLY" in bright cyan with a subtle glow. Photorealistic style, 8k resolution, volumetric lighting.
Negative prompts: blurry, watermark, extra fingers, garbled text, overexposed, plastic look.
```

---

### 若改用 Stable Diffusion XL（标签式）
```
(masterpiece, best quality, ultra-detailed), 3:4 portrait, close-up of matte black gaming laptop, screen glowing with cyan magenta terminal code, RGB keyboard purple backlight, condensation droplets on screen, dark wooden desk, cyberpunk aesthetic, cold blue hot magenta color grading, volumetric lighting, 8k, photorealistic, unreal engine 5 render

Negative: (worst quality, low quality:1.4), blurry, watermark, extra fingers, garbled text, overexposed, plastic, cheap, bad anatomy

Parameters: --ar 3:4 --s 250 --c 7 --niji 6
```

---

### 下一步建议
1. **选择模型** → 我可按你的目标模型微调方言（如 SDXL 的 LoRA 推荐、MJ 的 `--style raw` 等）
2. **生成后审计** → 把生成的图发给我，我按 [layout-spec-auditor](references/layout-spec-auditor.md) 审尺寸、安全区、文字可读性
3. **迭代优化** → 告诉我哪段不满意（如"代码不够密集""赛博感太弱"），我定位修改对应段落

请确认目标模型或提供上述缺失输入，我输出最终版。