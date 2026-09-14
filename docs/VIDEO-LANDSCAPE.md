# AI 视频生成方案全景调研 / Video Landscape (VERIFY BEFORE USE)

> **目的**：为本仓 `video` 场景技能（`video-prompt-engineer`、`storyboard-designer`、
> `shot-recipe-designer`、`visual-style-anchor` 等）提供外部事实基线——主流模型的
> 能力边界、prompt 方言、生产工作流模式。所有条目为 **2026-09-14 网络调研快照**，
> 遵循 SKILL-STANDARD-v2 诫 7/诫 8：执行前必须按第六节来源清单重新核实。
>
> **来源分级**：🟢 官方文档/官网 · 🟡 第三方聚合/评测 · 🔵 社区经验/教程。
> 与本仓技能冲突时，以本仓技能的安全区设计为准，本文档只做参考不做规范。

---

## 一、方案全景矩阵

### 1.1 闭源旗舰（API/订阅制）

| 模型 | 厂商 | 时长档位 | 分辨率 | 原生音频 | 关键能力 | 来源 |
|---|---|---|---|---|---|---|
| Sora 2 | OpenAI | 4/8/12/16/20s | 最高 1080p 级 | ✅ 含 dialogue block | 物理仿真（坠落/破碎/重力）、对白直接写进 prompt、lighting/palette 跨镜头可剪辑性 | 🟡🟢 |
| Veo 3.1 | Google | 4/6/8s | 1080p+ | ✅ 音效/对白内嵌 | 官方五段公式、首尾帧工作流、负向 prompt 名词式 | 🟢 |
| Runway Gen-4.5 | Runway | 2-10s | 1080p | ✅ | 运动优先叙事、参考图驱动（参考质量决定输出上限） | 🟢 |
| Kling 3.0 | 快手 | 5/10s（可续写拼接至 ~2min） | 1080p/4K | ✅ 音画同步特征解耦 | 15s 智能分镜一键直出、多模态指令、角色定向驱动、跨时空调度 | 🟢🟡 |
| Kling 2.5 | 快手 | 5/10s | 1080p/4K | ✅ | 写实动词理解（pouring/chewing 等物理动作）、复杂流体物理、首尾帧精准 | 🟡 |
| Seedance 2.5 | 字节 | 单次最长 30s（可多轮延长） | 4K | ✅ | timestamp 级编辑、最多 50 参考图、自动分镜+专业运镜、深联动剪映 | 🟡 |
| 通义万相 Wan2.5 | 阿里 | 5-10s | 1080p | ✅ 国内首个原生音画同步 | 口型/音效自动匹配、数字人与商品展示稳、首尾帧稳定 | 🟡 |
| Hailuo H3 | MiniMax | 短档位为主 | 2K | ✅ | omni-reference 支持 12 图参考 | 🟡 |

**共性趋势**（三条都值得写进设计方法论）：
1. **时长档位化**——各家不再提供任意时长，而是固定档位；长叙事 = 链式拼接多个短档位，而非塞满一个 prompt。
2. **原生音频标配化**——2026 年新模型几乎全部内置音效/对白，prompt 需要预留音频槽位。
3. **参考图驱动一致性**——从 Veo 首尾帧到 Seedance 50 图参考，一致性的正解是给参考而非堆形容词。

### 1.2 开源自托管（本地 GPU）

| 模型家族 | 参数规模 | 显存门槛 | 许可证 | 原生音频 | 定位 |
|---|---|---|---|---|---|
| Wan 2.2（阿里） | 5B / A14B | 22-24GB / 48GB(fp8) | Apache 2.0 | ❌ | 消费级默认选择；TI2V-5B 在 RTX 4090 跑 720p/24fps；MoE 高低噪双专家 |
| HunyuanVideo 1.5（腾讯） | 8.3B | 14GB(offload)/80GB | 腾讯社区许可（≤1亿 MAU 免费商用） | ❌ | 电影感运动、prompt 跟随强；双流 transformer |
| LTX-2.3/2.5（Lightricks） | ~2B/22B | 8GB基础/32GB(FP8) | LTX License（商用需协议） | ✅ 单前向音视频联合 | 速度优先、近实时迭代、60s 长档位、多关键帧 |
| CogVideoX 1.5（智谱） | 2B/5B | 16GB+ | Apache 2.0 | ❌ | 短片入门、Diffusers 集成最顺 |
| Mochi 1（Genmo） | 10B | 24GB+ | Apache 2.0 | ❌ | 已被 Wan 2.2 全面超越，仅存档价值 |
| SkyReels V2/V3 | 14B/19B | 24GB+ | 需核对 | ❌ | Diffusion Forcing 长视频、多参考图 |
| Open-Sora | 多版本 | 24GB+ | Apache 2.0 | ❌ | 训练框架/研究平台，非生产产出 |

