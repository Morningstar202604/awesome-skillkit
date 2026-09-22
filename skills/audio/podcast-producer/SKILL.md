---
name: podcast-producer
description: "Produce a podcast episode script from a topic or a document: hook-first outline, segment structure with target durations, two-voice dialogue or single-voice narration, and a shownotes draft. Hard rule: spoken words only — no stage directions, no [pause] markers, TTS reads everything verbatim. Chain entry of audio-studio; hands the script to tts-voice-director. Use when the user asks to 做播客 / 写播客脚本 / podcast 脚本 / 音频节目 / 把文章转成播客 / NotebookLM 式音频. Do NOT use for voice selection or synthesis parameters (tts-voice-director), nor for publishing metadata (episode-publisher)."
license: Apache-2.0
compatibility: Pure prompt-based; the bundled script_lint.py needs Python 3.8+ only.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: audio
  pattern: single-task
  tier: standard
  verified-date: "2026-09-14"
---

# Podcast Producer

链条入口。把选题（或一篇文档）变成**可以直接喂给 TTS 的分段脚本**。核心纪律只有一条但极硬：**纯口播词——TTS 会把你写的一切原样读出来**，`[停顿]`、"（笑）"、舞台指示全会变成节目内容。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 选题或文档 | ✓ | "聊聊 AI 视频这一年" 或直接贴一篇文章 |
| 形态 | ✗ | 单人口播（默认）/ 双人对话 / 文档转播客（NotebookLM 式） |
| 目标时长 | ✗ | 默认 5 分钟（≈750-900 字中文口播，按 150-180 字/分钟） |
| 节目信息 | ✗ | 节目名、slogan——有则进开场 |

缺输入时一次性问齐："请提供：① 选题或原文档 ② 形态（单人口播/双人对话/文档转播客）③ 目标时长（缺省 5 分钟）④ 节目名与 slogan（可选）。"

## 前置自检

```bash
test -f scripts/script_lint.py && echo LINT-OK
```

预期输出 `LINT-OK`；失败说明技能包不完整，STOP 并提示重装（lint 是进 TTS 前的硬门槛，没有它不许交付脚本）。脚本仅标准库，无需装依赖。

## 工作流

### 步骤 1：大纲先行（钩子 → 三段 → CTA）

```markdown
1. 钩子（15 秒内）：一个反常识 / 一个提问 / 一个数字——先抓人再报节目名
2. 主体：2-3 个 segment，每段一个论点 + 一个例子，段间显式转场句
3. CTA：关注/订阅 + 下期预告，一句话
```

### 步骤 2：逐段写脚本

规则（全部来自 TTS 实战教训）：

- **只写要说出来的词**。禁舞台指示、禁 `[pause]`/`（叹气）`/`**加粗**`/markdown 标记——要停顿就用标点（句号比逗号停得久，破折号制造悬念）
- **数字写汉字口播形**："2026 年"→"二零二六年"按合成器口径统一；易读错的术语给拼音备注到 shownotes 而不是脚本里
- **对话形态**：HOST/GUEST 逐行标注，每行 ≤3 句——单行太长合成腔立刻出来；追问句给 GUEST 制造节奏
- **长内容分段生成**：每段独立成品再拼接（ffmpeg concat），比一口气合成自然得多
- **文档转播客**：先提炼 3-5 个要点再展开成对话——不是把文章朗读一遍

### 步骤 3：跑脚本 lint（机器守门）

```bash
python3 scripts/script_lint.py --file assets/sample-script.md   # 随包样例播客稿
python3 scripts/script_lint.py --file assets/sample-script.md --dialogue   # 对话形态：强制 HOST/GUEST 行前缀
```

检查：舞台指示标记、方括号/圆括号插入语、markdown 残留、单行超长、缺失段间转场。非零退出码 = 有违规，修完重跑至退出码 0 再进 TTS。

### 步骤 4：链条移交

交付分段脚本 + shownotes 草稿。**接着说："脚本已过 lint，继续调用 tts-voice-director 做选声与合成，之后 episode-publisher 出发布件"**——链条自动展开。
- 预期：tts-voice-director 拿到的脚本 lint 退出码 0、分段带目标时长，可直接进选声。
- 若失败：合成阶段发现读错的术语 → 把读音备注写进 shownotes 术语表（不回写脚本），详见失败处置表。

## 交付标准

- 产物：分段脚本（纯口播词，无任何标记残留）+ shownotes 草稿（含术语表初稿）。
- 保存位置：直接输出在对话中；存文件时脚本命名 `script.md`（lint 入参约定）。
- 完整性验证：`python3 scripts/script_lint.py --file script.md` 退出码 0；总字数落在目标时长对应区间（150-180 字/分钟）；每段有显式转场句。

## 失败处置表

| 现象 | 原因 | 处置 |
|------|------|------|
| TTS 把标记读出来 | 脚本含舞台指示/括号 | 跑 script_lint 清零再合成 |
| 合成腔重、像机器人 | 单行太长 / 缺口语连接词 | 每行 ≤3 句；加"其实/说白了/你想"类口语词 |
| 中途节奏垮 | 三段论点平行无递进 | 重排为"现象→反直觉→怎么做"递进结构 |
| 对话像自问自答 | GUEST 只会附和 | 给 GUEST 独立立场或追问钩子 |
| 时长超了 | 字数没控 | 按目标时长倒推字数上限，先砍例子 |

## 参考

- [sources-and-methodology.md](references/sources-and-methodology.md) —— 方法论出处（Podify / inference.sh / 开源 TTS 生态）
