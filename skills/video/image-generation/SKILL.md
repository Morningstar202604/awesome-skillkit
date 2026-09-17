---
name: image-generation
description: >
  Generate images from text prompts or reference images through a local
  generation gateway (text-to-image and image-to-image with polling and
  download). Use when the user asks to 生成图片 / 画一张 / 文生图 /
  图生图 / 改图 / generate an image of / create a picture / edit this photo,
  or wants AI artwork, illustrations, covers, or product renders.
  Do NOT use for screenshot capture, cropping/resizing existing files,
  or OCR — those need local tools, not this skill.
license: Apache-2.0
compatibility: Requires curl and network access to the generation gateway endpoint.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: media-generation
  verified-date: "2026-08-26"
---

# 图像生成（文生图 / 图生图）

用 curl 驱动本地生成网关：提交任务 → 轮询至完成 → 下载 PNG → 把文件路径交给用户。不需要 Pillow/OpenCV，不装任何依赖——网关负责渲染，你负责编排。

## 输入清单

| 输入 | 必需 | 默认 | 说明 |
|---|---|---|---|
| 画面描述 | 是 | — | 图像画什么；按下文 prompt 公式撰写 |
| size | 否 | `1024x1024` | 任意宽高，两边均为 16 的倍数 |
| quality | 否 | `auto` | `auto` / `high` / `medium` / `low` |
| n | 否 | `1` | 生成张数 |
| reference_image_urls | 否 | — | 最多 14 个 URL；提供即切换为图生图模式 |

尺寸约束（使用前对照网关文档核实）：宽高都必须是 16 的倍数；宽高比在 1:3–3:1 之间；总像素在 655360–8294400 之间。

常用尺寸：1024x1024、1024x1536、1536x1024、960x1280、1280x960、1088x1920、1920x1088、2048x2048、2048x3072、3072x2048、1920x2560、2560x1920、1440x2560、2560x1440、2160x3840、3840x2160。

必需输入缺失时，一次性问齐：

> 请描述想要的画面：主体、风格、用途（如封面/插画/产品图）。可选告知：
> 尺寸（默认 1024x1024）、画质（默认 auto）、数量（默认 1）、参考图 URL。

## 前置自检

先解析网关基址（与工作流步骤 1 同一句，展开后留用），再探活：

```bash
IMAGE_GATEWAY_BASE="${IMAGE_GATEWAY_BASE:-http://127.0.0.1:30080}"
curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$IMAGE_GATEWAY_BASE/api/image/status?task_id=0"
```

预期：打印出任意 HTTP 码（网关可达）。若失败：curl 退出码非 0 → 报告 base URL 问题，请用户启动网关，STOP；HTTP 401/403 → 网关在跑但需鉴权，确认凭据走环境变量；HTTP 404 → 路由名与部署不符，对照网关文档核实端点。绝不退回到本地画图工具或占位文件。

## 工作流

### 步骤 1：确认网关地址

```bash
IMAGE_GATEWAY_BASE="${IMAGE_GATEWAY_BASE:-http://127.0.0.1:30080}"
echo "$IMAGE_GATEWAY_BASE"
```

预期：打印出一个 URL。
若失败：展开为空说明 shell 异常（或环境变量被显式置空）→ 改用字面量 base URL 并告知用户；URL 与前置自检探活的不一致 → 以前置自检通过的值为准，不要中途换地址。

### 步骤 2：撰写 prompt

精确描述物体、风格与文字排版——指令是否清晰、细节是否忠实，决定出图质量。结构：

```json
[主体与细节] + [风格/媒介] + [构图与视角] + [文字排版要求，如有]
```

规则：具体名词优于形容词（写"磨砂玻璃瓶上的水珠"，不写"好看的瓶子"）；风格只说一次、说清楚（"扁平插画、有限四色"）；图上要出现文字时，逐字引用字符串并标注位置（"顶部横排文字：春季上新"）。

预期：prompt 含全部四个成分，图上文字已逐字加引号。
若失败：写不出具体名词（只有"好看/高级"类词）→ 回输入清单向用户要参考物或用途（封面/插画/产品图），用参考物换算成具体描述；图上有中文文字且模型渲染不可靠 → 改为无字底图 + 后期排版，并在交付中说明。

### 步骤 3：提交任务

文生图：

```bash
curl -s -X POST "$IMAGE_GATEWAY_BASE/api/image/generate" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-image-2","prompt":"<STEP-2 PROMPT>","params":{"size":"1024x1024","quality":"auto","n":1}}'
```

图生图在 `params` 里追加 `"images":["<url>", ...]`。

预期：返回含 `task_id` 的 JSON。若失败：HTTP 错误或返回 HTML → 原样重试一次；仍失败 → 按失败处置表报告状态行并停止。返回尺寸/参数错误 → 按尺寸约束改尺寸后重新提交一次。

### 步骤 4：轮询至终态

```bash
curl -s "$IMAGE_GATEWAY_BASE/api/image/status?task_id=<TASK_ID>"
```

每 3–5 秒轮询一次。成功条件：`is_final == true` 且 `state == "success"`，取 `result_url`。`is_final == true` 但 state 为其他值即失败——查下方失败处置表。轮询上限 120 次（约 8 分钟）。
若失败：`state == "failed"` → 用更具体的细节重写 prompt 后重交一次；超 8 分钟仍未终态 → 报告 `task_id` 并建议重新提交；`is_final == true` 但缺 `result_url` → 把端点标记「使用前核实」，原始 JSON 报给维护者。

### 步骤 5：下载交付

```bash
curl -s -L -o "image_$(date +%Y%m%d_%H%M%S).png" "<RESULT_URL>"
ls -lh image_*.png
```

预期：工作目录出现非空 .png。确认文件大小 > 0 再宣布成功；报告绝对路径。
若失败：文件 0 字节 → `result_url` 已过期，重新轮询拿新 URL 再下载一次；仍为 0 → 向用户报告并附原始响应，不要用占位图冒充成功。

## 失败处置表

| 现象 | 原因 | 处置 |
|---|---|---|
| curl 无法连接（前置自检） | 网关未启动 | 请用户启动网关；停止 |
| generate 返回尺寸/参数错误 | 违反尺寸约束 | 改成 16 倍数且符合像素/比例边界的尺寸，重新提交一次 |
| status 一直 `pending` 超 8 分钟 | 队列卡住 | 报告 task_id，建议重新提交 |
| `state == "failed"` | prompt 太含糊或触犯政策 | 用具体细节重写 prompt，重新提交一次 |
| 下载文件 0 字节 | URL 已过期 | 重新轮询拿新的 result_url，再下载一次 |
| 成功但缺 `result_url` | API 结构变更 | 把端点标记为"使用前核实"；把原始 JSON 报给维护者 |

## 交付标准

成功 = 本地 `.png` 文件、大小 > 0、命名为 `image_YYYYMMDD_HHMMSS.png`（带时间戳），已报告绝对路径及所用的 size/quality。其余情况都算未完成——直说，并给出上方失败处置表的对应行。

## 参考

- 本技能为纯提示型，无需外部参考文件。
