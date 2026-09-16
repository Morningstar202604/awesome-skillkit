---
name: video-generation
description: >
  Generate short videos from text prompts or reference images through a local
  generation gateway (text-to-video and image-to-video with polling and
  download). Use when the user asks to 生成视频 / 做个短视频 / 文生视频 /
  图生视频 / make a video from this text / animate this image / 生成宣传片,
  or wants AI-generated footage. Do NOT use for video editing, subtitle
  burning, screen recording, or downloading existing videos from the web.
license: Apache-2.0
compatibility: Requires curl and network access to the generation gateway endpoint.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: media-generation
  verified-date: "2026-08-26"
---

# 视频生成（文生视频 / 图生视频）

用 curl 驱动本地生成网关：提交任务 → 轮询至完成 → 下载结果 → 把文件路径交给用户。不需要 ffmpeg，不装 Python 媒体库，不装任何依赖——网关负责渲染，你负责编排。

## 输入清单

| 输入 | 必需 | 默认 | 说明 |
|---|---|---|---|
| 主题 / 文案 | 是 | — | 视频拍什么；用户原话或一句话简报 |
| aspect_ratio | 否 | `16:9` | `16:9` 横屏、`9:16` 竖屏、`1:1` 方形 |
| duration | 否 | `6` | 秒数；`6` 或 `10` |
| size | 否 | `720P` | `720P` 或 `1080P` |
| reference_image_url | 否 | — | 提供即切换为图生视频模式 |

必需输入缺失时一次性问齐，其余按默认值补齐：

> 请提供：① 视频主题或文案。可选告知：② 画面比例（默认 16:9）、③ 时长
> （默认 6 秒，可选 10）、④ 画质（默认 720P）、⑤ 参考图 URL（有则走图生视频）。

## 前置自检

最先执行（BASE 取自工作流步骤 1）：

```bash
curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$VIDEO_GATEWAY_BASE/api/video/status?task_id=0"
```

预期：打印出任意 HTTP 码（网关可达）。curl 连接失败（退出码非 0）：告知用户 $VIDEO_GATEWAY_BASE 不可达，请其启动网关，STOP。不要退回本地渲染工具。

## 工作流

### 步骤 1：确认网关地址

```bash
VIDEO_GATEWAY_BASE="${VIDEO_GATEWAY_BASE:-http://127.0.0.1:30080}"
echo "$VIDEO_GATEWAY_BASE"
```

预期：打印出一个 URL。展开后为空说明 shell 异常——停止。

### 步骤 2：撰写 prompt

只写一段描述性文字，覆盖动作、场景与情绪。遵循 `references/prompt-recipes.md` 的公式（简报单薄或用户在意质量时先读它）。绝不把光秃秃的名词短语当 prompt 发出去。

### 步骤 3：提交生成任务

文生视频：

```bash
curl -s -X POST "$VIDEO_GATEWAY_BASE/api/video/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"<STEP-2 PROMPT>","params":{"aspect_ratio":"16:9","duration":"6","size":"720P"}}'
```

图生视频在 `params` 里追加 `"images":["<url>"]`。

预期：返回含任务 ID（`task_id`）的 JSON，提取并记住它。失败分支——HTTP 错误或返回 HTML 而非 JSON：原样重跑一次；再失败则向用户报告状态行并停止（见失败处置表）。

### 步骤 4：轮询至终态

```bash
curl -s "$VIDEO_GATEWAY_BASE/api/video/status?task_id=<TASK_ID>"
```

每 10 秒轮询一次。成功条件：`is_final == true` 且 `state == "success"`，此时 `result_url` 即下载地址。`is_final == true` 但 state 为其他值即失败——查下方失败处置表。轮询不超过 60 次（10 分钟）；超时须给出清晰报告。

### 步骤 5：下载交付

```bash
curl -s -L -o "video_$(date +%Y%m%d_%H%M%S).mp4" "<RESULT_URL>"
ls -lh video_*.mp4
```

预期：工作目录出现非空 .mp4。确认文件大小 > 0 再宣布成功。向用户报告绝对路径。

## 失败处置表

| 现象 | 原因 | 处置 |
|---|---|---|
| curl 无法连接（前置自检） | 网关未启动 | 请用户启动网关；停止 |
| generate 返回非 JSON | base URL 错误或有代理 | 重查一次步骤 1 的值，重试一次，然后报告 |
| status 一直 `pending` 超 10 分钟 | 队列卡住 | 报告 task_id，建议重新提交 |
| `state == "failed"` | prompt 被拒（通常太短） | 按配方重写 prompt，重新提交一次 |
| 下载文件 0 字节 | URL 过期/签名失效 | 重新轮询拿新的 result_url，再下载一次 |
| 成功但缺 `result_url` | API 结构变更 | 把端点标记为"使用前核实"；把原始 JSON 报给维护者 |

## 交付标准

成功 = 本地 `.mp4`、大小 > 0、命名为 `video_YYYYMMDD_HHMMSS.mp4`（带时间戳），已向用户报告路径及所用的时长/比例。其余情况都算未完成——直说，并给出上方失败处置表的对应行。

## 参考

- `references/prompt-recipes.md` —— prompt 公式与强弱示例；撰写任何 prompt 前先读
