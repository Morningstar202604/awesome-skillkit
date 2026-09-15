---
name: image-prompt-engineer
description: "Engineer text-to-image prompts from a design spec: five-segment structure (canvas + subject + composition + style anchor + text spec), photography vocabulary, text-rendering rules (quote exact strings, match length), negative terms as nouns, and per-model dialects including the text-rendering rule of thumb. Write or audit modes. Use when the user asks to 写生图 prompt / image prompt / 文生图提示词 / 让图更专业 / prompt audit 图片. Do NOT use for video prompts (video-prompt-engineer), nor for choosing canvas sizes (design-brief-interpreter already fixed them)."
license: Apache-2.0
compatibility: Pure prompt-based; no runtime dependencies.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: design
  pattern: dual-mode
  tier: standard
  verified-date: "2026-09-14"
---

# Image Prompt Engineer

从设计规格单写、审文生图 prompt。核心是**五段结构** + **文字渲染规则**——生图模型不读心，且图上文字是第一大崩坏源。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 模式 | ✓ | `write`（按规格写 prompt）\| `audit`（审已有 prompt） |
| 设计规格单 | write ✓ | 来自 design-brief-interpreter 的 7 字段规格 |
| 目标模型 | ✗ | 默认通用结构；指定则套方言（见 references/model-dialects.md） |
| 待审 prompt | audit ✓ | 原文粘贴 |

## 工作流

### 步骤 1（write）：按五段结构填空

```text
[画布 canvas 比例+尺寸] + [主体 subject 画面内容] + [构图 composition 景别+布局] + [风格锚 style 引用规格单] + [文字 text 逐字引号包裹]
```

规则（每条来自实战教训）：

- **自然语言整句**，不是关键词堆砌——"关键词念经"是 2023 年的写法，现代模型理解语法
- **精确到可复现**：写 "Kodak Portra 800 肤色调"、"Rembrandt 布光"、"50mm f/1.4 浅景深"，不写"专业摄影感"
- **不用代词**：模型分不清"它/那个人"——直接称"短发黑衣女子"、"红色轿车"
- **文字规则（最高优先级）**：要出现在图上的文字用**双引号逐字包裹**写进 prompt；新增/修改文字尽量匹配原文长度（字符数剧变会挤压版式）；改字用 "change '旧字' to '新字'" 编辑句式
- **负向约束用名词式**：`blurry, watermark, extra fingers, garbled text`——不写 "no blur"（会被当正文渲染）

### 步骤 2：套模型方言（含文字的图先查这条）

查 [model-dialects.md](references/model-dialects.md)。**头号硬规则：图上要出现可读文字（标题/标签/数据）→ 优先选文字渲染可靠模型（如 GPT Image 系），Gemini 系基本不渲染可读文字**——选错模型，prompt 写得再好都是废图。

### 步骤 3（audit）：对照五段核对

输出核对清单：每段 hit/miss + 文字是否逐字引号包裹 + 负向是否名词式。缺段按规格单补齐，交付修复前后对比。

### 步骤 4：交付与链条移交

交付 prompt 原文 + 五段标注版。**生成后立即移交 layout-spec-auditor 按设计规格审计尺寸与安全区**——链条继续，不等用户发话。

## 五段词典（最快查表）

| 段 | 常用句式 |
|----|----------|
| 画布 | "3:4 portrait, 1080x1440" |
| 主体 | "a short-black-haired woman in a black hoodie holding a book" |
| 构图 | "centered composition, generous negative space, low-angle hero shot" |
| 风格锚 | 引用规格单原文："flat editorial illustration, warm cream base, single coral accent" |
| 文字 | `bold condensed sans-serif title "AI VIDEO 2026" top-left` |

## 失败处置表

| 现象 | 原因 | 处置 |
|------|------|------|
| 图上文字乱码 | 模型不支持文字渲染 | 换文字渲染可靠的模型方言重写；或退一步：无字底图 + 后期排版 |
| 主体每张脸都不一样 | 主体描述含糊或用代词 | 写死外观特征清单；多轮编辑基于上张图改 |
| 风格漂移 | 风格锚没进 prompt | 每次都整段复制规格单 style 字段，不凭记忆 |
| 元素太挤 | 构图段缺留白声明 | 加 "generous negative space" 并砍次要元素 |
| 负向没生效 | 写成指令式 | 改名词列表 |

## 参考

- [model-dialects.md](references/model-dialects.md) —— 图像模型方言与文字渲染规则（核实链接在内）
