---
name: format-converter
description: "One entry point for format conversion: documents via pandoc, images via Pillow (with resize and quality), audio/video via ffmpeg, plus directory batch mode. Probes every external dependency first and prints the exact install command when something is missing. Use when the user asks to 格式转换 / 转成 pdf / 图片转 jpg / 批量转格式 / 压缩图片尺寸 / 视频转码 / convert file format / png to jpg / batch convert images. Do NOT use for editing file contents, extracting archives, or OCR of scanned documents."
license: Apache-2.0
compatibility: "Python 3.8+. Image mode requires Pillow (pip install pillow). Document mode requires pandoc. Media mode requires ffmpeg. Batch mode defaults to dry-run and needs --yes to write."
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: tools
  pattern: single-task
  tier: standard
  verified-date: "2026-09-17"
---

# Format Converter（格式转换统一入口）

解决"手上这个文件要变成另一种格式"的问题，把文档/图片/音视频三条管线收进一个命令。

**核心判断：先探测依赖，再动手转换。** 三条管线各自依赖外部工具（pandoc / Pillow / ffmpeg），
缺任何一个都只会得到一句 `command not found`——所以每个子命令开工前先找二进制或库，
缺失时打印**针对当前操作系统的确切安装命令**并以退出码 4 结束。绝不产出半成品冒充成功。

## 输入清单

| 输入 | 必填 | 说明 |
|------|:---:|------|
| 输入文件 / 目录 | 是 | `doc`/`image`/`media` 收两个位置参数 `<in> <out>`；`batch` 收一个目录 |
| 目标格式 | 是 | 由输出扩展名推断（`.docx`/`.jpg`/`.mp4`…）；`batch` 用 `--to <ext>` |
| `--width` / `--quality` | 否 | 仅图片：等比缩放宽度、JPEG/WebP 质量 1-100 |
| `--vcodec` / `--acodec` | 否 | 仅媒体：如 `libx264` / `aac` |
| `--yes` | 否 | `batch` 默认 dry-run，必须加它才写盘 |

缺输入时一次性问齐：「请提供：① 源文件或目录路径 ② 目标格式 ③ 图片是否要限宽/降质量 ④ 是否为批量（若是，先看 dry-run）。默认：单文件直接转换，批量先预演。」

## 前置自检

```bash
python3 --version                                        # 预期 >= 3.8
test -f scripts/convert.py && echo SCRIPT_OK             # 预期打印 SCRIPT_OK
python3 -c "import PIL; print('PIL_OK', PIL.__version__)" 2>/dev/null || echo "PIL 缺失：pip3 install pillow"
command -v pandoc || echo "pandoc 缺失：仅 doc 子命令受影响"
command -v ffmpeg || echo "ffmpeg 缺失：仅 media 子命令受影响"
```

三处外部依赖**按需检查**：只转图片时 pandoc/ffmpeg 缺失不影响使用，脚本也会照此逻辑放行。

## 工作流

### 步骤 1：判断走哪条管线

| 源 → 目标 | 管线 | 命令 |
|-----------|------|------|
| `.md` → `.docx` / `.pdf` / `.html` | doc | `doc` |
| `.docx` → `.md` / `.epub` | doc | `doc` |
| `.png` → `.jpg` / `.webp`（含缩放） | image | `image` |
| `.mov` → `.mp4` / `.webm`（含转码） | media | `media` |
| 目录内一批同类文件 | 上述任一条 | `batch --to <ext>` |

预期：确定管线后进入对应步骤。判读要点：**跨管线转换（如 `.mp4`→`.jpg` 抽帧）不在本工具范围**。
若失败：源/目标组合不在上表（如 `.mp4`→`.jpg`）→ 属跨管线，转告用户该需求本工具不做，
并给出对应专业命令（抽帧用 `ffmpeg -i in.mp4 -frames:v 1 out.jpg`）；
输出扩展名写错 → 脚本以退出码 3 报「无法从扩展名推断格式」，按提示换成受支持的扩展名。

### 步骤 2：单文件转换

```bash
# 文档
python3 scripts/convert.py doc report.md report.docx
# 图片：缩到 800 宽，质量为 85
python3 scripts/convert.py image photo.png photo.jpg --width 800 --quality 85
# 媒体
python3 scripts/convert.py media clip.mov clip.mp4 --vcodec libx264 --acodec aac
```

预期：先打印 `$ <实际执行的命令>`，成功后打印 `OK: <in> <原尺寸/模式> -> <out> <新尺寸> (<字节数>)`。

若失败：退出码 4 + `找不到 pandoc` → 按提示的安装命令装好再重跑（Mac 用 `brew install pandoc`，
Debian/Ubuntu 用 `sudo apt-get install pandoc`，Windows 用 `winget install --id JohnMacFarlane.Pandoc`）；
退出码 2 + `输出路径与输入相同` → 换个输出名，脚本拒绝自我覆盖。