**选型三问**（来源 🟡，可直接复用为技能决策树素材）：显存上限？要不要原生音频？
许可证允许什么商用？——三问之后候选池通常只剩 1-2 个。

---

## 二、Prompt 方法论精要

### 2.1 各家官方规范的可迁移结构

| 方法论 | 出处 | 结构 | 本仓对应 |
|---|---|---|---|
| 五段公式 | Veo 3.1 官方 🟢 | `[Cinematography] + [Subject] + [Action] + [Context] + [Style & Ambiance]` | 与六槽位高度同构：cinematography≈camera、context+style≈lighting/style |
| 模板分块 | Sora 2 模板 🟡 | Shot / Subject / Action / Environment / Light-palette + **Dialogue block** + Audio bed | 六槽位 + 需补音频槽位（见 gap） |
| 运动优先 | Runway 官方 🟢 | 先写运动与节奏，再写外观；参考图已有运动线索时反向 prompt 需大量迭代 | `camera-vocabulary.md` 已覆盖 |
| shot grammar | 跨模型社区共识 🔵 | One framing + One camera path + One subject action + 1-2 environmental reactions + One ending state | `storyboard-designer` 的单一动作原则同源 |
| 负向 prompt | Veo 3.1 官方 🟢 | 用**名词式排除**（cartoon, blur）而非指令式（no blur / do not） | `prompt_audit.py` 不审计负向，可写进方言笔记 |

### 2.2 六条跨模型硬纪律（本文档最重要的输出）

1. **一镜一动作**：所有模型对多动作串联都会崩坏（Wan T2V 短注意力尤甚——"walks, then sits, then drinks" 必崩，"drinking coffee" 必稳）。🟡🔵
2. **I2V 只写运动**：图生视频时不要描述画面内容（模型已经看得见），只描述运动/表情/环境反应。🔵
3. **相机词前置**：多数模型对 prompt 开头的相机关键词（Zoom In / Pan Right）响应更敏感。🔵
4. **名词式负向**：负向槽位写名词列表，指令式否定常被当正文渲染。🟢
5. **物理动词写实**：Kling 系对具体动词（pouring / chewing / dancing）的理解远强于抽象描述（"eating happily"）。🟡
6. **链式拼接长叙事**：单 prompt 超过模型时长档位上限 = 事故现场；用尾帧/首尾帧链下一段。🟢🟡

### 2.3 JSON prompt 的真相

Veo 与 Sora **官方均推荐自然语言散文**，无任何官方 JSON schema。JSON 写法是社区惯例，
模型只是把它当"组织良好的文本"读。它的真实价值有三：**coverage**（空槽位肉眼可见）、
**diffability**（单变量迭代对比）、**reuse**（模板批量复用）。——来源 🟡。
本仓 `video-prompt-engineer` 的六槽位审计脚本走的正是 coverage 路线，与 JSON 惯例殊途同归。

---

## 三、生产工作流模式

### 3.1 ComfyUI 关键帧管线（叙事视频事实标准）🟡

```text
关键帧生成（IP-Adapter/LoRA 保一致性，逐帧验人脸/光照/姿势递进）
  → I2V 动画（每个关键帧排队进 Wan 2.2 / LTX-2，逐段验证分辨率/FPS/时长）
  → 拼接（FFmpeg + 转场：crossfade / motion blur）
  → QA（人脸一致性分数、色彩直方图偏差、音频同步偏移）
```

配套工程实践：
- **验证套件两段式**：生成前（模型已加载/磁盘够/prompt 非空/workflow JSON 合法）+ 生成后（文件非零/分辨率匹配/无损坏/一致性 >0.85）。
- **Seed 随机化重试**：失败段换 seed 自动重生成，而非人工重跑。
- **多实例容灾**：8188 主力 / 8189 后处理 / 8190 备援，队列停滞 5 分钟即判死。
- **Workflow JSON 模块化**：预处理、关键帧、插帧、合成拆成独立 JSON 模块，可版本管理、可积木组合。
- **ComfyUI + Remotion 组合**：生成端随机性交给 ComfyUI，剪辑/字幕/配音的确定化合成交给 Remotion——多数开源短视频 Agent 的底层架构。

