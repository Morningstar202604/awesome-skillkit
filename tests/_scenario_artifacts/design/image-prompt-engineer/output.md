我先用**通用五段结构**把这一需求工程化成可直接用的 prompt，同时给出负面词、参数建议与模型选型。因为没拿到上游 `design-brief-interpreter` 的 7 字段规格单，风格/色彩/画幅我会做**工程化默认值**并在交付时标出假设；你若之后补上规格单，我立刻按规格单 style 字段逐字替换并重出。

## 假设清单（写 prompt 前必须确认）
1. **画幅**：3:4 竖版封面（封面最常用）；若需横版或方形请告知。
2. **文字**：封面**需要**可读标题吗？若需要，标题内容是什么（我将逐字双引号包裹并匹配原长）。
3. **目标生图模型**：未指定，默认通用结构 + 参数建议见下；**图上若要有可读文字**，请优先选文字渲染可靠的模型（见步骤 2）。
4. **风格锚**：未提供规格单，我用行业通用「赛博朋克×笔记本硬件」视觉约定作为 style 锚点，输出会整段保留以便你后期与真实规格单对齐。

## 交付 1：prompt 原文（可直接粘贴）

```text
3:4 portrait, 1080x1440, a compact laptop running a local large language model, dark industrial desk with ambient RGB lighting, glowing circuit patterns and neural network visualizations rendered on the laptop screen, steam or heat haze rising subtly from the chassis, shallow depth of field, neon cyan and magenta rim lights against a charcoal background, volumetric fog with light rays filtering through, cinematic color grading with cool blue tones and warm accent highlights, sharp focus on the laptop screen with bokeh in the foreground and background, "LOCAL LLM" bold condensed sans-serif title top-left, "ON DEVICE" smaller subtitle below, subtle negative-space area on the right third for logo placement
```

### 负面词（名词式列表）
```text
blurry, watermark, extra fingers, garbled text, poorly rendered text, overexposed, underexposed, chromatic aberration, noisy, low detail, flat lighting, cluttered composition, distorted perspective, bad anatomy, low resolution, jpeg artifacts, over-saturated, low contrast, plastic-looking materials, generic product photography, cluttered background, unreadable screen content, excessive lens flare, ghosting
```

## 交付 2：五段标注版

- **canvas**：`3:4 portrait, 1080x1440`
- **subject**：`a compact laptop running a local large language model, dark industrial desk with ambient RGB lighting, glowing circuit patterns and neural network visualizations rendered on the laptop screen, steam or heat haze rising subtly from the chassis`
- **composition**：`shallow depth of field, neon cyan and magenta rim lights against a charcoal background, volumetric fog with light rays filtering through, cinematic color grading with cool blue tones and warm accent highlights, sharp focus on the laptop screen with bokeh in the foreground and background, "LOCAL LLM" bold condensed sans-serif title top-left, "ON DEVICE" smaller subtitle below, subtle negative-space area on the right third for logo placement`
- **style**：`dark industrial sci-fi product photography, cyberpunk neon accent palette, cinematic lighting, high-detail hardware rendering`（这是通用风格锚；若有规格单请把 style 字段整段粘贴进来替换此行）
- **text**：`bold condensed sans-serif title "LOCAL LLM" top-left`、`smaller subtitle "ON DEVICE" below`

## 交付 3：参数建议（按主流工具）

| 工具 | 推荐参数 |
|---|---|
| Midjourney v6 | `--ar 3:4 --v 6 --style raw --s 250 --q 2` |
| Stable Diffusion XL | steps 30–40, CFG 5–7, sampler DPM++ 2M Karras, hires fix 1.5×, denoise 0.4 |
| DALL·E 3 | 默认精度即可；如需文字更准，提示里强调 `"LOCAL LLM"` 和 `"ON DEVICE"` 并保持单行 |
| Flux / SD3 系 | steps 20–30, CFG 3.5–5；文字渲染较好但仍建议单行、大写、无连字符 |

## 步骤 2 前置硬规则（图上要可读文字）
> **文本渲染是生图第一大崩坏源。** 若你的封面**必须有可读文字**（标题/标签/数据），优先选文字渲染可靠的模型方言（如 GPT Image 系、Midjourney v6、SD3/Flux 中等）。Gemini 系基本不渲染可读文字——选错模型，prompt 写得再好也是废图。

你现在有两个选项（二选一，别硬投）：
1. **换模型**：告诉我你用哪个模型，我按 [model-dialects.md](references/model-dialects.md) 的方言改写并给出该模型专属参数。
2. **无字底图 + 后期排版**：把 text 段从 prompt 里移除，生成干净底图后在 Figma/AE/PS 里叠字；这样能避开所有文字崩坏风险。

## 步骤 4：链条移交
我会在你回复后（或你直接说“继续”）把成品 prompt 再移交 `layout-spec-auditor` 做尺寸与安全区审计，确保文字区、留白区、裁切区都落在封面规范的硬边界内。

---

**下一步请你选/给**：
- A）确认画幅与是否保留文字（以及文字内容）
- B）指定目标模型（Midjourney / SDXL / DALL·E 3 / Flux / 其他）
- C）若上游有 design-brief-interpreter 的 7 字段规格单，直接粘贴，我按规格单 style 字段逐字替换并重新出 prompt

我现在按默认值交付了可用版本；等你选 A/B/C 我再精细化。