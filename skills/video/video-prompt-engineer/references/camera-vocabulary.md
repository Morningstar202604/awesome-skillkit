# 运镜与转场词汇表 / Camera & Transition Vocabulary

> 写 prompt 的镜头槽位时查这张表。英文词是生成模型的常用方言（各模型通用性较高），
> 中文是对齐概念。**运镜动词一次只用一个**——「slow push-in and orbit」会让模型乱晃。

## 一、景别（static framing）

| 中文 | 英文 | 用途 |
|------|------|------|
| 大远景 | extreme wide shot | 环境、孤独感 |
| 远景/定场 | wide establishing shot | 开场定调 |
| 全景 | full shot | 人物全身 + 环境 |
| 中景 | medium shot | 对话、动作主体 |
| 中近景 | medium close-up | 采访、反应 |
| 特写 | close-up | 情绪、面部 |
| 大特写/微距 | extreme close-up / macro | 道具、细节、眼睛 |

## 二、运镜（camera movement）——一次一个动词

| 中文 | 英文 | prompt 短语 | 备注 |
|------|------|-------------|------|
| 推 | push in / dolly in | `slow push-in` | 速度给档：slow / steady / fast |
| 拉 | pull back / dolly out | `quick pull-back reveal` | 拉出=揭示，常配 hook |
| 摇 | pan（水平）/ tilt（垂直） | `slow pan to the right` | 匀速，3s 摇过画幅宽 |
| 移 | tracking / dolly | `tracking shot alongside the subject` | 跟主体同速 |
| 跟 | follow | `follow shot from behind` | 背跟=代入感 |
| 升降 | crane up / down | `crane up revealing the city` | 大场面揭示 |
| 环绕 | orbit / arc | `slow orbit around the product` | 产品展示主力 |
| 手持 | handheld | `subtle handheld shake` | 纪实感；AI 生成易糊 |
| 固定 | static / locked-off | `static, locked-off camera` | 最稳，不确定就用它 |

## 三、转场词汇（衔接两镜）

| 中文 | 英文 | 适用 |
|------|------|------|
| 硬切 | hard cut | 默认；同场景内部 |
| 叠化 | dissolve / crossfade ≤0.5s | 时间流逝、情绪转换 |
| 匹配剪辑 | match cut | 形状/动作相似跳转 |
| J-cut / L-cut | audio leads / trails | 声音先行/延续，对话场景 |
| 擦除 | wipe（同向） | 流程蒙太奇步骤衔接 |
| 闪白/闪黑 | flash to white / cut to black | 高能段落终结 |
| 匹配叠加 | seamless morph | 同主体状态变化（慎用，易假） |

## 四、光影风格词（lighting 槽位）

| 概念 | 英文短语 |
|------|----------|
| 画内光源 | practical lights (neon, lamp, screen glow) |
| 黄金时刻 | golden hour backlight |
| 蓝调时刻 | blue hour twilight |
| 高对比黑白 | high-contrast noir |
| 柔光 | soft diffused light, overcast |
| 轮廓光 | rim light separation |
| 霓虹溢出 | neon spill, wet reflections |

## 五、媒介质感词（style 槽位）

`cinematic live-action` / `35mm film look` / `90s camcorder footage` /
`stop-motion feel` / `anime cel style` / `product-commercial gloss` /
`documentary handheld` —— 按项目风格锚（visual-style-anchor 产物）整段引用，不要现场发明。
