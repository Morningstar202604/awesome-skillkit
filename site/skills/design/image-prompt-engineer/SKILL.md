---
name: image-prompt-engineer
description: "Engineer text-to-image prompts from a design spec: five-segment structure (canvas + subject + composition + style anchor + text spec), prompt-priority ordering (position = weight), lighting and camera physics vocabulary, text-rendering rules (quote exact strings, match length), negative terms as nouns, and per-model dialects including the text-rendering rule of thumb. Write or audit modes. Use when the user asks to 写生图 prompt / image prompt / 文生图提示词 / 让图更专业 / prompt audit 图片. Do NOT use for video prompts (video-prompt-engineer), nor for choosing canvas sizes (design-brief-interpreter already fixed them)."
license: Apache-2.0
compatibility: Pure prompt-based; no runtime dependencies.
metadata:
  author: "awesome-skillkit"
  version: "2.0"
  category: design
  pattern: dual-mode
  tier: standard
  verified-date: "2026-09-22"
---

# 生图提示词工程师

从设计规格单写、审文生图 prompt。核心是**五段结构** + **文字渲染规则**——生图模型不读心，且图上文字是第一大崩坏源。

本技能只产 prompt（或审查报告），**不生成图片**：prompt 决定的是"上界"，出图质量还取决于模型能力、种子与参数。把这条先摆在前面，可以省掉后面所有"为什么照着写还是不好看"的扯皮。

## 适用决策表

| 你的处境 | 本技能的位置 | 去向 |
|----------|--------------|------|
| 有设计规格单，要写生图 prompt | ✅ write 模式 | 这里 |
| 有 prompt，怀疑有问题要审 | ✅ audit 模式 | 这里 |
| 要视频 prompt | ❌ 越界 | video-prompt-engineer |
| 画幅/尺寸还没定 | ❌ 顺序不对 | design-brief-interpreter（定画幅）→ 再回来 |
| 图已生成，要审尺寸/安全区 | ❌ 越界 | layout-spec-auditor |
| 图上要出可读文字，但不想看模型方言 | ⚠️ 必须查：选错模型 = 废图 | 步骤 2 + model-dialects.md 铁律 1 |

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 模式 | ✓ | `write`（按规格写 prompt）\| `audit`（审已有 prompt） |
| 设计规格单 | write ✓ | 来自 design-brief-interpreter 的 7 字段规格 |
| 目标模型 | ✗ | 默认通用结构；指定则套方言（见 references/model-dialects.md） |
| 待审 prompt | audit ✓ | 原文粘贴 |

缺输入时一次性问齐："请提供：① 模式（write 写新 prompt / audit 审已有 prompt）② design-brief-interpreter 的 7 字段规格单（write 必需）③ 目标模型（可选）④ 待审 prompt 原文（audit 必需）。"

## 前置自检

本技能纯 prompt 驱动：无运行时依赖、无端点、无环境变量。唯一自检点：

```bash
test -f references/model-dialects.md && echo OK
```

预期输出 `OK`；失败说明技能包不完整——通用五段结构（步骤 1）仍可用，但跳过步骤 2 的方言查询，并在交付时注明方言表缺失。**无法执行 shell 的环境直接视为通过**（技能包由本仓统一构建，方言表随包发布），不要因为无法运行这条命令而停下或向用户索要环境信息。输入不全（缺模式、或 write 缺规格单、或 audit 缺原文）→ 先问齐再 STOP，不猜。

## 暗知识（prompt 里真正决定成败的东西）

### 1. 位置即权重：不可协商的元素必须放最前

多数模型对 prompt **前部 token 的权重更高**。如果主体必须是一辆红色自行车，它不能是 prompt 里的第 8 个短语。排序纪律：**主体 > 动作 > 环境 > 光照 > 风格 > 技术参数 > 负向**。

### 2. 光照是最大的质量乘数

