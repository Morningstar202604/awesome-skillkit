---
name: visual-style-anchor
description: "Create a reusable visual style anchor for a video or image project: one-page style guide locking color palette, lighting scheme, materials, era, and medium texture — plus a character consistency card (identity line, wardrobe, props, forbidden changes) that keeps every generated shot on-model. Use when the user asks to 定视觉风格 / 风格设定 / 角色设定 / 保持角色一致 / 人物不跑脸 / style guide / character sheet / 视觉统一 before batch generation. Do NOT use for writing per-shot prompts (use video-prompt-engineer), nor for generating the images themselves."
license: Apache-2.0
compatibility: Pure prompt-based design skill; no scripts, no API keys.
metadata:
  author: "awesome-skillkit"
  version: "2.0"
  category: video
  pattern: single-task
  tier: standard
  verified-date: "2026-09-21"
---

# 视觉风格锚

产出两个可复用资产：**风格锚**（style-anchor.md，全片视觉 DNA）+ **角色一致性卡**（character-card.md，角色不跑脸的合同）。批量生成前先锁风格，是全片视觉统一的最便宜手段——逐张返工比先写一页锚定文档贵十倍。

## 适用决策表（先判断，再锚定）

| 你的场景 | 用不用本技能 | 怎么用 |
|---|---|---|
| 批量生成镜头/图片前，要先统一视觉 | 用 | 全流程：风格锚 +（如需）角色卡 |
| 单张一次性图，不复用 | 轻量用 | 只出风格锚，跳过角色卡与复用说明 |
| 项目已有旧风格锚 | 在旧文件上改 | **禁止另起炉灶**——锚一变，已生成镜头全部作废 |
| 只想生成一张图不等风格 | 别用 | 直接用图像生成工具，本技能是批量前的规划步骤 |
| 每镜头的 prompt 写法 | 别用 | 归 video-prompt-engineer（本技能是它的上游） |

## 领域暗知识（锚风格前必须懂的四件事）

**1. 青橙对比不是审美时尚，是生理学——但它已经是俗套。** 调色界共识（filmit.io 调色师长文及多家调色教程交叉印证）：人类肤色无论人种都落在光谱的橙色区间，青色（teal）是橙的互补色——把暗部推青、肤色保暖，人脸就会从背景里"跳"出来，这是不用合成技巧就能造纵深的物理机制。但它 2007 年前后（《变形金刚》+ 数字摄影机 + DaVinci Resolve LUT 工作流）被好莱坞工业化，**2012 年成为标准，2020 年成为俗套**——观众看两条调色教程就能认出它。落到风格锚上的纪律：选"电影感"时必须知道它是俗套起点；区分度来自题材与光线结构（画内光源/practical light），不是把暗部抹青。真正锁进锚里的是对比结构与光源类型，而不是某个流行色调本身。

**2. 调色的第一原则：先校正、后创作、留余量。** 调色师工作流（多源一致）：先做技术校正（白平衡/曝光）再做创意调色，顺序颠倒会把色偏放大而不是藏住；LUT 实际应用时透明度收到 **50-70%**（预置 LUT 为了预览效果都推得很猛）；**只推暗部、不动中间调**，肤色才有救；饱和度上限盯住肤色——皮肤发绿或发品红 = 病态感。落到风格锚上：色彩板规则一栏要写清"哪些允许溢出（高光）、哪些设上限（肤色/强调色饱和度）"，这就是锚里的"饱和度纪律"。

**3. 色彩情绪有行业温度字典，别自造对应关系。** 调色叙事的通用词典（多源一致）：暖调（琥珀/金/橙）= 怀旧、亲密、舒适；冷调（青/蓝/灰）= 距离、紧张、忧郁；高饱和 + 黑场上浮 = 商业感/明快；低饱和 + 压实黑场 = 电影感/阴郁。互补色（青橙、红绿、黄紫）制造张力，邻近色制造柔和统一（《月光男孩》式霓虹），单色系制造压抑氛围（《黑客帝国》绿）。风格锚的"色彩情绪"槽位从这本字典取词，用户给的"高级感/氛围感"按参考物换算成字典词——不要发明"灰色 = 高级"这类私人对应。

