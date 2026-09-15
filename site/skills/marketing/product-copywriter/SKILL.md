---
name: product-copywriter
description: "Write conversion-focused e-commerce product copy from raw product facts: framework selection (FAB / PAS / AIDA), benefit-first headlines, objection-handling section, and fact hygiene (no invented specs). Chain entry of growth-marketing — its copy feeds campaign-designer and channel-adapter directly. Use when the user asks to 写商品文案 / 详情页 / 卖点 / 产品描述 / sales copy / product description / 种草文案. Do NOT use for full campaign calendars (campaign-designer), nor per-platform reformatting of finished copy (channel-adapter)."
license: Apache-2.0
compatibility: Pure prompt-based; no runtime dependencies.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: marketing
  pattern: single-task
  tier: standard
  verified-date: "2026-09-14"
---

# Product Copywriter

链条入口。把商品事实（参数/场景/口碑）变成**能转化的文案**。核心是**框架先行**——不选框架就动笔，写出来的必然是参数罗列；参数罗列不转化。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 商品事实 | ✓ | 参数、材质、使用场景、真实口碑——只接受事实，不接受形容词 |
| 受众 | ✓（缺就问） | 谁买、为什么买、最怕什么 |
| 文案类型 | ✗ | 详情页（默认）/ 短视频口播 / 海报短文案 |

## 前置自检

商品事实里有**可验证的具体数字或材质**吗？"质量好、颜值高"不是事实，是结论——退回要事实。没事实就没证据链，文案全靠编 = 退款率预付款。

## 工作流

### 步骤 1：选框架（按受众决策阶段）

| 框架 | 结构 | 何时用 |
|------|------|--------|
| FAB | 特性→优势→利益 | 受众已知产品类，需要说服"选这家"——技术规格必须翻译成生活利益 |
| PAS | 问题→激化→解决 | 受众有痛点但没意识到解法——先扎心再给药 |
| AIDA | 注意→兴趣→欲望→行动 | 冷流量首次触达——先抓眼球 |

### 步骤 2：写四段结构（详情页骨架）

```markdown
1. 钩子标题：benefit-first，一句话说出"买了之后生活怎么变"
2. 主体：按所选框架展开，每个特性跟一条利益（FAB 纪律：特性不落单）
3. 异议处理：列出 3 个最可能的犹豫点（贵/耐用性/售后），逐个用事实回应
4. CTA：单一行动指令，不多于一个——两个 CTA 等于没有 CTA
```

### 步骤 3：事实卫生自查

- 数字、材质、认证逐条能追溯到输入事实，编造即返工
- 禁"最/第一/国家级"等极限词（广告法红线）——发现即改写为可比较表述（"比上一代薄 2mm"）
- 竞品只写自己可验证的优势，不点名贬损

### 步骤 4：链条移交

交付文案 + 所用框架标注。**接着说："文案就绪，继续调用 campaign-designer 排活动节奏，或 channel-adapter 出各平台变体"**——链条自动展开。

## 失败处置表

| 现象 | 原因 | 处置 |
|------|------|------|
| 通篇参数罗列 | 没选框架 / FAB 断层 | 每个特性强制跟"这意味着你…" |
| 文案没转化感 | 缺异议处理段 | 补 3 犹豫点逐个事实回应 |
| 像说明书不像文案 | 钩子缺失 | 重写 benefit-first 标题再进主体 |
| 有广告法风险 | 极限词/虚构认证 | 对照步骤 3 自查清单清零 |

## 参考

- [sources-and-methodology.md](references/sources-and-methodology.md) —— 直复营销框架出处与署名
