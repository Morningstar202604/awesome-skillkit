---
name: video-subtitles
description: "Generate SRT subtitles and platform-optimized captions from video script. Supports multi-language, timing sync, and per-platform caption formats. Use when the user asks to 加字幕 / 生成字幕 / 做字幕文件 / 短视频字幕 / 烧录字幕 / generate subtitles / add captions / make an SRT. Do NOT use for burning subtitles into video (see video-editor), translating audio (use a transcription tool), or styling thumbnails."
license: Apache-2.0
compatibility: Pure Python, no external dependencies. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: video
  pattern: single-task
  tier: basic
  verified-date: "2026-09-09"
---

# Video Subtitles & Captions

从脚本场景列表生成时间轴对齐的 SRT 字幕与平台合规标题。默认用 `scripts/subtitles.py` 确定性产出；只产字幕文件，不烧录（烧录见 `video-editor`）。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| script | ✓（批次）或 `text`+`start`+`end`（单条） | 场景列表 JSON，含 `dialogue` + `duration_sec` |
| platform | ✗ | `douyin` / `bilibili` / `tiktok` / `youtube`，默认 `douyin` |
| output | ✗ | SRT 输出路径，默认 `/tmp/subtitles.srt` |

任一必需输入缺失时，一次性问齐：

> 请提供：① 脚本场景列表（JSON，含每条 dialogue 与 duration_sec），或 ② 单句文本 + 起止时间。可选：③ 平台（默认 douyin）、④ SRT 输出路径。

## 前置自检

- `python3` 可用。
- 输入可解析：批次 JSON 含 `scenes[].dialogue` 与 `duration_sec`；单条给出 `text` / `start` / `end`。
- 总字幕时长与视频时长一致（误差 ≤ 0.5s），否则提示先校准脚本计时。

## 工作流

### 步骤 1：生成 SRT（批次）

动作：

```bash
python3 scripts/subtitles.py --script script.json --output subtitles.srt --platform douyin
```

预期：退出码 0；`subtitles.srt` 存在，每条 cue = 序号 + 时间码 `HH:MM:SS,mmm --> ...` + 文本，时间码连续无重叠。
若失败：JSON 缺 `duration_sec` → 补全后重跑；无 `dialogue` 的场景自动跳过该 cue。

### 步骤 2：单句字幕（可选）

动作：

```bash
python3 scripts/subtitles.py --text "你们猜我花了多少钱？" --start 0 --end 3 --output line.srt
```

预期：输出仅 1 条 cue，时间码 `00:00:00,000 --> 00:00:03,000`。
若失败：`end <= start` → 报告时间区间非法，修正后重跑。

### 步骤 3：生成平台标题

动作：按下方「平台标题规则」从脚本 `caption` 字段裁剪出合规标题 + 标签。
预期：不超平台字数 / 标签上限（douyin ≤50 字 + 3 标签）。
若失败：超限 → 裁剪标题或合并标签。

## SRT 格式示例

```text
1
00:00:00,000 --> 00:00:03,000
你们猜我花了多少钱？

2
00:00:03,000 --> 00:00:08,000
八千九！就这个？
```

## 平台标题规则

| Platform | Max Caption | Hashtag Limit | Style |
|----------|-----------|---------------|-------|
| Douyin | 50 chars | 3 tags | Emoji + keyword |
| Bilibili | 100 chars | 5 tags | 【标题】 format |
| TikTok | 220 chars | 5 tags | Lowercase + trending |
| YouTube | 100 chars | N/A | Title + description |

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| `--script` | JSON 文件 | 批次场景列表 |
| `--text` | str | 单句文本（与 `--script` 二选一） |
| `--start` / `--end` | float | 单句起止秒，默认 0 / 3 |
| `--platform` | enum | 平台 |
| `--output` | 文件 | SRT 输出路径 |

## 失败处置表

| 现象 | 原因 | 处置 |
|------|------|------|
| 时间码重叠 | 场景时长累加错 | 重算 `duration_sec` 后重跑 |
| caption 超限 | 平台限制 | 裁剪标题 / 合并标签 |
| SRT 为空 | 全场景无 dialogue | 补对话文本 |
| 解析失败 | JSON 语法错 | 修正 `--script` 输入 |

## 交付标准

- `subtitles.srt` 时间码连续、与视频时长一致（误差 ≤ 0.5s）；`caption` 符合平台约束。
- 仅产出字幕文件，不烧录；烧录进成片由 `video-editor` 负责。

## 参考

- `references/caption-formats.md` — 各平台字幕 / 标题格式细节与示例。
