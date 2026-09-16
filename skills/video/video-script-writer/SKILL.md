---
name: video-script-writer
description: "Write video scripts: dialogue, narration, shot descriptions, timing markers, and platform-compliant titles/captions. Supports multiple video types (talking character, meme, tutorial, vlog, short). Use when the user needs a script for a video before production. 当用户要求 写视频脚本 / 短视频文案 / 分镜脚本 时使用。 Do NOT use for generating video files (script text only)."
license: Apache-2.0
compatibility: Pure prompt-based; may call LLM for generation. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: video
  pattern: single-task
  tier: standard
  verified-date: "2026-09-09"
---

# Video Script Writer

产出可投产的结构化视频脚本：对话、计时、视觉提示、平台合规标题与标签。默认用 `scripts/script_writer.py` 确定性生成 JSON；纯提示词场景可直接照模板写。脚本文本是唯一产物，不生成视频文件。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| concept | ✓ | 视频概念一句话（含主体与钩子） |
| video_type | ✗ | `talking_character` / `meme` / `tutorial` / `vlog` / `short`，默认 `talking_character` |
| duration | ✗ | 目标时长（秒），默认 30 |
| platform | ✗ | `douyin` / `bilibili` / `tiktok`，默认 `douyin` |
| language | ✗ | `zh` / `en`，默认 `zh` |
| tone | ✗ | `funny` / `educational` / `dramatic`，默认 `funny` |
| character | ✗ | 角色 JSON（name / personality / voice_style） |

任一必需输入缺失时，一次性问齐：

> 请提供：① 视频概念（一句话）。可选：② 类型（默认 talking_character）、③ 时长（默认 30s）、④ 平台（默认 douyin）、⑤ 语言（默认 zh）、⑥ 角色设定、⑦ 基调（默认 funny）。

## 前置自检

- `python3` 可用（脚本模式）。
- 概念非空：空概念（如"拍个好看的视频"）直接退回，要求补充主体与钩子。
- 时长不超平台上限：douyin 60s / bilibili 900s / tiktok 600s；超限 → 提示拆集或下调时长。

## 工作流

### 步骤 1：生成脚本（脚本模式）

动作：

```bash
python3 scripts/script_writer.py --concept "宝宝测评手机" --type talking_character --duration 30 --platform douyin --language zh --tone funny
```

预期：stdout 输出 JSON，含 `title` / `hook` / `scenes`（id、duration_sec、dialogue、visual、camera、sfx） / `caption` / `total_duration`；`scenes` 总时长 ≈ `duration`。
若失败：JSON 缺字段 → 读 stderr 定位；总时长不符 → 调 `--duration` 或 `--type` 重跑。

### 步骤 2：完整输入 / 落盘（可选）

动作：

```bash
python3 scripts/script_writer.py --json-input script.json --output out.json
```

预期：退出码 0，结构化脚本写入 `out.json`。
若失败：`--json-input` 无法解析 → 报告 JSON 语法错误行，修正后重跑。

### 步骤 3：校验平台合规

动作：比对下方「平台约束」表，检查 `caption` 字数与标签数。
预期：`caption` 不超平台上限（douyin ≤50 字 + 3 标签）。
若失败：超限 → 裁剪标题或合并标签，重算后输出。

## 平台约束

| Platform | Max Duration | Safe Zone | Caption Limit |
|----------|-------------|-----------|---------------|
| Douyin | 60s (short) / 15min (long) | Top 10%, Bottom 15% | 50 chars + 3 tags |
| Bilibili | Unlimited | Full frame | 100 chars |
| TikTok | 10min | Top 10%, Bottom 15% | 220 chars + 5 hashtags |

## 脚本类型要点

### Talking Character（baby, nailong 等）

- 对话驱动，2–4 场景；每场景一句台词 + 一个动作。
- 金句落在 70–80% 处；视觉以角色 + 道具为主，背景极简。

### Meme / Reaction

- 1–3 场景，快切；文字压屏 + 音频金句；每场景 3–7s；结尾利于循环。

### Tutorial / Explainer

- 开头 5s → 步骤 20–60s → 结尾 5s；每步配音 + 录屏；单步 < 10s。

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| `--concept` | str | 必填，视频概念 |
| `--type` | enum | 模板类型（见上） |
| `--duration` | int | 目标秒数，默认 30 |
| `--platform` | enum | 平台 |
| `--language` | zh/en | 默认 zh |
| `--tone` | enum | 基调，默认 funny |
| `--character` | JSON 串 | 角色设定 |
| `--json-input` | 文件 | 完整 JSON 输入，覆盖单项参数 |
| `--output` | 文件 | 写文件替代 stdout |

## 失败处置表

| 现象 | 原因 | 处置 |
|------|------|------|
| 总时长 ≠ 目标 | 模板比例累计误差 | 微调 `--duration` 或拆分场景 |
| caption 超限 | 平台字数/标签限制 | 裁剪标题、合并标签 |
| 空概念报错 | 无输入 | 退回要求补概念 |
| JSON 解析失败 | 输入语法错 | 修正 `--json-input` 后重跑 |

## 交付标准

- 结构化脚本 JSON（含 `title` / `hook` / `scenes` / `caption` / `total_duration`）。
- 总时长匹配目标（±1s）；`caption` 符合平台约束。
- 仅脚本文本，不生成视频文件；下游接 `video-voice-synth` → `video-lip-sync` → `video-editor`。

## 参考

- `references/script-templates.md` — 各类型成品模板，写脚本前照抄骨架。
- `references/timing-guide.md` — 节奏 / beat 规则与时长分配。
