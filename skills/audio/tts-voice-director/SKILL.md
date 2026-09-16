---
name: tts-voice-director
description: "Direct text-to-speech synthesis for a produced script: cast voices per character from a voice catalog (Kokoro/DIA/Qwen3-TTS families), set per-segment synthesis parameters (speed, stability), plan stitching (per-segment render + ffmpeg concat + crossfade), and voice-design via descriptive prompts on supported models. Reads the script from podcast-producer, hands rendered audio plan to episode-publisher. Use when the user asks to 选声音 / TTS 配音 / 语音合成 / voice casting / 让声音自然 / 多角色配音. Do NOT use for writing or linting the script (podcast-producer), nor for publishing metadata (episode-publisher)."
license: Apache-2.0
compatibility: Pure prompt-based; references only — no bundled synthesis binary (calls user-side TTS per catalog).
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: audio
  pattern: single-task
  tier: standard
  verified-date: "2026-09-14"
---

# TTS Voice Director

给已过 lint 的脚本做**声音执导**：选声、定参、排拼接。核心判断是**角色-声音匹配表**——声音选错，脚本再好也是播报腔。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 脚本 | ✓ | podcast-producer 的产出（已过 script_lint） |
| 形态 | ✓ | 单人 / 双人对话 / 有声书 |
| TTS 引擎 | ✗ | 默认 Kokoro 系（本地免费）；指定则按目录适配 |
| 情绪要求 | ✗ | 每段的情绪标签（沉稳/兴奋/低语） |

缺输入时一次性问齐："请提供：① 已过 lint 的脚本 ② 形态（单人/双人对话/有声书）③ TTS 引擎（缺省 Kokoro 系）④ 特殊情绪要求（可选）。"

## 前置自检

本技能自身无运行时依赖（纯规划，不捆绑合成引擎）。自检点：

```bash
test -f references/voice-catalog.md && echo CATALOG-OK
```

- `CATALOG-OK` 必须出现；失败说明技能包不完整，STOP 并提示重装。
- **引擎在位性是用户侧状态**，本技能不打包引擎、也没有统一探测命令：执行合成前按 [voice-catalog.md](references/voice-catalog.md) 的"核实方法"（各引擎官方页/HuggingFace 模型卡）确认所选引擎可用，再动第一段合成。规划阶段不被此阻塞。

## 工作流

### 步骤 1：查声音目录选角

打开 [voice-catalog.md](references/voice-catalog.md)，按「角色气质 → 声音 ID」映射表选声。纪律：

- **先定角色气质再挑声音**：温暖主持人 / 权威解说 / 轻松搭档 / 有声书旁白——气质词来自脚本大纲的人物设定，不是听到哪个顺耳用哪个
- **双人对话必须声线差异最大化**：男女搭配或不同音区，同性别选不同 ID 且试听对比
- **同节目全季固定卡司**：声音 ID 写进节目配置，换季不换声

### 步骤 2：定合成参数

- **语速**：中文口播 1.0 基准，解说类可 1.05-1.1，沉思类 0.95
- **停顿靠标点**：脚本里的句号/破折号就是全部停顿控制；合成参数里没有"情感"滑块时，改写文案比调参数有效
- **voice design（仅支持的模型）**：Qwen3-TTS 类支持描述式生成音色（"图书馆里的低沉男声"），零样本克隆需 ≥3 秒样本并留授权记录

### 步骤 3：排拼接计划

```text
intro 音乐（fade in 2s）
  → seg-01（host 声）→ 500ms 间隔 → seg-02（guest 声）→ ...
outro 音乐（fade out，匹配 intro 风格）
```

- **逐段合成再拼接**（ffmpeg concat `-c copy` 不重编码，秒级完成）
- 对话段相邻行 crossfade 300-500ms 消接缝
- 音乐垫底只铺 intro/outro 与段间，人声段不压床（除非音量 -18dB 以下）

### 步骤 4：链条移交

交付合成计划（角色-段落-参数表）+ 拼接清单。**接着说："合成计划已就绪，执行后调用 episode-publisher 产发布件"**——链条收口。
- 预期：episode-publisher 拿到的计划每段有声源与参数，拼接清单可直接喂 ffmpeg。
- 若失败：合成后发现某段音色不合适 → 只重合成该段再拼接（逐段合成的意义），不推倒整条时间线。

## 交付标准

- 产物：合成计划表（段落 × 声音 ID × 语速/参数）+ 拼接清单（含 crossfade 时长与音乐段落）。
- 保存位置：直接输出在对话中；实际音频由执行侧产出，本技能不落盘音频。
- 完整性验证：脚本每个分段都分配到声音与参数；双人对话两声线 ID 不同；全季声音 ID 与节目配置一致。

## 失败处置表

| 现象 | 原因 | 处置 |
|------|------|------|
| 声音出戏 | 气质与角色不匹配 | 回目录按气质重选，双人做声线差异对比 |
| 语速赶/拖 | 语速参数一刀切 | 按段定速：解说 1.05+ / 沉思 0.95 |
| 接缝爆音 | 硬拼接 | 相邻段 crossfade 300-500ms |
| 专有名词读错 | 合成器词典缺词 | 错词记录进 shownotes 术语表；反复错就改写谐音字并同步人工校对 |
| 情绪平 | 模型无情感参数 | 回到脚本改文案——节奏在标点和句子长短里，不在参数里 |

## 参考

- [voice-catalog.md](references/voice-catalog.md) —— 声音目录：各家 TTS 的声音 ID、气质映射与核实方法
