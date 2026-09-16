# 电影感词库：转场 · 动作 · 表演 · 节奏（cinematography-lexicon）

> 写视频 prompt 时按槽位查这张表。词条 = 英文术语（生成模型方言）+ 中文对齐 + 效果 + 何时用。
> **铁律**：一个镜头槽位只放一个运镜动词；动作动词要带方向和身体部位；模糊词（moves / acts / performs）一律替换为具体动词。
> 快速版见 [camera-vocabulary.md](camera-vocabulary.md)，本表是深度版。

## 一、转场词库（15+ 种，衔接两镜）

| 英文 | 中文 | 效果与情绪 | 何时用 | prompt 示例片段 |
|------|------|-----------|--------|----------------|
| hard cut | 硬切 | 干脆、无加工感 | 默认衔接；同场景节奏推进 | `hard cut to the kitchen scene` |
| smash cut | 猛切 | 巨大反差冲击（响→静、亮→暗） | 惊吓点、反转、节奏爆点 | `smash cut from the loud concert to silent empty street` |
| match cut | 匹配剪辑 | 形状/动作/构图相似跳切，产生隐喻 | 章节转场、时间跨度大跳 | `match cut: the spinning coin becomes the rotating planet` |
| match on action | 动作接动作 | 跨镜头延续同一动作，丝滑不跳 | 追逐、开门、拿起物品 | `match on action as her hand reaches the door handle` |
| J-cut | 声音先行 | 下一场的声音先进来，听觉引导视觉 | 对话转场、悬念铺垫 | `J-cut: her voice starts over the previous night-city shot` |
| L-cut | 声音延续 | 上一场声音拖到下一画面 | 对话余韵、旁白过渡 | `L-cut: his narration continues over the sunrise shots` |
| dissolve / crossfade | 叠化（≤0.5s） | 时间流逝、思绪过渡 | 蒙太奇、回忆 | `slow dissolve from childhood photo to the same street today` |
| whip pan transition | 甩镜转场 | 高速横摇模糊衔接，动感强烈 | 动作片、快节奏 vlog | `whip pan transition, motion blur, lands on the new scene` |
| invisible cut | 隐形剪辑 | 用黑场/遮挡物藏住剪辑点 | 一镜到底伪像 | `the subject walks past the camera, blocking the frame — invisible cut` |
| jump cut | 跳切 | 同机位时间跳跃，生硬但有意 | vlog 时间压缩、焦躁感 | `jump cut series, same framing, three outfits` |
| cutaway | 切出 | 插入相关细节镜头再切回 | 反应、伏笔、缓解节奏 | `cutaway to the ticking clock, then back to his face` |
| insert shot | 插入镜头 | 道具/局部特写强调 | 关键物件交代 | `insert shot: the letter, wax seal breaking` |
| flash frame | 闪帧 | 单帧白/红闪入，紧张不安 | 高能段落、悬疑 | `subtle flash frames of white between cuts` |
| contrast cut | 反差切 | 情绪/色彩急转（暖→冷） | 叙事转折 | `contrast cut from warm sunset to cold blue interior` |
| audio bridge | 声桥 | 音乐跨场不断，缝合成整体 | 混剪、多场景串联 | `music continues across the cut as an audio bridge` |
| seamless FPV fly-through | 无缝穿越飞行 | FPV 一镜飞过多个场景 | 场景漫游、炫技开场 | `continuous hyperspeed FPV flight through the glacial canyon into the cloudscape` |
| morph transition | 形变过渡 | 同主体形态渐变 | 慎用（易假）；风格化短片 | `seamless morph: the young tree grows into the old oak` |

> 组合拳：`smash cut + audio bridge`（狠切但音乐不断）是短视频 hook 到正片的常用接法。

## 二、动作动词表（按空间语义选词，避免模糊动词）

动作动词是 Gen-3 类模型杠杆最高的槽位——不同动词被解释成不同的空间行为。

| 意图 | 用这些动词 | 别用这些 |
|------|-----------|---------|
| 朝镜头来 | `approaches` / `advances` / `walks toward the camera` | comes, moves |
| 背镜头去 | `recedes` / `walks away` / `turns and departs` | leaves, exits |
| 横向穿画 | `crosses frame left to right` / `glides sideways` | walks, moves |
| 身体微动 | `shifts weight` / `breathes visibly` / `looks around` | acts, performs |
| 环境动态 | `rain falls in sheets` / `smoke drifts` / `light flickers` | environment moves |
| 面部微表情 | `eyebrows furrow` / `jaw tightens` / `gaze shifts away` | expresses, reacts |
| 手部动作 | `fingers tap the table twice` / `grip tightens on the railing` | gestures |

**公式**：`身体部位 + 具体动词 + 方向/次数/幅度`。
- 差：`a man is walking`
- 好：`a man strides toward the camera with purpose, coat flaring with each step`
- 差：`she reacts to the news`
- 好：`she freezes, her eyes widen, the cup pauses halfway to her lips`

## 三、表演与微表情细节（让角色"活"而非"动"）