同一主体换光照 = 换情绪换档次。写光照四要素：**光源类型**（自然/戏剧/人工）→ **方向**（逆光/侧光/顶光）→ **性质**（软/硬/漫射）→ **色温或时段**。写不出的用 `references/visual-detail-lexicon.md` 的光照三层表查词。
（此条为多来源一致结论，也是本仓词库开篇的铁律。）

### 3. 描述，而不是评价

`beautiful` / `stunning` / `masterpiece` / `震撼` 不携带任何视觉信息——它们只表达了"我想要好看的"。替换法：把评价换成一到三个**可观察细节**（`soft rim light on hair`、`visible pores and skin texture`、`scuffed metal edges`）。
**判定标准**：另一个人拿着这条 prompt，能不能复现出相似的图？答不上就是没写清。

### 4. 相机物理撬动写实感

扩散模型学过了真实镜头的光学特征。写焦段与光圈，模型就模拟景深、畸变与颗粒：
- 人像：`shot on 85mm, f/1.8, shallow depth of field, bokeh background`
- 风光：`shot on 14mm ultra-wide, f/11 deep focus`
- 街拍：`35mm, f/5.6, film grain, Kodak Portra 400`
（一句"专业摄影感"抵不上一个焦段。）

### 5. 迭代纪律：一次只改一个变量

改 prompt 要能归因：一轮只动一个槽位（改了光照就别同时换风格），否则好看了也不知道是哪句起了作用。攒下有效的组合，形成自己的 prompt 库——复现比灵感值钱。

### 6. prompt 预算：超长会稀释权重

各来源给的长度上限口径不一（约 75–150 词），共识是**超长会把关键信息稀释掉**。本技能给区间不给精确数字：prompt 超过约 150 词时，按暗知识 1 的优先级从头砍。
**质量词封顶 2–3 个**（`8K, masterpiece, ultra-detailed` 堆到五个彼此打架，反而掉权重）。

### 7. 负向约束的三条纪律

1. **名词式列举**：`blurry, watermark, extra fingers, garbled text`——`no blur` 会被当正文渲染（指令式是负向最常见的翻车）。
2. **短而具体**：长负向列表会渗入正向语义空间、整体降质。3–8 个高价值词封顶。
3. **正向指定比负向更可靠**：想要背景清晰就写 `sharp background detail`，别指望 `no blurry background`。有独立负向字段的模型（SD 系）才把负向放独立字段，其余模型负向效力弱。

### 8. 模型选择在 prompt 之前

同一条 prompt 跨模型的结果差异，比同模型上改十遍 prompt 还大。**要出图上文字 → 先按铁律 1 选文字渲染可靠的模型族**（见 `references/model-dialects.md`）——这一步错了，prompt 写得再好都是废图。

### 9. 塑料感的解药是微细节与瑕疵

AI 图"一眼假"常因为太干净。注入真实的脏：`pores and skin texture visible`、`dust particles in the air`、`micro-scratches on the glass`、`fuzz on the wool sweater`。
（采信程度：单来源经验技法，未达多来源交叉验证门槛——按可尝试的技巧使用，不作共识主张。）

### 10. 关掉模型的"美颜"

部分模型默认加美化滤镜，会覆盖你设计的光效（把硬光自动修成柔光）。可用时用 `--style raw` 类参数抑制默认审美，让 prompt 的指令真正生效。

## 红线（硬性禁令）

1. **不用极端质量词堆砌充数**（`8K`/`masterpiece`/`超高清`/`极致细节`）：不携带视觉信息，堆多反而掉权重；用暗知识 3 的具体细节替代。
2. **不写 `no xxx` 指令式负向**（会被当正文渲染）；也不把负向列表写成小作文。
3. **不把受版权保护的风格名/角色名当交付内容**：商用交付里 `in the style of <在世艺术家>`、知名 IP 角色名有法律风险；要求风格时改写成可描述特征（画法/笔触/色彩/年代）。
4. **audit 模式不擅自改设计**：只修机制（结构缺段、引号缺失、负向句式、评价词、代词），改设计意图（换主体/换风格/换构图）必须先问用户。
5. **不承诺出图质量与文字渲染成功率**：本技能交付 prompt 文本；能否出好图取决于模型、参数与随机性（诚实声明 1、6）。