### 3.2 Agent 编排模式 🟡

- **MCP 操控**：Agent（LLM）生成 Workflow JSON → MCP 调用 ComfyUI API 推理 → 取素材 → Remotion 渲染成片。
- **自适应重生成**：Agent 视觉评估产出（如结构分数 <0.8 触发重生成），把"审美判断"编进循环。
- **显存三角**：质量、速度、时长/分辨率三者不可兼得——预算约束下的取舍必须是显式决策，不是调参玄学。

---

## 四、Gap 分析（对照本仓 video 技能）

| # | 发现 | 影响 | 处置 |
|---|---|---|---|
| G-1 | `model-dialects.md` 缺 Sora 2 / Veo 3.1 / Runway Gen-4.5 / Wan 方言条目 | 方言笔记覆盖不全，恰缺三家最主流闭源 + 最大开源家族 | ✅ 本轮已补（见该文件 2026-09-14 快照） |
| G-2 | 六槽位无音频槽位，而 2026 新模型原生音频已成标配 | Sora 2 dialogue block、Veo 音效、可灵音画同步无处安放 | `model-dialects.md` 已注明"音频槽位"扩展；六槽位本体保持跨模型不变量定位不动 |
| G-3 | `storyboard-designer` 时长安全区 1-10s | 对 Veo（≤8s）/Runway（≤10s）刚好；对 Sora 2（≤20s）/Seedance（≤30s）偏保守 | **有意保留**——安全区设计优先覆盖最严格档位；长档位走链式拼接（2.2 第 6 条），不放宽 lint |
| G-4 | 无"多镜头链式拼接"专项技能 | 长叙事方法论散落在 storyboard-designer 与本文档 | 候选新技能（`sequence-chain-designer` 之类），等有真实使用反馈再立项，避免提前造轮子 |
| G-5 | 负向 prompt 名词式纪律未成文 | 写错负向是高频翻车点 | 已写入本文 2.2 第 4 条 + 方言笔记 Veo 条目 |
| G-6 | 开源模型（Wan/HunyuanVideo/LTX）无显式选型指引 | 用户问"本地跑哪个"时无仓内答案 | 本文 1.2 表格即答案；选型三问可日后纳入 prompt-engineer 扩展 |

---

## 五、行动项

**本轮已落地**：
- [x] G-1：`model-dialects.md` 补 6 家方言条目 + 快照日期更新
- [x] 本调研文档沉淀（你正在读的这份）

**后续候选**（按投入产出排序，均未承诺）：
- [ ] G-4 链式拼接技能立项（先攒 2-3 次真实长叙事需求再动手）
- [ ] `shot-recipe-designer` 配方卡补音频维度（如 beat-sync-cut 配 Sora dialogue block 变体）
- [ ] 把 2.2 六条硬纪律浓缩进 `video-prompt-engineer` SKILL.md 的审计建议文案

---

## 六、来源与核实清单

> 核实姿势：标注 🟢 的直接搜官方文档（如 "Veo 3.1 prompt guide site:ai.google"）；
> 标注 🟡 的找至少两个独立第三方交叉验证；标注 🔵 的当经验参考，必须实测。

| 主题 | 来源 | 等级 |
|---|---|---|
| Veo 3.1 五段公式/负向/首尾帧 | Google 官方 Veo prompt guide | 🟢 |
| Runway Gen-4.5 运动优先/参考图 | Runway 官方文档 | 🟢 |
| Kling 3.0 智能分镜/音画同步 | klingai.com 官网 + 头条对比文 | 🟢🟡 |
| Seedance 2.5 30s/50 参考图 | Wink 年度指南 + 头条对比文 | 🟡 |
| Sora 2 档位/dialogue block/物理 | OpenAI 官方 + 第三方聚合 | 🟡🟢 |
| 开源模型矩阵（Wan/Hunyuan/LTX/Cog） | LTX 官方博客、掘金全景表、Wink 指南三源交叉 | 🟡 |
| 方言 prompt 技巧（动词/I2V/相机词） | inrole.ai 模型指南 | 🔵 |
| ComfyUI 关键帧管线/验证套件 | claudeskills.info comfyui-expert + CSDN 解析 | 🟡 |
| JSON prompt 三价值 | 社区评测共识 | 🟡 |

*快照日期：2026-09-14 · 维护者：video-prompt-engineer 的方言笔记与本文件同步更新*
