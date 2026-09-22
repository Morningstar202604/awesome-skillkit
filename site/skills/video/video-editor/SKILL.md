---
name: video-editor
description: "Assemble video clips with transitions, mix audio tracks, add effects, and produce final video. Supports FFmpeg-based real editing and mock mode. Use after lip-sync clips are ready, before subtitle/thumbnail steps. 当用户要求 剪辑视频 / 拼接片段 / 合成成片 / 加背景音乐 时使用。 Also triggers on / 视频合成 / 加转场 / 音频混音 / cut video / stitch clips. Do NOT use for generating footage from text (use video-generation)."
license: Apache-2.0
compatibility: Requires FFmpeg for real editing; mock mode works without. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: video
  pattern: single-task
  tier: standard
  verified-date: "2026-09-09"
---

# Video Editor / Assembly

组合片段、混音、加转场，产出可发布成片。默认**真实模式**：调用 `scripts/editor.py`（底层用 ffmpeg）真实产出文件；`--mock` 或 `SKILLKIT_MOCK=1` 只输出元数据，仅供下游联调，不可交付。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| clips | ✓ | 待拼接片段路径列表（顺序即拼接顺序） |
| output | ✓ | 成片输出路径，如 `final.mp4` |
| audio | ✗ | 背景音乐 / 配音文件，可多个 |
| transitions | ✗ | 片段间转场类型：`fade` / `cut` / `slide`，默认 `cut` |
| script | ✗ | 整链路 JSON（批次模式，含 clips/audio 描述） |

任一必需输入缺失时，一次性问齐：

> 请提供：① 片段文件列表（路径）；② 成片输出路径。可选：③ 背景音乐、④ 转场类型（默认 cut）、⑤ 整链路 script JSON。

## 前置自检

```bash
command -v ffmpeg >/dev/null && echo "ffmpeg ok" || echo "ffmpeg MISSING"
for f in clip1.mp4 clip2.mp4; do test -f "$f" && echo "found $f" || echo "MISSING $f"; done
```

探测项：① `ffmpeg` 已安装（真实模式必需）；② 每个 `clips` 文件存在；③ `output` 所在目录可写。
任一失败 → 给出修复并 STOP：ffmpeg 缺失打印安装指引（`sudo apt install -y ffmpeg` / `brew install ffmpeg`，校验 `ffmpeg -version`）；文件缺失报告具体文件名；不静默降级到占位文件。

## 工作流

### 步骤 1：收集并校验片段

动作：列出 `clips`，确认每个文件存在且可解码（`ffprobe -v error "<clip>"` 退出码 0）。
预期：片段列表非空，每个文件 `ffprobe` 通过。
若失败：文件缺失/解码失败 → 报告文件名并 STOP，不要跳过该片段继续拼接。

### 步骤 2：运行剪辑脚本（真实模式）

动作：

```bash
python3 scripts/editor.py --clips clip1.mp4 clip2.mp4 --audio bgm.mp3 --output final.mp4 --transitions fade cut --mock   # --mock 仅联调（产物占位不可交付）；真实产出去掉 --mock（需 ffmpeg）
```

预期：退出码 0；`final.mp4` 存在且 `ls -l final.mp4` 显示大小 > 0。
若失败：退出非 0 → 读 stderr；`ffmpeg: command not found` 见前置自检重装；转场类型不被支持 → 降级为 `cut` 重跑。

### 步骤 3：批次链路（可选）

动作：

```bash
python3 scripts/editor.py --script script.json --clips-dir clips/ --audio-dir tts/ --output final.mp4
```

预期：退出码 0，按 `script.json` 组装所有片段与音频。
若失败：JSON 字段缺失 → 读 stderr 定位，补全 `clips`/`audio` 键后重跑。

### 步骤 4：校验成片

动作：

```bash
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1 final.mp4
```

预期：打印成片时长（秒），与脚本目标时长误差 ≤ 0.5s。
若失败：时长明显偏短 → 检查 `--clips` 是否有遗漏片段，补回重拼。

## 底层 FFmpeg 配方

脚本已封装常见操作；需要手动调参时，以下配方与 `references/ffmpeg-recipes.md` 一致：

```bash
# 拼接（生成 clips.txt：每行 file '<路径>'）
ffmpeg -f concat -safe 0 -i clips.txt -c copy combined.mp4

# 混 BGM（压到 0.3 音量后与原声混合）
ffmpeg -i combined.mp4 -i bgm.mp3 -filter_complex \
  "[1:a]volume=0.3[bgm];[0:a][bgm]amix=inputs=2" final.mp4

# 片段间交叉淡入
ffmpeg -i clip1.mp4 -i clip2.mp4 -filter_complex \
  "xfade=transition=fade:duration=0.5" output.mp4
```

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| `--clips` | 文件列表 | 顺序即拼接顺序 |
| `--audio` | 文件列表 | 与画面混音，音量见配方 |
| `--transitions` | fade/cut/slide | 片段间转场，默认 cut |
| `--script` | JSON 文件 | 整链路批次模式（覆盖单项参数） |
| `--clips-dir` / `--audio-dir` | 目录 | 批次模式的片段/音频目录，默认 `clips`/`tts` |
| `--output` | 路径 | 成片路径，默认 `final_video.mp4` |
| `--mock` | 标志 | 只输出元数据不生成文件（下游联调） |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| `ffmpeg: command not found` | 未安装 | 装 ffmpeg 后重跑（见前置自检） |
| 脚本退出非 0 | 片段缺失/解码失败 | 读 stderr 定位具体文件 |
| 成片时长偏短 | 片段漏拼 | 核对 `--clips` 列表补全 |
| 成片无声 | 未传 `--audio` | 追加 `--audio bgm.mp3` 重混 |
| 覆盖已有文件 | 用户同名成片 | 覆盖前先向用户确认（不可逆写操作） |

## 交付标准

- `final.mp4` 存在，`ls -l` 大小 > 0，时长匹配目标（误差 ≤ 0.5s）。
- 真实模式为默认；`--mock` 仅产出元数据占位，不可作为最终交付。
- 不可逆写操作（覆盖用户已有同名成片）前必须向用户确认。

## 参考

- `references/ffmpeg-recipes.md` — 拼接 / 混音 / 转场的底层 ffmpeg 配方与手动调参示例，脚本封装之外需要精修时查阅。
