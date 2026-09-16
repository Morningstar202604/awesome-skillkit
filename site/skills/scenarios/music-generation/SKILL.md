---
name: music-generation
description: >
  Generate music tracks from a text brief through a local generation gateway
  (style, instruments, mood, duration; polling and download included). Use
  when the user asks to 生成音乐 / 做首曲子 / 配乐 / background music /
  generate a song / make BGM / 写段旋律. Do NOT use for text-to-speech,
  audio editing, trimming MP3s, or transcription.
license: Apache-2.0
compatibility: Requires curl and network access to the generation gateway endpoint.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: media-generation
  verified-date: "2026-08-26"
---

# Music Generation（需求简报 → 音轨）

用 curl 驱动本地生成网关：提交音乐任务，轮询到结束，下载音频文件。不用本地合成工具，不装依赖——渲染在网关侧，你负责编排。

> ENDPOINT STATUS: VERIFY BEFORE USE — 首次运行前，先对照你的网关文档确认
> `/api/music/*` 路径；下方前置自检会在路由不同或缺失时快速失败。

## 输入清单

| 输入 | 必填 | 默认 | 说明 |
|---|---|---|---|
| 风格/情绪简报 | 是 | — | 曲风 + 乐器 + 情绪，一句话 |
| duration_seconds | 否 | `30` | 保持在网关文档标注的范围内 |
| instrumental | 否 | `true` | 仅在提供歌词时设 `false` |
| lyrics | 否 | — | instrumental 为 false 时必填 |

缺必填项时，只问一次：

> 请描述想要的音乐：风格（如轻快的企业宣传曲）、主要乐器、情绪。
> 可选告知：时长（默认 30 秒）、是否需要人声歌词（默认纯音乐）。

## 前置自检

```bash
curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$MUSIC_GATEWAY_BASE/api/music/status?task_id=0"
```

预期：打印一个 HTTP 状态码。若连接失败或路径返回 404：报告 $MUSIC_GATEWAY_BASE 处音乐端点不可用，展示确切状态码，然后 STOP。绝不改用本地合成顶替。

## 工作流

### 步骤 1：确定网关基址

```bash
MUSIC_GATEWAY_BASE="${MUSIC_GATEWAY_BASE:-http://127.0.0.1:30080}"
echo "$MUSIC_GATEWAY_BASE"
```

预期：打印一个 URL。

### 步骤 2：组织音乐简报

一句话填满三个槽位：

```json
[风格流派] + [主导乐器] + [情绪与用途]
```

示例："轻快的流行电子风，钢琴与合成器主导，用于产品发布会的开场暖场，
积极向上。" 不要点名艺术家；改用声音特征描述。

### 步骤 3：提交任务

```bash
curl -s -X POST "$MUSIC_GATEWAY_BASE/api/music/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"<STEP-2 BRIEF>","params":{"duration":"30","instrumental":true}}'
```

带歌词：加 `"instrumental":false` 和 `"lyrics":"<LYRICS>"`。

预期：JSON 含 `task_id`。失败分支——HTTP 错误或返回 HTML：
原样重试一次，然后报告并停止。

### 步骤 4：轮询到终态

```bash
curl -s "$MUSIC_GATEWAY_BASE/api/music/status?task_id=<TASK_ID>"
```

每 10 秒轮询一次。成功条件：`is_final == true` 且
`state == "success"`；取 `result_url`。上限 60 次（10 分钟）。

### 步骤 5：下载并交付

```bash
curl -s -L -o "music_$(date +%Y%m%d_%H%M%S).mp3" "<RESULT_URL>"
ls -lh music_*.mp3
```

预期：非空音频文件。声称成功前先验证大小 > 0；
回报绝对路径和所用简报。

## 失败处置表

| 现象 | 可能原因 | 处置 |
|---|---|---|
| 前置自检 404 | 该网关路由名不同 | 查网关文档；更新本文件常量；告知用户 |
| 前置自检连接失败 | 网关未启动 | 请用户启动；停止 |
| 不带 flag 提交歌词被拒 | 参数不匹配 | 显式设 instrumental=false，重提交一次 |
| status 长时间停在 `pending`（>10 分钟） | 队列卡住 | 回报 task_id，建议重提交 |
| `state == "failed"` | 简报太模糊或命中歌词策略 | 把简报改具体 / 缩短歌词，重试一次 |
| 下载文件 0 字节 | URL 过期 | 重新轮询拿新 result_url，再下载一次 |

## 交付标准

成功 = 本地非空音频文件 `music_YYYYMMDD_HHMMSS.mp3`，回报绝对路径并附风格简报与时长。缺任何一项即未完成——如实说明并指出上方对应的失败行。

## 链条衔接（下游建议）

本技能产出 BGM / 配乐，可作为 video 域 meme / talking_character 链的 music-generation 步骤输入（video 域 chains 已登记 music-generation，但本技能未列入 skills 列表，属游离）。建议在 video 域 skills 列表中补登本技能以完成衔接。衔接仅为文字描述。