**4. 一致性比漂亮值钱——跨镜头稳定是专业分水岭。** 调色界的老话：观众最先注意到的是不自然的肤色，而**跨镜头肤色不一致 = 立刻露 amateur 底**。风格锚的全部价值就在"锁定"二字：批量生成时漂移的不是审美，是熵——每张图各美各的，合在一起就不是一部片。所以锚是合同不是参考：五槽位逐镜头原样引用，改一个词就是重开项目。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 项目一句话 | ✓ | 「雨夜便利店霓虹短片」这种粒度 |
| 参考（文字/图链） | 可选 | 「像《银翼杀手》的雨夜」级别的参照即可 |
| 角色数量 | ✗ | 0 = 只出风格锚；≥1 = 每角色一张一致性卡 |
| 画幅/平台 | ✗ | 默认 16:9 |

缺失时一次性问齐：「请提供：① 项目一句话 ② 角色数量（默认 0，只出风格锚）。其余我将采用默认值。」

## 红线（硬性禁令，不可协商）

1. 已有旧锚不另起炉灶：风格锚中途变更 = 已生成镜头全部作废；确需变更 → 明确告知返工范围并获用户确认。
2. 身份行禁止否定句：`not wearing hat` 会生成 hat——否定式一律改写为肯定式或移进「禁改 forbidden」段。
3. 身份行禁止同义改写：每个含角色 prompt 的 subject 槽位原样复制粘贴，改一个词模型就可能换脸。
4. 情绪词必须换算落盘：「高级感」类抽象词不进锚，参考物换算成可判定描述并经用户确认。
5. 色彩板 ≤3 主色 + 强调色唯一：强调色只给焦点对象（60-30-10 稀缺性法则）；禁止"到处点缀"。

## 前置自检

- 本项目是否已有旧的 `style-anchor.md` / `character-card-*.md`？有 → 在旧文件上
  更新，不要另起炉灶——风格锚一变，已生成的镜头全部作废（红线 1）。
- 参考文件在盘：`test -f references/style-anchor-formula.md`（展开公式时要用），
  缺失 → STOP 并回报仓库不完整。

## 工作流

### 步骤 1：按五槽位公式定风格锚

```markdown
# Style Anchor: <项目名>

## 色彩板 palette
主色 #0E1A2B（夜空蓝黑）/ 强调 #FF6B35（霓虹橙）/ 辅助 #7FD1C9（青）
规则：全片 ≤3 主色；强调色只给焦点对象；肤色饱和度设上限（暗知识 2）。

## 光线 lighting
夜外景：practical neon（画内光源）为主，青橙对比结构，高光允许溢出。

## 材质 materials
湿面反光沥青、磨砂塑料、玻璃橱窗。禁止：纯平色块、低饱和哑光。

## 时代 era
现代都市，无年代标记物冲突（全片禁: CRT 电视、胶片颗粒）。

## 媒介质感 medium
cinematic live-action, 35mm depth-of-field feel, 轻微手持呼吸感。
```

预期：五槽位全填，色彩板给了 HEX 值，色彩板规则含饱和度纪律。
若失败：用户只给情绪词（「高级感」）→ 用暗知识 3 的温度字典换算：「高级感 = 低饱和 + 大面积暗部 + 单强调色」，向用户确认换算结果再定稿（红线 4）。

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

预期：身份行 ≤25 词（太长塞不进每个 prompt）、无否定句（红线 2）。
若失败：身份行超 25 词 → 砍掉非辨识度特征（服装细节留到 wardrobe 段），只保留定脸要素；身份行里出现否定句 → 改写为肯定式或移进「禁改 forbidden」段；用户给不出参考图 → 仍产出文字版身份行，并注明「参考图未定稿，漂移风险自担」。

