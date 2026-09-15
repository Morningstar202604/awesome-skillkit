---
name: storyboard-designer
description: "Design scene-by-scene storyboards for short videos: beat sheet with timings, per-scene prompt pairs (image board + video-generation prompt), and a continuity constraint table covering character, wardrobe, props, location, and aspect ratio. Use when the user asks to 分镜设计 / 画分镜 / 做 storyboard / 场景拆解 / 出镜头表 / 把脚本拆成分镜 before video generation. Do NOT use for generating the video or images themselves (outputs are prompt scripts — feed them to video-generation / image-generation), nor for writing dialogue (use video-script-writer)."
license: Apache-2.0
compatibility: Pure prompt-based design skill; the bundled scene_lint.py needs Python 3.8+ only.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: video
  pattern: single-task
  tier: standard
  verified-date: "2026-09-14"
---

# Storyboard Designer

把一段视频概念拆成可执行的逐场景分镜包：节拍表 + 每场景「图像板 prompt + 视频 prompt」成对产出 + 连续性约束表。分镜是设计与生成的合同——合同写得越死，生成越不跑偏。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 视频概念 / 脚本 | ✅ | 一段话或 video-script-writer 产出的脚本 |
| 总时长 | ✅ | 秒；缺失时按平台默认（抖音/Reels ≤30s，B站/YouTube 30-60s） |
| 画幅 | ❌ | 16:9（横屏/B站）\| 9:16（竖屏/抖音）\| 1:1；默认 16:9 |
| 角色设定 | 可选 | 已有 character sheet 则必须随附（进入连续性表） |
| 视觉风格锚 | 可选 | 已有 style anchor 则全场景锁定 |
| 输出语言 | ❌ | prompt 脚本语言，默认跟随用户 |

缺失时一次性问齐：「请提供：① 视频概念 ② 总时长 ③ 画幅（默认 16:9）。其余我将采用默认值。」

## 前置自检

- 概念是否可在总时长内讲完？场景数 ≈ 总时长 ÷ 单场景时长（默认 5s/场景）。
- 输出目录 `storyboard/` 是否已存在同名 scene 文件？有则先询问是否覆盖（防误删已确认稿）。

## 工作流

### 步骤 1：产出节拍表（beat sheet）

先不写 prompt，先把节奏定死。每行一个节拍：

```markdown
| # | 时间 | 节拍功能 | 画面一句话 | 声音 |
|---|------|----------|-----------|------|
| 1 | 0-3s | 钩子 hook | 雨夜霓虹街，镜头推向伞下人 | 雨声渐入 |
```

节拍功能只用五种：`hook 钩子` / `setup 铺垫` / `beat 展开` / `twist 反转` / `cta 收束`。30s 视频典型节奏 = hook 3s + setup 5s + beat×3 + twist 5s + cta 2s。
预期：节拍表时长合计 = 总时长，否则回到本步重切。
若失败：概念讲不完 → 建议「砍概念」或「提时长」，二选一问用户，不要自行加时长。

### 步骤 2：逐场景产出 prompt 对

每个场景输出两个文件（编号两位数字，从 01 起）：

- `scene-01.md`（存放在输出目录 `storyboard/` 下）—— 场景 prompt 脚本（结构见下节公式）
- 场景的图像板描述段（若用户有图像生成工具，按此段生成 scene-01.png 存入同目录；本技能只产 prompt，不产图——禁止用代码/SVG 画假分镜图充数）

### 步骤 3：填连续性约束表

```markdown
| 维度 | 锁定值 | 出处场景 |
|------|--------|----------|
| 角色 | 小雨，短发黑衣女性 | 全部 |
| 服装 | 黑色连帽衫、白鞋 | scene-01 定 |
| 关键道具 | 蓝色打火机 | scene-02 出现 → scene-04 复现 |
| 场景 | 雨夜便利店门口 | scene-01/02 |
| 画幅 | 9:16 | 全部 |
| 调色 | 青橙对比、夜景高光溢出 | 全部 |
```

每个维度必须有「出处场景」——后面场景只能引用已锁定的值，不允许 scene-05 突然换装。
预期：连续性表先于场景 prompt 定稿；任何场景 prompt 与表冲突即重写该场景。

### 步骤 4：跑 lint 校验

```bash
python3 scripts/scene_lint.py storyboard/
```
预期：`ALL OK`。非 0 退出按输出逐条修。

### 步骤 5：交付

按「交付标准」核对后，向用户输出：节拍表 + 连续性表 + 场景文件清单。

## 场景文件结构公式（scene-XX.md）

```markdown
# Scene NN —— <一句话>
- 时长: <Ns>  画幅: <ratio>  景别: <远/全/中/近/特>
- 画面: <主体> + <动作> + <环境>（一句完整中文/英文，≤40 字）
- 运镜: <推/拉/摇/移/跟/固定> + <速度>
- 光影: <时段 + 光源 + 对比度>
- 声音: <对白/TTS 文本 | 环境 SFX | BGM 情绪>
- 视频 prompt: <可直接投喂生成模型的英文 prompt，含时长与画幅>
- 转场: 出场转场 <硬切/J-cut/匹配剪辑/叠化>
- 连续性: 引用连续性表的行 <原样复制值>
```

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| 单场景时长 | 3-8s | 生成模型单段普遍 ≤10s，超长必须切场景 |
| 场景数 | 时长÷5s | 30s → 5-7 场景 |
| 景别梯度 | 全片至少 3 种 | 全片同一景别 = 视觉催眠，lint 不查但审查必打回 |

## 失败处置表

| 现象 | 原因 | 处置 |
|------|------|------|
| 节拍合计 ≠ 总时长 | 切分粗糙 | 按 1s 粒度重切，先定 hook 和 cta 两端 |
| 场景间角色变脸 | 连续性表后补 | 推倒：先定表再写场景 |
| prompt 超模型时长上限 | 单场景 >10s | 一分为二，插入匹配剪辑转场 |
| 用户只要分镜图不要 prompt | 理解偏差 | 仍产出 .md（prompt 是图的放大器），说明用途 |

## 交付标准

- `storyboard/scene-01.md ... scene-NN.md`，NN 连号无跳号
- 每个文件含上述 9 个字段，缺一即不合格
- 节拍表 + 连续性表随交付（存为输出目录下的 `beat-sheet.md` 与 `continuity.md`）
- `scene_lint.py` 退出码 0

## 参考

- [sources-and-methodology.md](references/sources-and-methodology.md) —— 分镜方法论的开源出处与致谢（必读，理解为何这样设计）
- 同包的 `shot-recipe-designer` 技能（注意：跨技能禁止链接引用，此处仅文字提及）——需要更细的运镜/转场设计时单独调用它

## 链条衔接（下游建议）
本技能承接 video-script-writer 的脚本输出，产出分镜包供 video-generation / image-generation 使用；需要更细运镜/转场时再调用 shot-recipe-designer，需要锁定角色一致时引用 visual-style-anchor 的角色卡。建议在 video 域 chains 中以「上游规划」步骤接入 talking_character / meme 链。当前为游离技能，衔接仅为文字描述。
