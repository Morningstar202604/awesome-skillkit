---
name: ai-baby-podcast
description: >
  Produce viral "AI baby podcast / talking baby" entertainment shorts:
  character design, script with adult-voice contrast, TTS audio, lip-sync
  generation, and platform-compliant publishing. Use when the user asks to
  做宝宝播客 / AI奶娃视频 / 会说话的宝宝 / baby podcast video /
  婴儿主播 / 搞笑AI小孩短视频, or wants meme-style talking-character shorts.
  Do NOT use for real-child footage editing, deepfakes of real people,
  or news-style content presented as factual.
license: Apache-2.0
compatibility: Uses web creation tools (image gen, TTS, lip-sync) in a browser workflow; no local install needed.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: viral-entertainment
  verified-date: "2026-08-26"
---

# AI Baby Podcast (viral talking-character shorts)

The format: a baby (or toddler) face with an ADULT voice delivering confident
opinions — the contrast IS the joke. Mature four-stage pipeline: 形象图 →
脚本 → 成人声 TTS → 口型驱动 → 剪辑发布. This skill orchestrates the whole
line and enforces the two disciplines that separate hit accounts from one-hit
wonders: character locking and platform compliance.

## Red lines — read before anything else

1. **必须声明 AI 生成**：发布时勾选平台"内容由 AI 生成"声明，视频起始画面加显式提示
   （文字高度 ≥ 画面最短边 5%、持续 ≥ 2 秒）。依据《人工智能生成合成内容标识办法》
   （2025-09-01 施行）；不标 → 平台检测后打"疑似AI"标签并限流/下架。
2. **只用纯 AI 虚构婴儿形象**。真实儿童照片即使自家孩子也不建议；绝不给真实未成年人
   做口型让"他说了没说过的话"。原因：肖像权+平台对未成年人内容的重点审查。
3. **不克隆名人声音/肖像**（明星音色、名人婴儿化）除非拿到授权——平台与法律双重风险。
4. **不做"AI幼儿专家育儿课"式误导题材**——这是监管文件点名的整治对象。

## Inputs

| Input | Required | Default | Notes |
|---|---|---|---|
| topic / 热梗 | yes | — | the baby's take |
| persona | no | 新建角色 | 新建 or 沿用既有角色卡 |
| format | no | 单人独白 | 单人 / 双人对谈 |
| target_platform | no | 抖音 | 决定画幅与标识细节 |

If topic is missing, ask ONCE:

> 请给出这期主题（蹭什么热梗/聊什么观点）。可选：用已有角色还是新建、
> 单人还是双人对话、发哪个平台（默认抖音竖屏）。

## Character lock discipline (do this once, reuse forever)

Create `character_bible.md` containing:
① 形象参考图 prompt 原文；② 参考图文件（正面 + 左右侧 + 说话中表情 共 4–6 张，
同一 seed 生成）；③ 锁定的 TTS 音色 ID 与参数；④ 3–5 条"不要"规则
（如"永远戴黑框眼镜""不换衣服颜色"）。此后每期只用参考图驱动，**永不从文字
重新生成角色**；每 10 条视频把最新一帧与参考图并排对比一次（眼距/鼻形/发际线），
发现漂移立即从原始参考图重来。原因：漂移是掉粉第一杀手，观众认的是同一张脸。

## Workflow

### Step 1: 形象图

Prompt 公式（任何文生图工具均可，含本仓 `image-generation` 技能）：

> 一个可爱婴儿坐在专业播客演播室里，戴黑框眼镜和头戴式耳机，对着嘴下方的
> 专业麦克风，正脸看镜头，嘴巴自然闭合，演播室灯光与吸音棉背景，
> 超写实照片风格，喜剧感。

Expected: 正面清晰单人脸、麦克风不遮挡嘴唇、光线均匀。失败分支：多人脸/
侧脸/手挡嘴 → 加"single character, front-facing"重生成。生成后存入角色卡。

### Step 2: 脚本（15–40 秒）

公式：`前2秒钩子（反差宣言）→ 一个具体而自信的观点 → 一句反转或金句 →
固定结尾口癖`。
Example skeleton: "关于<话题>，你们大人都想错了。<一个具体主张+理由>。
<金句反转>。我是XX，下次摇篮里接着聊。"
Rules: 口语短句（每句 ≤15 字）；观点越成人化越好——反差来自内容与脸的错位；
双人对谈则写 A/B 交替台词并标注角色。

### Step 3: TTS 配音

用任意 TTS 工具生成**成人成熟声音**（低音播音腔=经典配方；软萌童声只适合
亲子向温和内容）。语速调至 1.2–1.4 倍更贴短视频节奏。Expected: 干声 mp3/wav，
无 BGM 无混响——口型工具吃干净音频。锁定该音色写进角色卡，之后每期同一个声音。

### Step 4: 口型驱动

把 Step 1 参考图 + Step 3 干声喂给口型工具（即梦"对口型"、Hedra 等）。
先跑一句最短的台词验证口型与闭口音，再跑全片。Expected: 嘴型逐字吻合、
头部有轻微自然晃动。失败表见下。多角色对谈 = 每个角色单独生成一条，
剪辑时切镜拼接，不要同框生成。

### Step 5: 剪辑与合规发布

剪映：导入口型片段 → 识别字幕（静音刷屏党靠字幕，必须有）→ 铺 BGM 与音效
（BGM 音量低于人声 12dB 以上）→ 导出 9:16 / 1080P。
发布三件套缺一不可：① 发布页勾选"内容由 AI 生成"；② 片头显式提示字样；
③ 文案里带话题标签。Expected: 视频文件 + 已打标截图确认。

## Failure handling

| Symptom | Likely cause | Action |
|---|---|---|
| 嘴几乎不动 | 音频含糊或有BGM干扰 | 换干净干声、标点断句重试 |
| 麦克风区域变形 | 源图麦克风横跨嘴唇 | 重生成形象图，麦克风放下巴以下 |
| 长句后半段口型漂移 | 单次生成过长 | 按 2–3 句切段分别生成再剪辑 |
| 双人对话串脸 | 同框生成 | 改为分角色单拍+切镜 |
| 角色和上一期长得不一样 | 未走角色卡/重新文生图 | 回滚到锁定的参考图重跑 |
| 平台判"疑似AI"未申明 | 忘记打标 | 立即补声明并检查下条流程第5步 |

## Delivery standard

Success = 成片 mp4（9:16、带字幕、时长 15–40s）+ AI 标识已加的证据 +
本期素材归档进角色卡目录。Anything else is not done — say so plainly.

## References

- `references/character-consistency.md` — 漂移检测与多角度参考集的完整纪律；做系列账号前必读
