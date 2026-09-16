---
name: video-voice-synth
description: "Text-to-speech for video production via scripts/voice_synth.py: single-line and batch synthesis against a local TTS gateway, per-scene WAV files with the scene_{id}.wav naming contract, six built-in voices (baby/adult/mascot/narrator), --mock silent placeholders for downstream wiring. Use when the script is ready and audio is needed before lip-sync, or when the user asks to 配音 / 合成语音 / 文字转语音 / TTS / 给视频配个声音 / text to speech / generate voiceover / synthesize narration. Do NOT use for cloning a real person's voice without documented consent."
license: Apache-2.0
compatibility: Requires the local TTS gateway (default 127.0.0.1:30081) or --mock mode; the script itself needs Python 3.8+ only. No API keys required (gateway auth optional via GATEWAY_API_KEY env).
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: video
  pattern: single-task
  tier: standard
  verified-date: "2026-09-09"
---

# Video Voice Synthesis（TTS 配音）

把脚本台词转成语音文件。通过本目录 `scripts/voice_synth.py` 执行：默认真实
模式调 TTS 网关真实产出音频，网关不可达即打印排查指引并退出非 0，绝不静默
返回假音频；`--mock` 只出静音占位，供下游联调，不可交付。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 模式 | ✓ | 单句（需 text）/ 批量（需 script JSON） |
| text | 单句 ✓ | 待合成台词 |
| voice | ✗ | 默认 `baby_f01`；全部取值见下方声音目录 |
| speed / pitch | ✗ | 缺省用所选 voice 的内置值（见目录表） |
| script | 批量 ✓ | 脚本 JSON（video-script-writer 产出），含 `tts_config` 与 `scenes[].dialogue` |
| audio_dir | 批量 ✗ | 场景音频输出目录，默认当前目录 |
| output | ✗ | 单句输出路径；默认 `tts_<时间戳>.wav` |

缺输入时一次性问齐：「请提供：① 台词文本（或脚本 JSON 路径）② 音色
（默认 baby_f01）。可选：语速、输出路径。」

## 前置自检

- 网关探活：
  `curl -sS -m 5 -o /dev/null -w '%{http_code}' http://127.0.0.1:30081/`
  打印出任何 HTTP 码（2xx/401/403/404 都算活着）即通过；连接失败 → 让用户
  启动网关或 `export GATEWAY_BASE_URL=http://<host>:<port>`（不带尾斜杠），STOP。
  部署细节见 [references/gateway-setup.md](references/gateway-setup.md)。
- 批量模式：`test -f <script.json>` 通过吗？不通过 → 向用户要脚本文件，STOP。
- 仅下游联调时加 `--mock`（或 `SKILLKIT_MOCK=1`）：产物是静音 WAV 占位，
  **不可交付**。

## 声音目录（音色 × 内置参数）

| Voice ID | Description | pitch | speed | Best For |
|----------|-------------|-------|-------|----------|
| baby_f01 | High-pitched child, fast | 5 | 1.3 | Baby podcast, cute characters |
| baby_f02 | Slightly lower baby, slower | 4 | 1.0 | Baby educational |
| adult_m01 | Male narrator, calm | 0 | 1.0 | Tutorials, vlogs |
| adult_f01 | Female narrator, warm | 1 | 1.0 | Tutorials, reviews |
| mascot_01 | Enthusiastic, slightly robotic | 2 | 1.1 | Mascot/animated characters |
| narrator_01 | Neutral, clear | 0 | 0.9 | Explainer videos |

（`--speed`/`--pitch` 显式传参时覆盖内置值；音色发音调校见
[references/voice-config.md](references/voice-config.md)。）

## 工作流

### 步骤 1：准备输入

单句：确认 text 非空（空文本脚本 exit 3）。批量：确认脚本 JSON 里有
`scenes[].dialogue` 与 `tts_config`（`voice_style`/`speed`）；没有
`tts_config` → 按 baby_f01 默认执行并告知用户。
预期：文本或 JSON 就位，音色选定。
若失败：dialogue 全为空 → 批量会得到 0 条结果；先回视频脚本技能补台词。

