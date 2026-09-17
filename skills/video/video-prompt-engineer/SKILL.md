---
name: video-prompt-engineer
description: "Engineer and audit text-to-video prompts across generation models: the six-slot structure (subject + action + camera + lighting + style + duration), camera-move and transition vocabulary, and per-model dialect notes with verification steps. Two modes: write a prompt from a scene description, or audit an existing prompt and report which slots are missing or contradictory. Use when the user asks to 写视频提示词 / 视频 prompt / text-to-video prompt / 提示词审计 / prompt audit / 让画面更电影感. Do NOT use for generating the video itself, nor for image-generation prompts (static-image structure differs — no motion slots)."
license: Apache-2.0
compatibility: Pure prompt-based; the bundled prompt_audit.py needs Python 3.8+ only.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: video
  pattern: single-task
  tier: standard
  verified-date: "2026-09-14"
---

# Video Prompt Engineer

写、审跨模型文生视频 prompt。核心是**六槽位结构**——模型不会读心，缺一个槽位就自由发挥一个，自由发挥就是废片来源。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 模式 | ✓ | `write`（从场景描述写 prompt）\| `audit`（审计已有 prompt） |
| 场景描述 | write ✓ | 一句话画面：主体 + 动作 + 环境 |
| 目标模型 | ✗ | 通用结构默认；指定模型（seedance/kling/veo 等）则套方言（见 references/model-dialects.md） |
| 时长 | ✗ | 默认 5s |
| 画幅 | ✗ | 默认 16:9 |
| 待审 prompt | audit ✓ | 原文粘贴 |

## 前置自检

- audit 模式：prompt 原文拿到了吗？没有就先要，不要凭记忆审计。
- write 模式：场景描述里有主体吗？「拍一个好看的镜头」这种没有主体的描述直接退回。

## 工作流

### 步骤 1（write）：按六槽位填空

```text
[主体 subject] + [动作 action] + [镜头 camera] + [光影 lighting] + [风格 style] + [时长/画幅 duration]
```

示例（可整段照抄换词）：

```text
A young woman in a black hoodie walks through a rainy neon-lit street,
slow push-in from mid shot to close-up, night exterior with cyan-orange
neon spill and wet-reflective asphalt, cinematic live-action look,
5 seconds, 9:16 vertical.
```

规则：
- 动作必须**单一且可在一个镜头内完成**（"坐下并点燃打火机"是两个动作 → 拆两个 prompt）
- 每槽位一个短语，禁止写成长句故事——prompt 是参数表不是剧本
- 数字一律显式（"5 seconds"），不写 "a few seconds"

预期：产出 prompt 含全部 6 槽位；跑 `python3 scripts/prompt_audit.py --prompt "<文本>" --mode write` 返回 6/6。
若失败：自检返回 <6/6 → 读缺失清单逐槽补词后才交付，不带着 miss 项进下一步；某槽位实在填不出（如场景描述里没有光影信息）→ 回输入清单问用户要环境/时段，不要编；动作槽写成两个动词 → 拆成两个 prompt，不许合并。

### 步骤 2（audit）：跑结构审计

```bash
python3 scripts/prompt_audit.py --prompt "<待审文本>"
```

预期：输出 JSON，含每个槽位 `hit/miss` 与缺失清单。miss 项按下方处置表补齐。
若失败：`--prompt` 传空/只有空白 → 脚本报错，回输入清单向用户要 prompt 原文；JSON 无法解析 → 确认 prompt 里的引号已转义（命令行下用单引号包裹，或把 prompt 存文件后再传）。

### 步骤 3：套模型方言（仅当指定了模型）

查 [model-dialects.md](references/model-dialects.md) 对应模型的语法差异（标记符号、参考图槽位、音频槽位）。**所有方言条目均为 2026-09 网络调研值，执行前按文档内给出的官方 prompt guide 链接核实（VERIFY BEFORE USE）**——模型语法月度级更新。

预期：prompt 已按该模型方言改写，且文档内官方核实链接已点开确认。
若失败：核实链接失效或文档缺失 → 按通用六槽位结构交付，并在交付物中注明「方言未核实」。文档里查不到用户指定的模型 → 同上按通用结构交付并注明，不要凭记忆发明该模型的语法。

### 步骤 4：交付

write 模式交付 prompt 原文 + 槽位标注版；audit 模式交付 JSON 报告 + 修复后的 prompt 对比版。
若失败：用户只想要 prompt 原文、不要槽位标注 → 交付原文即止，标注版附后备查，不因格式分歧卡住交付。

## 六槽位词典（最快查表）

| 槽位 | 常用词 |
|------|--------|
| 主体 | 身份 + 服装 + 表情：「a young woman in a black hoodie, tired eyes」 |
| 动作 | 单一动词短语：「walks slowly toward camera」「picks up a blue lighter」 |
| 镜头 | 景别 + 运镜：「extreme close-up, slow push-in」「wide establishing, static」 |
| 光影 | 时段 + 光源 + 对比：「golden hour backlight」「high-contrast noir, practical neon」 |
| 风格 | 媒介质感：「cinematic live-action」「stop-motion feel」「90s camcorder」 |
| 时长画幅 | 「5 seconds, 9:16 vertical」 |

## 失败处置表

| 现象 | 原因 | 处置 |
|------|------|------|
| 主体每帧变脸 | 缺参考图槽 / 主体描述含糊 | 加角色卡描述或模型参考图槽位；见 visual-style-anchor 技能的角色卡 |
| 动作没发生 | 动作被写成结果 | 「拿着点燃的打火机」→「ignites the lighter」（写过程不写状态）|
| 运镜乱晃 | 两个运镜叠加 | 一个 prompt 只留一个运镜动词 |
| 画面与时长不符 | 动作量超时长 | 按每秒 1 个动词砍动作 |
| 审计 6/6 但生成仍差 | 结构对、选词弱 | 把形容词换成具体名词：beautiful lighting → cyan neon spill |

## 交付标准

- write：6 槽位齐全的英文 prompt + 中文槽位对照
- audit：JSON 报告（每槽 hit/miss）+ 修复版 prompt
- 方言条目使用前已按 model-dialects.md 的核实步骤确认

## 参考

- [camera-vocabulary.md](references/camera-vocabulary.md) —— 运镜与转场词汇表（快速版）
- [cinematography-lexicon.md](references/cinematography-lexicon.md) —— 深度词库：17 种转场、动作动词空间语义、微表情表演、速度节奏、物理属性描述、各模型方言速查、迭代修复对照（写 prompt 时优先查这张）
- [model-dialects.md](references/model-dialects.md) —— 各模型语法方言与核实链接
- [sources-and-methodology.md](references/sources-and-methodology.md) —— 方法论开源出处与致谢（CC BY 4.0 署名信息）

## 链条衔接（下游建议）

本技能承接 storyboard-designer / shot-recipe-designer 的场景描述，产出六槽位 prompt 供 video-generation / image-generation 投喂；角色一致性须引用 visual-style-anchor 的身份行。建议作为 video 域 chains 的上游规划步骤。当前为游离技能，衔接仅为文字描述。