| 英文短语 | 中文 | 传递的情绪 |
|----------|------|-----------|
| `eyes widen, then narrow` | 瞪大→眯起 | 惊讶转怀疑 |
| `swallows hard` | 用力吞咽 | 强忍恐惧 |
| `shoulders drop` | 肩膀垮下 | 失落、泄气 |
| `exhales slowly through the nose` | 鼻息缓出 | 压抑的愤怒/释然 |
| `a half-smile tugs at the corner of her mouth` | 嘴角勾起半个笑 | 暧昧、自嘲 |
| `grip tightens, knuckles whiten` | 攥紧，指节发白 | 忍耐 |
| `steals a glance` | 偷瞄 | 心虚、暗恋 |
| `chin lifts a fraction` | 下巴微抬 | 对抗、傲慢 |
| `hands keep busy, folding the map again and again` | 手反复折地图 | 焦虑转移 |

> 每个镜头只给 1-2 个微表情；AI 视频同一镜头塞 3 个以上表情会崩脸。

## 四、速度与节奏词（motion 槽位）

| 英文 | 中文 | 效果 | 何时用 |
|------|------|------|--------|
| `dynamic motion` | 强动感 | 全画面明显运动 | 广告、开场 |
| `slow motion` | 慢动作 | 情绪放大、细节凝视 | 高光时刻 |
| `hyperspeed` | 极速 | 时空压缩、炫技 | 穿越蒙太奇 |
| `timelapse` | 延时 | 时间流逝（云/车流/天色） | 交代时间 |
| `subtle camera drift` | 微漂移 | 几乎不动但活着 | 产品图动画、氛围镜 |
| `locked-off, no movement` | 锁死不动 | 全稳 | 不确定就用它 |
| `--motion 2`（Runway 档位 1-6） | 运动量档 | 2=克制，4=明确，6=狂野 | 迭代修复用 |
| `over 5 seconds` | 时长锚定 | 把动作钉在具体秒数 | 防止 AI 抢节奏 |

## 五、运动类型词（Runway 官方 movement types，画面整体的"变形方式"）

`grows`（生长）· `emerges`（浮现）· `explodes`（爆开）· `ascends`（升腾）· `undulates`（波浪起伏）· `warps`（扭曲）· `transforms`（变形）· `ripples`（涟漪）· `shatters`（碎裂）· `unfolds`（展开）· `vortex`（涡旋）

> 这组词适合抽象/风格化内容（片头、转场素材、MV），不适合写实叙事。

## 六、物理属性描述法（可灵/写实模型强项）

物理质感要写"材质在力下的行为"，而非只写名词：

- 雨：`heavy rain falling in visible sheets`（成片的雨幕）而非 `rainy`
- 布：`loose silk fabric rippling in the breeze`（丝绸随风起浪）
- 烟：`thick smoke slowly expanding, curling at the edges`（边缘打卷）
- 水：`water splashing, droplets catching the light`（水珠反光）
- 发：`hair flowing in the wind, strands crossing her face`（发丝扫脸）
- 火：`flames licking upward, embers drifting`（火舌上舔，火星漂移）

## 七、各模型方言速查（同一个镜头，不同模型说法不同）

| 模型 | 结构偏好 | 关键差异 |
|------|---------|---------|
| **Veo 3** | 五段式：核心场景→视觉细节→运动镜头→音频→风格参数；支持 JSON 字段（shot/subject/action/setting/camera/lens/lighting/color_grade/audio/dialogue） | 唯一可靠生成对白的模型；audio 槽位要写实音而非配乐 |
| **Runway Gen-3** | `[camera movement]: [establishing scene]. [additional details].` | 运动 Brush 可圈定动区；迭代修复（先构图→修光→修动作）；`--motion` 档位 |
| **Sora** | 电影分镜式自然语言 | 吃胶片引用（`Shot on 35mm film, warm grain`）；一镜一个主动作；时间指令（`transitioning from clear sky to storm clouds`）；文字会变形、手别特写 |
| **可灵 Kling** | 物理 + 主体细节优先 | 水布发火物理最强；中式内容（古建/街景）表现好；主体要写发色/服装/姿态 |
| **即梦/海螺** | 中文 prompt 直写 | 中文成语和口语句直接可用；先给中文版再补英文关键词 |

## 八、迭代修复对照表（哪坏了改哪个槽）

| 症状 | 修改动作 |
|------|---------|
| 太静、像幻灯片 | 加 `dynamic motion` 或升 `--motion` 档；给环境加动词（flickers / drifts） |
| 乱晃、看晕 | 降 `--motion`；改 `subtle camera drift` 或 `static, locked-off` |
| 主体没动只有镜头动 | 把运动从 camera 槽移到 subject 槽（`she turns her head`） |
| 动作太僵 | 换动词：`walks` → `strides` / `saunters`；加 `natural momentum, hesitant start` |
| 下一镜忘了上一镜 | 迭代 prompt 里加 `Previous generation achieved [X]; preserve [X]` |
| 文字乱码 | 别指望画面内文字；文字用后期贴片 |

## 九、负面清单（写了必崩的）

- 画面内可读文字（字母变形）——除 Runway 官方文字卡示例外一律后期
- 手部特写（多指/畸形）
- 一镜多个同时事件（视觉混乱）——一镜一主动作
- 超过 10s 的角色一致性——拆镜 + 首帧参考图
- `a person does something interesting` 这类抽象形容——AI 不懂 "interesting"，只懂动词和身体