## 诚实声明

1. **本技能不生成图片**：产物是 prompt 文本（write）或审查报告（audit）。所有"最终效果"都要由生图模型兑现。
2. **`references/model-dialects.md` 是 2026-09-14 的网络调研快照**，文件顶部自带时效声明。图像模型以**月度级**速度更新——执行前必须按该文件的「核实方法」列重新确认，本技能不保证表中结论当前有效。
3. **「五段结构」是本仓的可操作化框架**，不是任何模型厂商的官方规范；其跨模型通用性来自实践归纳。
4. **负向约束的效力因模型而异**：具备独立负向字段的模型效力强；只在 prompt 里写名词式的，效力弱且可能被渲染成元素。
5. **prompt 长度上限（75–150 词）各来源口径不一**：本技能给区间不给精确阈值；原则（超长稀释）可信，数字仅作参考。
6. **文字渲染不保证**：即使选对模型族，长文本、小字号、多语言混排仍高发崩坏。稳妥做法是"无字底图 + 后期排版"兜底——把这条作为选项主动告知用户。

## 工作流

### 步骤 1（write）：按优先级排序 + 五段填空

```text
[画布 canvas 比例+尺寸] + [主体 subject 画面内容] + [构图 composition 景别+布局] + [风格锚 style 引用规格单] + [文字 text 逐字引号包裹]
```

规则（每条来自实战教训）：

- **自然语言整句**，不是关键词堆砌——"关键词念经"是 2023 年的写法，现代模型理解语法
- **精确到可复现**：写 "Kodak Portra 800 肤色调"、"Rembrandt 布光"、"50mm f/1.4 浅景深"，不写"专业摄影感"
- **不用代词**：模型分不清"它/那个人"——直接称"短发黑衣女子"、"红色轿车"
- **文字规则（最高优先级）**：要出现在图上的文字用**双引号逐字包裹**写进 prompt；新增/修改文字尽量匹配原文长度（字符数剧变会挤压版式）；改字用 "change '旧字' to '新字'" 编辑句式
- **负向约束用名词式**：`blurry, watermark, extra fingers, garbled text`——不写 "no blur"（会被当正文渲染）

预期：产出 prompt 含全部五段，主体信息在最前，图上文字已逐字双引号包裹，负向约束为短名词列表。
若失败：某段填不出（如规格单没给构图）→ 回设计规格单补齐后再写，不要自行发明；文字段写不出可读文案 → 回 design-brief-interpreter 的 text 字段取原文；负向约束里出现 "no xxx" 句式 → 改写成名词列表重出。

### 步骤 2：套模型方言（含文字的图先查这条）

查 [model-dialects.md](references/model-dialects.md)。**头号硬规则：图上要出现可读文字（标题/标签/数据）→ 优先选文字渲染可靠模型（如 GPT Image 系），Gemini 系基本不渲染可读文字**——选错模型，prompt 写得再好都是废图。

预期：已按目标模型的方言改写，且「图上要出文字」这一条硬规则已核对。
若失败：用户指定的模型与「图上要可读文字」冲突 → 先向用户说明取舍（换模型 / 无字底图后期排版），二选一后再往下走，不硬投。

### 步骤 3（audit）：对照五段核对

输出核对清单：每段 hit/miss + 文字是否逐字引号包裹 + 负向是否名词式（**并解释机制**：`no xxx` 会被当正文渲染、长清单会渗入正向语义——暗知识 7）+ **有无评价词堆砌**（**逐条点名原 prompt 里的具体短语**，如「咖啡很好喝的感觉」「专业摄影感」这类，不要只点名类别）+ **有无代词**（规则 4）。缺段按规格单补齐，交付修复前后对比。

**改写只出一版整合稿**：保留原意的全部要素（主体 / 场景 / 用途 / 照片感），只补可执行细节；**不给多风格备选方案**（「写实 vs 时尚编辑」式分流 = 擅自改设计方向，违反红线 4）。确有值得分流的选项时，在结尾另起一行列出并注明「需你拍板」，不计入交付主体。
**报告语言跟随用户提问语言**；prompt 本体可按模型方言用英文，但诊断与说明与用户同语言。

