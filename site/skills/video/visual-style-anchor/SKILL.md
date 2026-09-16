---
name: visual-style-anchor
description: "Create a reusable visual style anchor for a video or image project: one-page style guide locking color palette, lighting scheme, materials, era, and medium texture — plus a character consistency card (identity line, wardrobe, props, forbidden changes) that keeps every generated shot on-model. Use when the user asks to 定视觉风格 / 风格设定 / 角色设定 / 保持角色一致 / 人物不跑脸 / style guide / character sheet / 视觉统一 before batch generation. Do NOT use for writing per-shot prompts (use video-prompt-engineer), nor for generating the images themselves."
license: Apache-2.0
compatibility: Pure prompt-based design skill; no scripts, no API keys.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: video
  pattern: single-task
  tier: standard
  verified-date: "2026-09-14"
---

# 视觉风格锚

产出两个可复用资产：**风格锚**（style-anchor.md，全片视觉 DNA）+ **角色一致性卡**（character-card.md，角色不跑脸的合同）。批量生成前先锁风格，是全片视觉统一的最便宜手段——逐张返工比先写一页锚定文档贵十倍。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 项目一句话 | ✓ | 「雨夜便利店霓虹短片」这种粒度 |
| 参考（文字/图链） | 可选 | 「像《银翼杀手》的雨夜」级别的参照即可 |
| 角色数量 | ✗ | 0 = 只出风格锚；≥1 = 每角色一张一致性卡 |
| 画幅/平台 | ✗ | 默认 16:9 |

缺失时一次性问齐：「请提供：① 项目一句话 ② 角色数量（默认 0，只出风格锚）。其余我将采用默认值。」

## 前置自检

- 本项目是否已有旧的 `style-anchor.md` / `character-card-*.md`？有 → 在旧文件上
  更新，不要另起炉灶——风格锚一变，已生成的镜头全部作废。
- 参考文件在盘：`test -f references/style-anchor-formula.md`（展开公式时要用），
  缺失 → STOP 并回报仓库不完整。

## 工作流

### 步骤 1：按五槽位公式定风格锚

```markdown
# Style Anchor: <项目名>

## 色彩板 palette
主色 #0E1A2B（夜空蓝黑）/ 强调 #FF6B35（霓虹橙）/ 辅助 #7FD1C9（青）
规则：全片 ≤3 主色；强调色只给焦点对象。

## 光线 lighting
夜外景：practical neon（画内光源）为主，青橙对比，高光允许溢出。

## 材质 materials
湿面反光沥青、磨砂塑料、玻璃橱窗。禁止：纯平色块、低饱和哑光。

## 时代 era
现代都市，无年代标记物冲突（全片禁: CRT 电视、胶片颗粒）。

## 媒介质感 medium
cinematic live-action, 35mm depth-of-field feel, 轻微手持呼吸感。
```

预期：五槽位全填，色彩板给了 HEX 值。
若失败：用户只给情绪词（「高级感」）→ 用参考物换算：「高级感 = 低饱和 + 大面积暗部 + 单强调色」，向用户确认换算结果再定稿。

### 步骤 2：产出角色一致性卡（如需）

```markdown
# Character Card: 小雨

## 身份行 identity line（可直接嵌进任何 prompt 的单句）
a young woman, short black bob hair, tired but sharp eyes, black oversized hoodie, white sneakers

## 三视图清单 turnaround
正面 / 3/4 侧面 / 背面（有图像生成工具时先出这三张定稿，后续所有镜头引用）

## 锁定 wardrobe & props
黑色连帽衫（帽子常垂）、白鞋、蓝色打火机（剧情道具）

## 禁改 forbidden
发型、发色、瞳色、身高比例 —— 任何 prompt 不得添加眼镜/帽子/换装
（如剧情需要变装 → 停止，回到本卡开新变体卡 variant-B，禁止临时改）
```

预期：身份行 ≤25 词（太长塞不进每个 prompt）。

### 步骤 3：写复用说明

在两个文件末尾各加一段「如何使用」：
- style-anchor → 每个 prompt 的 style 槽位整段引用
- character-card 的身份行 → 每个含角色 prompt 的 subject 槽位原样嵌入，禁止改写措辞（改一个词，模型就可能换脸）

### 步骤 4：交付核对

| 核对项 | 通过标准 |
|--------|----------|
| 五槽位齐全 | 色彩有 HEX、光线有光源类型 |
| 身份行可用 | ≤25 词、无否定句（「not wearing hat」模型会生成 hat）|
| 禁改清单存在 | 每角色 ≥3 条 |

## 失败处置表

| 现象 | 原因 | 处置 |
|------|------|------|
| 生成仍跑脸 | prompt 里改写了身份行措辞 | 身份行必须复制粘贴，禁止同义改写 |
| 色彩板跨镜头漂移 | style 槽位没每 prompt 都带 | style 槽位是必填槽，见 video-prompt-engineer 的六槽位 |
| 用户中途加新角色 | 卡没预留变体机制 | 开 variant 卡，并更新连续性约束表（storyboard-designer 产物）|
| 情绪词无法落地 | 「高级感」类抽象词 | 强制走参考物换算并向用户确认 |

## 交付标准

- `style-anchor.md` 一页（≤60 行），五槽位齐全
- `character-card-<名字>.md` 每角色一份，身份行 + 禁改清单齐全
- 两个文件都含「如何使用」段落

## 参考

- [style-anchor-formula.md](references/style-anchor-formula.md) —— 风格锚五槽位的展开公式与更多示例
- [character-consistency.md](references/character-consistency.md) —— 角色一致性的完整纪律（含 seed/音色锁定、漂移审计）
- [sources-and-methodology.md](references/sources-and-methodology.md) —— 方法论出处（含本仓 ai-baby-podcast 的既有实践与开源生态致谢）

## 链条衔接（下游建议）

本技能是视频域生产链（production chains）的上游「视觉规划」技能。建议编排顺序：
visual-style-anchor → storyboard-designer → shot-recipe-designer → video-prompt-engineer → video-script-writer，之后再接入 video 域已登记的 talking_character / meme 链条（video-voice-synth → video-lip-sync → video-editor → video-subtitles → video-thumbnail）。
当前 skill_chains.json 的 video 域 skills 列表未登记本技能（游离技能）；以上衔接仅为文字描述，无跨目录硬链接引用。
