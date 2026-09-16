---
name: video-thumbnail
description: "Design and generate video thumbnails/covers per platform spec (douyin/bilibili/tiktok/youtube), via ffmpeg frame extraction or the image-generation gateway (scripts/thumbnail.py; --mock only for downstream wiring). Use when the user asks to 做视频封面 / 设计封面图 / 缩略图 / 封面图 / video thumbnail / design a cover / YouTube cover image, as the final step before publishing. Do NOT use for generating the video itself, or for in-video subtitles."
license: Apache-2.0
compatibility: Route A (gateway) needs the image-generation gateway; Route B (frame extract) needs ffmpeg. No API keys required (gateway auth optional via GATEWAY_API_KEY env).
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: video
  pattern: single-task
  tier: basic
  verified-date: "2026-09-09"
---

# Video Thumbnail / Cover（平台规格封面）

两条路线产出平台规格封面：A=文生图走图像网关，B=从成片 ffmpeg 抽帧。
全部通过本目录 `scripts/thumbnail.py` 执行，脚本默认真实模式，失败退出非 0，
绝不静默返回假结果。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 路线 | ✓ | `A` = AI 生成（需 title）；`B` = 成片抽帧（需 video_source） |
| title | A ✓ | 封面主题/标题文案 |
| platform | ✗ | `douyin`（默认）/ `bilibili` / `tiktok` / `youtube`，决定分辨率与比例 |
| style | ✗ | `funny`（默认）/ `professional` / `dramatic` / `cute`；funny 自动加 NEW 徽章 |
| video_source | B ✓ | 成片 mp4 路径 |
| character_image | ✗ | 角色图路径（路线 A 可选，须真实存在于盘上） |
| output | ✗ | 输出路径；默认 `thumbnail_<platform>.png`（抽帧默认 `thumb_frame.png`） |

缺输入时一次性问齐：「请提供：① 路线（AI 生成 / 从成片抽帧）② 平台（默认抖音）。
路线 A 再给标题；路线 B 再给成片路径。」

## 平台规格

| Platform | Size | Ratio | Max Size |
|----------|------|-------|----------|
| Douyin | 1080x1920 | 9:16 | 2MB |
| Bilibili | 1920x1080 | 16:9 | 2MB |
| TikTok | 1080x1920 | 9:16 | 2MB |
| YouTube | 1280x720 | 16:9 | 2MB |

（脚本内置同款 `PLATFORM_SPECS`；2026 年常见值，发布前请核对平台最新规范。）

## 前置自检

- 路线 B：`command -v ffmpeg` 有输出吗？没有 → `sudo apt install -y ffmpeg`
  或 `brew install ffmpeg` 后重试，或改走路线 A。
- 路线 B：`test -f <video_source>` 通过吗？不通过 → 向用户要正确路径，STOP。
- 路线 A：网关探活
  `curl -sS -m 5 -o /dev/null -w '%{http_code}' http://127.0.0.1:30080/`
  打印出任何 HTTP 码（2xx/401/403/404 都算活着）即通过；连接失败 → 让用户
  启动网关或 `export GATEWAY_BASE_URL=http://<host>:<port>`（不带尾斜杠），STOP。
- 仅下游联调时可加 `--mock`（或 `SKILLKIT_MOCK=1`）：只输出布局元数据、
  不生成文件，**产物不可交付**。

## 工作流

### 步骤 1：确定平台规格

按上表取 resolution/ratio，或直接用脚本默认 `--platform douyin`。
预期：写下了目标 width/height 与 2MB 上限。
若失败：平台不在四选项内 → 按 9:16 或 16:9 就近映射并告知用户。

### 步骤 2A：路线 A —— 网关生成

```bash
python3 scripts/thumbnail.py --title "宝宝测评iPhone 16" --style funny \
  --platform douyin --character /tmp/baby.png --output thumbnail_douyin.png
```

预期：退出码 0，stdout 打印 JSON，含 `output_path`、`spec`（width/height）、
`layout`（`text_position`/`font_size`/`badge`），且该文件非空。
若失败：非 0 退出按 stderr 指引处理（exit 3=角色图不存在；exit 4=网关不可达
或 HTTP 错误），见失败处置表。

### 步骤 2B：路线 B —— ffmpeg 抽帧

```bash
python3 scripts/thumbnail.py --video /tmp/final.mp4 --timestamp 1.0 \
  --output thumb_frame.png
```

预期：退出码 0，`thumb_frame.png` 非空。`--timestamp` 默认 0.5s，片头常是
黑场，建议 ≥1.0。若失败：exit 3 且提示抽帧结果为空 → 调大 `--timestamp` 重跑。

### 步骤 3：文字叠加与徽章

脚本 JSON 里的 `layout` 给出布局参数：9:16 用 `bottom_center`（避让平台 UI）、
其余 `center`；width ≥1920 用 `font_size 72`，否则 48；`style=funny` 自动带
`NEW` 徽章。文字内容 = title，9:16 最多 2–4 个字。设计原则按
[references/thumbnail-design.md](references/thumbnail-design.md) 执行（此时读）。
预期：叠加方案能复述出位置/字号/文案三要素。
若失败：title 太长 → 与用户确认截短版本后再落版。

### 步骤 4：校验与交付

```bash
ls -lh thumbnail_douyin.png
```

预期：文件存在、非空、小于平台 2MB 上限（超限脚本会打 `[WARN]`，按提示转
JPG 或降质量重导）。向用户报告绝对路径与平台规格。
若失败：超限警告 → 转 JPG/降质量后重跑步骤 2，再校验一次。

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------|------|------|
| exit 2：PATH 中未找到 ffmpeg | 路线 B 缺依赖 | 按 stderr 指引安装 ffmpeg；或改走路线 A |
| exit 3：角色图不存在 | `--character` 路径错 | `test -f` 核对路径，向用户要正确文件 |
| exit 3：抽帧结果为空 | 时间点落在黑场/坏帧 | 调大 `--timestamp`（如 1.5、2.0）重跑 |
| exit 4：无法连接网关 | 网关未启动或地址错 | 按前置自检探活命令排查；确认 `GATEWAY_BASE_URL` 无尾斜杠 |
| exit 4：网关返回 HTTP 4xx/5xx | 鉴权/限流/服务异常 | 鉴权走 `GATEWAY_API_KEY` 环境变量（勿写进命令行）；429 稍后重试 |
| `[WARN]` 封面超 2MB | 分辨率高/质量过高 | 转 JPG 或降质量重导，再校验 |
| 拿到的是 mock 输出 | 误用 `--mock`/SKILLKIT_MOCK=1 | mock 无真实文件，去掉 mock 参数重跑真实模式 |

## 交付标准

- 成功 = 真实模式产出的封面文件，非空、尺寸符合平台规格、体积 < 2MB 上限，
  绝对路径已报告（默认命名 `thumbnail_<platform>.png` 或用户指定的 `--output`）。
- 9:16 平台的文字叠加方案（位置/字号/文案）已按 layout 落实。
- mock 产物不是交付物——拿到 mock JSON 视为未完成。

## 参考

- [references/thumbnail-design.md](references/thumbnail-design.md) —— 封面设计原则与示例；步骤 3 落文字/徽章前必读
