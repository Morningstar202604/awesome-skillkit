---
name: video-lip-sync
description: "Synchronize character mouth movements with TTS audio. Takes a face image + audio file, generates lip-synced video. Gateway-based with mock fallback. Use when the user asks to 对口型 / 口型同步 / 数字人说话 / 让照片开口说话 / lip sync / talking head video / make the avatar talk. Do NOT use for voice synthesis (see video-voice-synth), subtitle generation (see video-subtitles), or generic video editing."
license: Apache-2.0
compatibility: Requires local lip-sync gateway at 127.0.0.1:30081 or mock mode. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: video
  pattern: single-task
  tier: standard
  verified-date: "2026-09-09"
---

# Video Lip Sync

把角色正面图与 TTS 干声同步成口型视频。默认**真实模式**：调用 `scripts/lip_sync.py` 访问用户自备的 lip-sync 网关真实产出视频；`--mock` 或 `SKILLKIT_MOCK=1` 只输出元数据，仅供下游联调，不可交付。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| face_image | ✓ | 角色正面图路径（与 voice-synth 用同一张，保证不跑脸） |
| audio | ✓（单条）或 `script`（批量） | TTS 干声，无 BGM / 无混响 |
| output | ✗ | 输出路径，默认 `lipsync_<face>.mp4` |
| mouth_width / mouth_height | ✗ | 口型框尺寸（像素），默认 `40` / `30` |
| gateway_url | ✗ | 网关根地址，覆盖 `GATEWAY_BASE_URL` |

任一必需输入缺失时，一次性问齐：

> 请提供：① 角色正面图路径；② 干声文件路径（或批量 script JSON）。可选：③ 输出路径、④ 口型框尺寸（默认 40×30）。

## 前置自检

```bash
GATEWAY_BASE_URL="${GATEWAY_BASE_URL:-http://127.0.0.1:30081}"
curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$GATEWAY_BASE_URL/v1/lipsync"
```

探测项：① 网关可达（真实模式必需；mock 模式跳过）；② `face_image` 与 `audio` 文件存在；③ `python3` 可用。
预期：真实模式下打印 HTTP 码（网关在线）。任一失败 → 修复并 STOP：网关不可达提示启动服务或设置 `GATEWAY_BASE_URL`；文件缺失报告具体文件名；绝不静默返回假结果。

## 工作流

### 步骤 1：单条口型同步（真实模式）

动作：

```bash
python3 scripts/lip_sync.py --face character.png --audio scene_1.wav --output lipsync_scene_1.mp4
```

预期：退出码 0；`lipsync_scene_1.mp4` 存在且 `ls -l` 大小 > 0；时长 ≈ 音频时长。
若失败：网关 4xx/5xx → 查 `references/gateway-setup.md` 核对端点字段；嘴几乎不动 → 换成干净干声（无 BGM）重抽；出口型失真 → 调 `--mouth-width/--mouth-height` 重试。

### 步骤 2：批量同步

动作：

```bash
python3 scripts/lip_sync.py --face character.png --script script.json --audio-dir tts/ --output lipsync.mp4
```

预期：每个场景产出一条口型视频，退出码 0。
若失败：某场景音频缺失 → 报告缺哪条，补齐 `audio-dir` 内对应文件后重跑。

### 步骤 3：mock 联调（可选，仅供下游接线）

动作：追加 `--mock`（或 `SKILLKIT_MOCK=1`）。
预期：只输出元数据 JSON，不生成视频文件。
若失败：非 mock 却网关挂 → 退出非 0；此时要么启网关，要么显式 `--mock`。

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| `--face` | 路径 | 必填，角色正面图 |
| `--audio` | 路径 | 单条音频（与 `--script` 二选一） |
| `--script` | JSON | 批量模式剧本 |
| `--audio-dir` | 目录 | 批量音频目录，默认 `.` |
| `--output` | 路径 | 输出视频路径 |
| `--mouth-width` / `--mouth-height` | int | 口型框尺寸，默认 40 / 30 |
| `--gateway-url` | URL | 覆盖 `GATEWAY_BASE_URL` 与环境变量 |
| `--mock` | 标志 | 静默占位（只输出元数据） |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| 网关不可达 | 服务未启动 | 启网关 / 设 `GATEWAY_BASE_URL`，或显式 `--mock` |
| 嘴几乎不动 | 音频含 BGM / 含糊 | 换干净干声，标点断句重试 |
| 口型框错位 | mouth 尺寸不当 | 调 `--mouth-width/--mouth-height` |
| 端点字段不符 | 部署与默认不同 | 查 `references/gateway-setup.md`，端点路径/字段标 `VERIFY BEFORE USE` |
| 覆盖已有文件 | 用户同名输出 | 覆盖前先向用户确认（不可逆写操作） |

## 交付标准

- 每场景 `lipsync_*.mp4` 存在，`ls -l` 大小 > 0，时长匹配对应音频。
- 真实模式为默认；`--mock` 仅产出占位，不可作为最终交付。
- 角色图与 voice-synth 用同一张，保证口型与音色一致、不跑脸。

## 参考

- `references/gateway-setup.md` — lip-sync 网关部署、端点路径与字段名核实（部署差异大，执行前按文档核对）。