### 步骤 3：写复用说明

在两个文件末尾各加一段「如何使用」：
- style-anchor → 每个 prompt 的 style 槽位整段引用
- character-card 的身份行 → 每个含角色 prompt 的 subject 槽位原样嵌入，禁止改写措辞（改一个词，模型就可能换脸——红线 3）

预期：两个文件的「如何使用」段落都已写入，且明确写了「原样引用/禁止改写」。
若失败：用户的项目不需要复用（单张图一次性）→ 省略本步，并在交付标准里注明「非复用场景，未附复用说明」。

### 步骤 4：交付核对

| 核对项 | 通过标准 |
|--------|----------|
| 五槽位齐全 | 色彩有 HEX、光线有光源类型、色彩板规则含饱和度纪律 |
| 身份行可用 | ≤25 词、无否定句（「not wearing hat」模型会生成 hat）|
| 禁改清单存在 | 每角色 ≥3 条 |
| 情绪词已换算 | 锚内不存在「高级感」类抽象词（红线 4）|

预期：四项全部通过，方可交付。
若失败：任一项不通过 → 回对应步骤（五槽位缺 → 回步骤 1；身份行不合格 → 回步骤 2；禁改清单不足 3 条 → 补足后重核；情绪词残留 → 回暗知识 3 换算），不带着不合格项交付。

## 失败处置表

| 现象 | 原因 | 处置 |
|---|---|---|
| 生成仍跑脸 | prompt 里改写了身份行措辞 | 身份行必须复制粘贴，禁止同义改写（红线 3） |
| 色彩板跨镜头漂移 | style 槽位没每 prompt 都带 | style 槽位是必填槽，见 video-prompt-engineer 的六槽位 |
| 用户中途加新角色 | 卡没预留变体机制 | 开 variant 卡，并更新连续性约束表（storyboard-designer 产物）|
| 情绪词无法落地 | 「高级感」类抽象词 | 强制走暗知识 3 温度字典换算并向用户确认 |
| 用户点名"就要青橙大片感" | 触碰俗套风险（暗知识 1） | 不拒绝但说破：2020 年起已是俗套；改写为"青橙对比结构 + 题材化光源"，区分度靠光线与题材 |
| 肤色跨镜头不一致 | 没锁饱和度纪律 | 回步骤 1 补饱和度上限规则；批量重生成受影响镜头 |
| 用户中途要求改锚 | 触碰红线 1 | 列出作废镜头清单与返工成本，确认后开新锚 |

## 交付标准

- `style-anchor.md` 一页（≤60 行），五槽位齐全，色彩板规则含饱和度纪律
- `character-card-<名字>.md` 每角色一份，身份行 + 禁改清单齐全
- 两个文件都含「如何使用」段落
- 锚内无未换算的情绪词（红线 4 全查）

## 参考

- [style-anchor-formula.md](references/style-anchor-formula.md) —— 风格锚五槽位的展开公式与更多示例
- [character-consistency.md](references/character-consistency.md) —— 角色一致性的完整纪律（含 seed/音色锁定、漂移审计）
- [sources-and-methodology.md](references/sources-and-methodology.md) —— 方法论出处（含本仓 ai-baby-podcast 的既有实践与开源生态致谢）与 v2.0 调查来源（调色师工作流/青橙演化史/色彩温度词典）

## 链条衔接（下游建议）

本技能是视频域生产链（production chains）的上游「视觉规划」技能。建议编排顺序：
visual-style-anchor → storyboard-designer → shot-recipe-designer → video-prompt-engineer → video-script-writer，之后再接入 video 域已登记的 talking_character / meme 链条（video-voice-synth → video-lip-sync → video-editor → video-subtitles → video-thumbnail）。
当前 skill_chains.json 的 video 域 skills 列表未登记本技能（游离技能）；以上衔接仅为文字描述，无跨目录硬链接引用。
