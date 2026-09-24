# 模型方言笔记 / Model Dialects (VERIFY BEFORE USE)

> ⚠️ **时效声明**：文生视频模型语法以**月度级**速度更新。本文件所有条目为
> 2026-09-14 网络调研快照，结构参考多家官方文档与社区指南归纳（调研过程与
> 来源分级见仓库根 docs 目录下的调研文档 VIDEO-LANDSCAPE.md）。**执行前
> 必须按「核实方法」列给出的官方文档重新确认**——这是 SKILL-STANDARD-v2
> 诫 7/诫 8 的硬要求，本文件不豁免。

## 通用六槽位（不指定模型时的默认）

```text
[subject 主体] + [action 单一动作] + [camera 景别+单运镜] + [lighting 光影] + [style 媒介质感] + [duration 时长, ratio 画幅]
```

任何模型的 prompt 都应先满足六槽位，再叠加方言特化。

**音频扩展槽位**（可选）：2026 年起原生音频已成新模型标配。目标模型支持音频时，
在六槽位外追加 `[audio 音效/对白/环境声]`；对白建议独立成块（见 Sora 条目），
不与画面描述混写。

**跨模型硬纪律**（详见 VIDEO-LANDSCAPE.md §2.2）：一镜一动作、I2V 只写运动、
相机词前置、负向 prompt 用名词式排除（写 `cartoon, blur` 不写 `no blur`）、
长叙事链式拼接不塞单 prompt。

## 各模型方言要点

### Sora 2（OpenAI）

- 时长档位固定：4/8/12/16/20s——写 prompt 前先选档位，短档位更可靠；长叙事用末帧链下一段
- 模板分块：Shot / Subject / Action / Environment / Light-palette，**对白直接写进 prompt 的对话块**（dialogue block），再补 audio bed 槽位
- lighting/palette 跨镜头可剪辑性：系列镜头保持光影描述一致，成片剪辑不跳
- 物理仿真理解较强（坠落/破碎/重力交互），物理动词可写实
- 核实方法：搜索「Sora 2 prompt guide」取 OpenAI 官方文档最新版

### Veo 3.1（Google）

- **官方五段公式**：`[Cinematography] + [Subject] + [Action] + [Context] + [Style & Ambiance]`——与六槽位同构，camera 放最前
- 时长档位仅 4/6/8s，超长叙事必须首尾帧链式拼接
- 负向 prompt 用**名词式排除**（如 `cartoon, blur, low contrast`），指令式否定（no/do not）会被当正文渲染
- 首尾帧工作流：给首帧+尾帧约束中间过程，适合连续镜头
- 核实方法：Google AI 官方文档「Veo prompt guide」

### Runway Gen-4.5

- 运动优先：先写运动与节奏，再写外观细节；时长 2-10s
- 参考图驱动：参考图质量决定输出上限；参考图自带运动线索时，反向 prompt 需大量迭代
- 核实方法：Runway 官方文档「Gen-4.5 guide」

### Seedance（字节跳动）

- 标记符号体系：`( )` 权重、`{ }` 随机分支、`【 】` 音频/对白/字幕标记——多标记语法**必须**对照官方 Prompt Guide 核实后再用
- 参考角色槽位：2.5 支持最多 50 参考图，按「参考角色纪律」声明每个参考的用途优先级
- 多镜头单 prompt：支持「阶段 + 终态」描述法，2.5 单次最长 30s + timestamp 级编辑（官方示例验证过三段式）
- 核实方法：搜索「Seedance official prompt guide」取字节跳动官方文档最新版

### Kling（快手）

- 结构感强：主体/动作/镜头描述分开写更稳；支持尾帧续接（用末帧图链下一段），拼接可拓展至约 2 分钟
- 动词写实：对具体物理动词（pouring / chewing / dancing）理解远强于抽象描述；3.0 支持 15s 智能分镜与音画同步
- 口型/音效槽位：带音频版本的能力矩阵变化快，核实「Kling AI 官方帮助文档」
- 核实方法：快手官方帮助中心 → 视频生成章节

### Wan（阿里，开源可自托管）

- T2V 短注意力：一个 prompt 只放一个清晰动作，多动作串联必崩；写材质纹理比写情节有效
- 相机关键词前置：把 `Zoom In / Pan Right` 等放 prompt 开头，响应更敏感
- I2V 只写运动：不要描述画面内容（模型看得见），只写运动/表情/环境反应
- 核实方法：Wan GitHub 仓库 README 与 prompt 指南

### 通用兜底策略

方言不确定时的安全写法：**只用通用六槽位 + 显式时长/画幅**，跳过所有特殊
标记符号。标记符号写错比不写更糟——模型可能把它们当正文渲染。

## Audit vs dialect

`prompt_audit.py` 只审通用六槽位（跨模型不变量）。方言合规靠人工对照本文件 +
官方文档核实——两层检查，缺一不可。

## Change maintenance

发现方言失效时：直接更新本文件对应条目 + 顶部快照日期，PR 走正常门禁。