### 步骤 2：单句合成

```bash
python3 scripts/voice_synth.py --text "你们猜我花了多少钱买了这个？" \
  --voice baby_f01 --output tts_test.wav
```

预期：退出码 0，stdout 打印 JSON，含 `audio_path`、`voice_used`、`speed`、
`pitch`、`bytes`（`mock:false`），且该 wav 非空。
若失败：exit 4 → 按失败处置表排查网关；先跑一句最短台词验证再上批量。

### 步骤 3：批量合成（按场景）

```bash
python3 scripts/voice_synth.py --script script.json --audio-dir audio/
```

预期：退出码 0，`audio/` 下出现 `scene_<id>.wav`（每个有 dialogue 的场景一个
文件），stdout JSON 的 `all_generated == true`。**命名契约**：`scene_<id>.wav`
是下游 `video-lip-sync --audio-dir` 与 `video-editor --audio-dir` 的约定，不要改名。
若失败：某个场景报错 → 结果 JSON 里 `results[]` 定位该 `scene_id`，单独重跑
该句；`all_generated == false` → 有场景没产出，逐个补。

### 步骤 4：校验与交付

```bash
ls -lh audio/scene_*.wav
```

预期：文件齐全非空；每段音频时长与脚本场景 `duration_sec` 大致吻合
（差得远 → 调 `--speed` 重合成该句）。向用户报告目录与文件清单。
若失败：文件缺失 → 按步骤 3 的结果 JSON 重跑缺失场景。

## 网关协议（真实模式）

网关地址解析顺序：`--gateway-url` > 环境变量 `GATEWAY_BASE_URL` > 默认
`http://127.0.0.1:30081`（仓库示例值，以实际部署为准）。

```text
POST /v1/tts
{"text": "...", "voice": "baby_f01", "speed": 1.3, "pitch": 5, "format": "wav"}
Response: audio binary
```

鉴权：设了 `GATEWAY_API_KEY` 环境变量时自动带 `Authorization: Bearer` 头
（凭据只走环境变量，不写进命令行）。超时由 `GATEWAY_TIMEOUT` 控制（秒，
默认 30）。端点路径与字段名以你的实际部署为准（VERIFY BEFORE USE）。

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------|------|------|
| exit 3：待合成文本为空 | text 只有空格/漏传 | 补文本重跑 |
| exit 3：脚本文件不存在 | `--script` 路径错 | `test -f` 核对路径 |
| exit 4：无法连接网关 | 网关未启动或地址错 | 按前置自检探活命令排查；确认 `GATEWAY_BASE_URL` 无尾斜杠 |
| exit 4：网关返回 HTTP 4xx/5xx | 鉴权/限流/服务异常 | 鉴权走 `GATEWAY_API_KEY` 环境变量；429 稍后重试；超时调大 `GATEWAY_TIMEOUT` |
| exit 4：网关返回空音频 | 服务端异常 | 重试一次；仍空 → 报告网关日志给维护者 |
| 音频时长与场景对不上 | 语速不匹配 | 调 `--speed` 后只重合成该场景 |
| 拿到静音 wav | 误用 `--mock`/SKILLKIT_MOCK=1 | mock 占位不可交付；去掉 mock 重跑真实模式 |

## 交付标准

- 成功 = 真实模式产出的 wav：单句给绝对路径；批量给 `scene_<id>.wav` 全集
  （`all_generated == true`），时长与场景 timing 对得上，目录清单已报告。
- 音色/语速/音高取值已在回报中注明（可复现）。
- mock 产物不是交付物——拿到 mock JSON 视为未完成。

## 参考

- [references/voice-config.md](references/voice-config.md) —— 音色参数与发音调校；选定音色后、批量合成前读
- [references/gateway-setup.md](references/gateway-setup.md) —— 本地 TTS 网关部署；前置自检失败时读
