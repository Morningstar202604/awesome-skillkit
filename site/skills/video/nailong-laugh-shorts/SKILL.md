---
name: nailong-laugh-shorts
description: >
  Produce "大笑奶龙"-style laughing dragon meme videos: generate the chubby
  yellow dragon character image, animate belly-laugh actions or swap actions
  from human footage, add processed giggle audio, batch skin variants, and
  publish with probability-bait captions. Use when the user asks to 做奶龙视频 /
  大笑奶龙 / 捧腹奶龙 / 奶龙表情包成精 / 魔性小龙搞笑视频 /
  make a nailong meme video. Do NOT use for harassing specific real persons,
  or political/factual disinformation contexts.
license: Apache-2.0
compatibility: Uses web AI tools (text-to-image, image-to-video, action transfer); no local install needed.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: viral-entertainment
  verified-date: "2026-08-26"
---

# Nailong Laugh Shorts ("大笑奶龙" production manual)

Risk note (one line, then we work): 公开发布使用该商业 IP 形象属未授权使用，
非盈利个人号现实后果通常是限流/下架/账号处罚而非诉讼，商用则必被追责——
自行权衡；发布时勾选"内容由 AI 生成"能明显降低处置概率。

The look that makes people laugh, in order of importance:
①头小身大的扭曲比例 ②仰天捧腹的抖动 ③高饱和明黄 ④呆萌与癫狂的表情反差。

## Inputs

| Input | Required | Default | Notes |
|---|---|---|---|
| pipeline | no | A | A=表情包成精（图→视频）；B=真人动作套壳 |
| skin/theme | no | 原味黄 | 节日/职业/变色等变体主题 |
| episode_count | no | `1` | 系列化建议一次 ≥5 条 |

Ask ONCE only if user gave nothing at all:

> 要哪种做法？A：生成一张捧腹大笑形象让它动起来（简单快）；
> B：拿真人魔性动作视频换成这个形象（更还原梗的扭曲感）。
> 可选：做几期、要不要换装系列。

## Character description library (copy-paste prompts)

Base body (official-ish look):

> 一只圆滚滚的黄色卡通小恐龙，大大的白色椭圆肚皮，短小的四肢和尾巴，
> 呆萌的大眼睛，Q 版 3D 卡通渲染，高饱和明黄色，纯色背景，全身正面。

Laughing variant (the meme look):

> 同一只黄色小恐龙仰天捧腹大笑，头向后仰，两只短手抱着肚子，
> 肚皮剧烈抖动，眼睛笑成两条缝，嘴张到最大，身体比例夸张——
> 头小肚子极大，动态模糊的抖动感。

Mutated proportions (the "奶蛙" distortion that makes it funnier):

> 同一角色但比例刻意失调：头部缩小、身体拉长放大，四肢细短乱蹬，
> 五官挤在脸下半部，扭曲滑稽，橡皮质感抖动。

Skin matrix ideas for series: 黄金圣衣版 / 西装上班版 / 春节红灯笼版 /
西瓜皮版 / 深夜emo关灯版。每张皮肤 = base prompt + 一句皮肤描述。

## Pipeline A: 表情包成精（最快出片）

### Step 1: 生成静态大笑图

用任意文生图工具跑上面的 laughing variant prompt。
Expected: 单角色、正面或微侧、肚子占比大、无多余肢体。
失败分支：多角色/肢体崩坏 → 加 "single character, simple pose" 重生成。

### Step 2: 图生视频

把图喂给图生视频工具（即梦/可灵等），动作指令：

> 角色保持位置不变，仰天大笑，肚子剧烈抖动弹跳，身体前后摇摆，
> 循环动画。

Expected: 3–5 秒无缝循环感素材。失败分支：动作僵硬 → 改指令强调
"rubber-hose wobble, exaggerated squash and stretch" 再抽卡 1–2 次。

### Step 3: 配笑声与字幕

笑声制作：自己对着手机录一段大笑 → 变声器处理（升调 20–30% + 轻微机械感
+ 按四四拍断句），剪出 3–8 秒可循环版本。**不要直接搬运别人视频里的原声**
——平台查重会判搬运限流，自制同款效果才是自己的资产。
剪辑：开头 0.5 秒内笑声炸响 → 视频循环 2–3 遍 → 大字标题压屏。

## Pipeline B: 真人动作套壳（更还原原梗的扭曲感）

### Step 1: 动作源

找一段魔性真人动作（军体拳、社会摇、广场舞、摔跤倒地）。自己拍最稳；
用网络素材注意只取动作参考、不保留任何人脸画面。

### Step 2: 动作迁移

用支持视频生视频/动作迁移的工具（即梦、可灵等）：参考图用 Step-A1 的
形象图 + 动作视频作驱动。Expected: 角色复刻动作且比例被 AI 拉歪——
**这种失控感正是原梗好笑的核心，别修它**。
失败分支：完全不像原动作 → 换轮廓更简单的动作重跑；太像正常动画不搞笑 →
prompt 加 "distorted proportions, head shrinking, belly expanding"。

### Step 3–4: 同 Pipeline A 的 Step 3，然后进入系列化。

## Series formula (hook-and-body batching)

一个身体壳 × N 张皮肤 × 固定文案模板 = 一晚上五条存货：

| 模板 | 示例 |
|---|---|
| 开光式 | 《恭喜你刷到了大笑奶龙》＋"刷到的都是天选之人" |
| 稀有概率 | "金色奶龙，出现概率仅 0.01%，见者好运" |
| 对话梗 | 两只同款对喊"我是奶龙！""我才是奶龙！" |
| 反差日常 | 上班版/上课版/干饭版各一条 |

发布：勾选"内容由 AI 生成"；标题带 #奶龙 类话题标签获取流量池。

## Failure handling

| Symptom | Likely cause | Action |
|---|---|---|
| 图出来像青蛙/蜥蜴不像胖龙 | 白肚皮没写进 prompt | 补 "big white oval belly" 重生成 |
| 视频里肚子不抖 | 动作指令太平淡 | 强调 shake/jiggle/wobble 三连词重抽 |
| 笑声尴尬不洗脑 | 无节奏处理 | 四四拍断句 + 二次变声器处理 |
| 平台判搬运 | 用了他人原声/素材 | 全部自制：自录笑声、自己拍动作源 |
| 被判疑似AI未申明 | 漏勾声明 | 补勾，检查下次清单 |

## Delivery standard

Success = 成片 mp4（9:16、开头即笑声、字幕齐全）+ 所用形象图/prompt 存档
（做系列必须归档，保证每期同一张脸）+ 已勾选 AI 声明的截图确认。
Anything else is not done — say so plainly.