修复优先级：**选错模型（若有文字需求）> 图上文字未逐字引号 > 负向指令式 > 评价词堆砌 > 缺段 > 缺技术参数**。前两项属于"一定崩"，先修。
若失败：待审 prompt 缺规格单无从比对 → 先要规格单；用户给不出规格单 → 退化为纯结构审查（只查五段齐否、引号与名词式规则），并在报告中注明「未对照规格单」。

### 步骤 4：交付与链条移交

交付 prompt 原文 + 五段标注版。**生成后立即移交 layout-spec-auditor 按设计规格审计尺寸与安全区**——链条继续，不等用户发话。
- 预期：下游拿到的东西可逐字使用——prompt 原文可直接粘贴进生图模型，标注版每段有段名。
- 若失败：用户只想自己拿去用（不进链条）→ 交付 prompt 原文即止，标注版附后备查。

## 内置验证步骤（交付前逐条打勾）

- [ ] **五段齐全**，且顺序符合优先级（主体在最前）
- [ ] **可复现测试**：另一个人拿这条 prompt 能复现出相似构图与光照（暗知识 3）
- [ ] **文字测试**：图上文字逐字双引号包裹；长度与位置说明清楚
- [ ] **负向测试**：全部为名词式、3–8 个、有独立字段的模型已放独立字段
- [ ] **空词扫描**：无 `beautiful/masterpiece/8K/超高清/极致` 类无信息词
- [ ] **代词扫描**：无"它/这个/那个人"
- [ ] **模型核对**（含文字时）：已按方言表确认文字渲染能力，并注明方言表快照日期
- [ ]（audit 模式）逐条点名了原 prompt 的具体短语，改写仅一版整合稿（未分流多风格方案），报告语言与用户一致

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
| 负向没生效 | 写成指令式 / 无独立负向字段 | 改名词列表；有独立字段的模型放独立字段（暗知识 7） |
| 图"一眼 AI" | 太干净、缺微细节 | 注入瑕疵与纹理（暗知识 9） |
| 改了很多处，效果变差说不清原因 | 多变量同改 | 回滚到上一版，一次只改一个槽位（暗知识 5） |
| 硬光被"修"成柔光 | 模型默认美化覆盖 | 用 `--style raw` 类参数抑制默认审美（暗知识 10） |
| 用户要求"某艺术家风格"商用 | 版权风险 | 改写成可描述特征（笔触/色彩/年代），并说明原因（红线 3） |

## 交付标准

- 产物（write）：prompt 原文一段 + 五段标注版（每段标 `canvas/subject/composition/style/text`）。
- 产物（audit）：核对清单（每段 hit/miss，逐条点名原 prompt 的具体问题短语）+ **一版整合改写**（保留原意、不擅自换设计方向）+ 修复前后对比 + 修复优先级说明；报告语言与用户提问语言一致。
- 保存位置：直接输出在对话中（本技能不写文件）。
- 完整性验证：五段齐全且顺序符合优先级；图上文字逐字双引号包裹；负向约束为短名词列表（无 "no xxx" 句式）；无评价词堆砌与代词；style 段与规格单 style 字段逐字一致。
- 含文字需求时：注明所用模型族的文字渲染核对结论与方言表快照日期。

## 参考

- [model-dialects.md](references/model-dialects.md) —— 图像模型方言与文字渲染规则（含时效声明与来源分级；执行前须按"核实方法"重新确认）
- [visual-detail-lexicon.md](references/visual-detail-lexicon.md) —— 深度词库：三层光照、构图、焦段透视性格、材质微细节、色彩方案、静态图动势词、场景模板（写 prompt 时优先查这张）
- [sources-and-methodology.md](references/sources-and-methodology.md) —— 暗知识 1–10 的来源清单、交叉验证矩阵（≥2 来源才写入）与未采信内容（拒绝营销话术）