### 步骤 3：批量转换（先预演）

```bash
python3 scripts/convert.py batch "$TARGET_DIR" --to jpg
```

预期：逐行 `[dry-run] (image) a.png -> _converted.jpg/a.jpg`，末尾"磁盘未变化"。
跨管线文件会被明确跳过并标注原因，例如 `[skip:跨管线 media->image] clip.mp4`。

若失败：`候选文件 0 个` → 目录下没有目标管线的源文件，检查 `--to` 是否写错。

### 步骤 4：确认后写盘

```bash
python3 scripts/convert.py batch "$TARGET_DIR" --to jpg --yes
```

预期：逐个打印 `OK:`，末尾"成功 N 个，失败 M 个"，产物落在 `_converted.jpg/`。
批量模式下单个文件失败**不会中断**其余转换，失败项在结尾计数里体现。

若失败：`失败` 计数 > 0 → 逐个看 `[fail]` 行；缺依赖导致的失败会说明是哪个依赖。

### 步骤 5：验收产物

```bash
ls -l "$TARGET_DIR/_converted.jpg/"                    # 数量应与"成功 N 个"一致
python3 -c "
from PIL import Image; import glob
for f in sorted(glob.glob('$TARGET_DIR/_converted.jpg/*.jpg')):
    im = Image.open(f); print(f, im.width, im.height, im.format)
"
```

预期：每个文件都能被打开，尺寸/格式与预期一致。
若失败：`ls` 数量小于"成功 N 个" → 有产物被同名覆盖，加 `--overwrite` 或换 `--outdir` 重跑；
PIL 打不开某个文件 → 该产物损坏（多为转换中途被中断），删掉它并单文件重转。

## 依赖与安装对照表

| 依赖 | 用于 | macOS | Debian/Ubuntu | Windows |
|------|------|-------|---------------|---------|
| pandoc | `doc` | `brew install pandoc` | `sudo apt-get install pandoc` | `winget install --id JohnMacFarlane.Pandoc` |
| Pillow | `image` | `pip3 install pillow` | `pip3 install pillow` | `pip install pillow` |
| ffmpeg | `media` | `brew install ffmpeg` | `sudo apt-get install ffmpeg` | `winget install --id Gyan.FFmpeg` |

脚本在缺依赖时打印的安装命令与上表一致，按当前系统自动选择。

## 失败处置表

| 现象 | 原因 | 处置 |
|------|------|------|
| 退出码 4，`找不到 pandoc/ffmpeg` | 外部二进制未安装 | 按打印的安装命令装好，`<tool> --version` 确认后重跑 |
| 退出码 4，`图片转换需要 Pillow` | 缺 Python 库 | `python3 -m pip install pillow` |
| 退出码 2，`输出路径与输入相同` | `<in>` 与 `<out>` 指向同一文件 | 换输出文件名 |
| 退出码 1，`输入文件不存在` | 路径拼错 | 用 `ls` 核对实际路径 |
| 退出码 3，`无法从扩展名推断格式` | 少见格式未登记 | 直接用 `pandoc -f <from> -t <to>` 显式指定 |
| JPEG 输出报 `cannot write mode RGBA` | 源图带透明通道 | 脚本已自动转 RGB；若自行调库需手动 `convert("RGB")` |
| `[skip:跨管线 media->image]` | 想从视频抽帧成图 | 本工具不做，改用 `ffmpeg -i in.mp4 -frames:v 1 out.jpg` |
| batch 全部 `[skip:目标已存在]` | 上次已转过 | 加 `--overwrite`，或指定新的 `--outdir` |

## 交付标准

**成功定义**：命令退出码为 0 且打印 `OK:`；批量模式下"失败 0 个"。

**产物命名**：单文件用调用方给定的 `<out>`；批量模式为 `<原文件名去扩展>.<目标扩展>`。

**保存位置**：单文件写到指定的输出路径；批量默认写 `<dir>/_converted<ext>/`，可用 `--outdir` 改。

**完整性验证**：

```bash
test -s "$OUT" && echo "非空产物 OK"          # 拒绝 0 字节产物
python3 -c "
from PIL import Image; im = Image.open('$OUT'); im.verify(); print('图片可解码 OK')
" 2>/dev/null || true
ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT" 2>/dev/null   # 媒体时长非空
```

## 参考

- `scripts/convert.py` —— 运行它执行四条子命令；`require_binary`/`require_pillow` 是依赖闸门
- `references/sources-and-methodology.md` —— 依赖探测策略、跨管线拒绝与批量容错的设计依据
