# Shot Recipes — 12 张完整配方卡

## Table of Contents

1. [establishing-wide 开场定调](#1-establishing-wide-开场定调)
2. [hook-pop-in 钩子镜头](#2-hook-pop-in-钩子镜头)
3. [insert-closeup 特写插入](#3-insert-closeup-特写插入)
4. [parallax-push 2.5D 视差推动](#4-parallax-push-25d-视差推动)
5. [title-card 标题卡](#5-title-card-标题卡)
6. [match-cut 匹配剪辑](#6-match-cut-匹配剪辑)
7. [reaction-cutaway 反应切出](#7-reaction-cutaway-反应切出)
8. [process-montage 流程蒙太奇](#8-process-montage-流程蒙太奇)
9. [reveal-pan 揭示横摇](#9-reveal-pan-揭示横摇)
10. [beat-sync-cut 卡点连切](#10-beat-sync-cut-卡点连切)
11. [final-frame-hold 定格收束](#11-final-frame-hold-定格收束)
12. [cta-endcard 行动号召尾板](#12-cta-endcard-行动号召尾板)

---

每张卡固定字段：**用途 / 能量 / 时长 / 运镜公式 / 生成 prompt 模板 / 常见坑**。

## 1. establishing-wide 开场定调

- **用途**：第一个镜头，交代环境与基调。能量低，给观众入戏时间。
- **时长**：3-4s
- **运镜公式**：广角定场 + 缓推（slow push-in, 5% zoom）或全静止
- **prompt 模板**：`wide establishing shot of <地点>, <时段与光源>, slow push-in, cinematic live-action, <Ns>, <ratio>`
- **坑**：推太快变成「进场景」而非「定场景」；缩放速率 ≤5%/秒。

## 2. hook-pop-in 钩子镜头

- **用途**：前 1-3 秒抓注意力，信息密度最高的一帧。
- **时长**：1-2s
- **运镜公式**：特写起幅 + 快速拉出（whip-out）或弹入（pop-in scale 0.9→1.0）
- **prompt 模板**：`extreme close-up of <焦点物>, quick pull-back reveal, high contrast, <Ns>`
- **坑**：把钩子用在信息而不是冲突上——先给「反差」再给「主体」。

## 3. insert-closeup 特写插入

- **用途**：强调关键道具/细节（剧情钩子物、数字、按钮）。
- **时长**：1-2s
- **运镜公式**：固定微距或极缓推
- **prompt 模板**：`macro insert shot of <道具>, shallow depth of field, static, <Ns>`
- **坑**：特写物与剧情无关 → 观众找意义找不到就出戏。只插「后面会用到」的东西。

## 4. parallax-push 2.5D 视差推动

- **用途**：把平面图/截图/海报变立体，产品视频主力卡。
- **时长**：3-4s
- **运镜公式**：分层位移——前景 1.2×、中景 1.0×、背景 0.8× 推近
- **prompt 模板**（供支持分层输入的工具）+ 后期说明：前景层位移 1.2×/背景 0.8×
- **坑**：层数超过 3 层会假；纯文字页先拆标题层/内容层/背景层。

## 5. title-card 标题卡

- **用途**：章节分隔、片名、呼吸口。
- **时长**：2-3s
- **运镜公式**：纯排版 + 微动效（字距扩张 / 单色扫光）
- **prompt 模板**：`minimal title card, <标题文本>, <底色 HEX>, subtle letter-spacing animation, <Ns>`
- **坑**：标题卡能量是全片最低点，放在两个高能段之间；连用两张 = 冷场。

## 6. match-cut 匹配剪辑

- **用途**：时空/主题跳转，用形状或动作相似性缝合两镜。
- **时长**：前后各 2-3s
- **运镜公式**：A 镜末帧构图 ≈ B 镜首帧构图（圆形→圆形，动作→动作）
- **prompt 模板**：A/B 两 prompt 各自独立，构图列标注「match cut pair」
- **坑**：形状相似度 60% 以下观众看不出来——宁可用叠化。

## 7. reaction-cutaway 反应切出

- **用途**：主角说话后切听者反应，给台词「落地感」。
- **时长**：1-2s
- **运镜公式**：中近景固定，微表情
- **prompt 模板**：`medium close-up of <听者>, subtle reaction, static camera, <Ns>`
- **坑**：反应比台词长 = 观众等下一个字；反应镜头 ≤ 台词镜头的 1/2 时长。

## 8. process-montage 流程蒙太奇

- **用途**：把 3-6 步流程压进 3-5s（制作过程、安装步骤）。
- **时长**：3-5s
- **运镜公式**：同机位同构图 × N 步快切，或同向擦除衔接
- **prompt 模板**：N 个同构图变体 prompt + 每段 0.8-1s
- **坑**：步骤超过 6 个就别塞了，观众数不过来——合并或砍。

## 9. reveal-pan 揭示横摇

- **用途**：从局部摇到全貌，制造「原来这么大/这么全」。
- **时长**：3-4s
- **运镜公式**：起幅遮住主体 70%，匀速横摇露出全部
- **prompt 模板**：`slow pan from <遮挡物> revealing <全貌>, steady speed, <Ns>`
- **坑**：摇速不匀 = 低级感；按「3 秒摇过画幅宽度」匀速。

## 10. beat-sync-cut 卡点连切

- **用途**：BGM 重拍上的 3-6 连切，能量顶点。
- **时长**：每切 0.5-1s × N
- **运镜公式**：构图跳变最大化的相邻画面（大→小、亮→暗）
- **prompt 模板**：N 个强对比构图 prompt；渲染前先锁 BGM BPM 再定切点
- **坑**：没 BPM 就别用这张卡——切点对不上拍子不如不切。

## 11. final-frame-hold 定格收束

- **用途**：高潮后定格 2s，给情绪留余韵，也是截封面位。
- **时长**：2s
- **运镜公式**：动作结束帧完全静止（或 slow 2% 缩放）
- **prompt 模板**：`final frame hold on <画面>, complete stillness, <Ns>`
- **坑**：定格帧要提前按「可做封面」标准构图（留标题位）。

## 12. cta-endcard 行动号召尾板

- **用途**：尾板：关注/购买/链接，平台合规排版。
- **时长**：2-3s
- **运镜公式**：静态版式 + 单元素入场（按钮/二维码淡入）
- **prompt 模板**：`end card, <主文案> + <行动语>, brand colors <HEX>, static, <Ns>`
- **坑**：CTA 文案超过一行 = 没人读完；平台违禁词先查（见 video-script-writer 的平台合规节）。

---

能量曲线自查：把 12 个镜头的能量（低/中/高）排成序列，合法形态是「波浪」，
禁止全高（观众疲劳）或全低（观众划走）。
