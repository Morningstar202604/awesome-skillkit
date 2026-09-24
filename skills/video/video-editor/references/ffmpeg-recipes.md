# FFmpeg 剪辑速查（video-editor）

本技能「拼接 / 转场 / 混音 / 竖屏封装 / 静音检测 / 抽帧 / 字幕」七类场景的可复制命令。
适用 ffmpeg 4.x–7.x 通用语法；滤镜参数随版本增改，不确定处一律标 `VERIFY BEFORE USE`
并给出核实命令——宁可少写一个参数，也不写编不出来的假参数。

约定：示例中的 `in.mp4` / `out.mp4` 一律为**相对路径**，执行前先 `cd` 到工作目录；默认带 `-y`
（覆盖输出，避免 "Overwrite? [y/N]" 卡住非交互执行）；在 shell 循环 / cron 中调用另加
`-nostdin`，否则 ffmpeg 会吃掉脚本的 stdin。

## Table of Contents

0. 前置自检 / 1. concat demuxer 拼接 / 2. concat 滤镜兜底 / 3. xfade 转场 / 4. BGM 混音
5. 竖屏 1080x1920 / 6. 静音检测与裁剪 / 7. 抽帧 / 8. 字幕烧录与软挂 / 9. 报错处置表

## 0. 前置自检

```bash
ffmpeg -version | head -1                                        # 预期：版本行
ffprobe -v error -show_entries format=duration -of default=nw=1 in.mp4   # 预期：秒数
ffmpeg -filters 2>/dev/null | grep -E " (xfade|amix|subtitles|silencedetect) "
ffmpeg -encoders 2>/dev/null | grep -E " (libx264|aac) "
```

后两条需分别列出 `xfade`/`amix`/`subtitles`/`silencedetect` 与 `libx264`/`aac` 才算功能完整。
缺 `subtitles` = 未编译 libass（字幕烧录不可用）；缺 `libx264` = 无 H.264 编码器（换 `-c:v mpeg4`
或安装含 x264 的构建）。

## 1. 拼接：concat demuxer（无损、最快）

适用：所有片段**编码参数一致**（同一流水线产出），只求首尾相接。

```bash
printf "file 'scene_1.mp4'\nfile 'scene_2.mp4'\nfile 'scene_3.mp4'\n" > clips.txt
ffmpeg -y -nostdin -f concat -safe 0 -i clips.txt -c copy combined.mp4
```

`-f concat` 启用 concat demuxer；`-safe 0` 允许清单出现绝对路径、`..`、空格或特殊字符
（不加则直接报 `Unsafe file name`）；`-c copy` 复制码流，秒级完成且无画质损失。
预期：时长等于各片段之和（±1 帧）。

失败分支：`Unsafe file name` → 加 `-safe 0` 或改相对路径；`Non-monotonous DTS`、音画不同步
→ 片段编码不一致，改用第 2 节；漏片段 → `cat clips.txt` 核对引号与换行。

## 2. 拼接：concat 滤镜（编码不一致时的兜底）

```bash
ffmpeg -y -nostdin -i scene_1.mp4 -i scene_2.mp4 -filter_complex \
  "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]" \
  -map "[v]" -map "[a]" -c:v libx264 -crf 20 -preset medium -c:a aac -b:a 192k combined.mp4
```

`concat=n=2:v=1:a=1` = 2 个输入、输出 1 视频 1 音频；输入必须按 `[v0][a0][v1][a1]` 成对列出。
代价是全片重编码。失败分支：`Stream specifier ':a' ... matches no streams` → 某片段无音轨，
先补静音轨 `ffmpeg -i v.mp4 -f lavfi -i anullsrc=r=44100:cl=stereo -shortest -c:v copy -c:a aac v_a.mp4`。

## 3. 转场：xfade 交叉淡化

```bash
# clip_a 时长 D1，转场时长 T，则 offset = D1 - T（本例 D1=5s, T=0.5s）
ffmpeg -y -nostdin -i clip_a.mp4 -i clip_b.mp4 -filter_complex "\
[0:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,settb=AVTB,fps=30[va];\
[1:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,settb=AVTB,fps=30[vb];\
[va][vb]xfade=transition=fade:duration=0.5:offset=4.5[v]" \
  -map "[v]" -c:v libx264 -crf 20 -pix_fmt yuv420p out.mp4
```

`transition` 取 `fade`/`wipeleft`/`slideup`/`circleopen` 等（完整列表 `ffmpeg -h filter=xfade`）；
`duration` 是重叠时长；`offset` 是转场**在第一个输入上开始的时间点**。三片段时把上次结果
作为下次输入、offset 累计：`[0][1]xfade=duration=0.5:offset=4.5[v01];[v01][2]xfade=duration=0.5:offset=9.0[v]`。

失败分支：`First input link main timebase ... do not match` → 两输入时间基不同，前置 `settb=AVTB`；
宽高/SAR 不匹配 → 前置 `scale=...:force_original_aspect_ratio=decrease,pad=...,setsar=1` 统一；
末尾少一段 → `offset` 算错，用 `ffprobe` 取实际时长重算。

## 4. 混音：BGM + 人声，音量与闪避

```bash
ffmpeg -y -nostdin -i video.mp4 -stream_loop -1 -i bgm.mp3 -filter_complex "\
[1:a]volume=0.25[bgm];\
[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest final.mp4
```

`-stream_loop -1` 让短 BGM 循环（必须写在它所修饰的 `-i` **之前**）；`volume=0.25` 是线性增益
倍数（不是 dB）；`duration=first` 以第一路长度为准；`-shortest` 兜底截断。

**音量坑**：`amix` 默认把各路按 1/n 缩放，人声会被压低。想关闭先核实本机是否有该参数：
`ffmpeg -h filter=amix` 看到 `-normalize` 才可用（VERIFY BEFORE USE），有则写
`amix=inputs=2:duration=first:normalize=0`。

人声闪避（说话时自动压 BGM）：`[0:a][bgm]sidechaincompress=threshold=0.05:ratio=6:attack=20:release=250[a]`
——参数名与默认值随版本变化，执行前必须 `ffmpeg -h filter=sidechaincompress` 确认（VERIFY BEFORE USE）。

失败分支：输出无声 → 忘了 `-map "[a]"`，滤镜输出必须显式 map；`Could not find tag for codec mp3`
→ MP4 不装 MP3，本例已用 `-c:a aac` 转码；音画漂移 → 采样率不一致，前置 `aresample=44100`。

## 5. 竖屏：1080x1920 缩放与填充

```bash
# 5a) 留黑边
ffmpeg -y -nostdin -i in.mp4 -vf \
  "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1" \
  -c:v libx264 -crf 20 -preset medium -c:a aac vertical.mp4

# 5b) 模糊背景填充（不留黑边）
ffmpeg -y -nostdin -i in.mp4 -filter_complex "\
[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:2[bg];\
[0:v]scale=1080:1920:force_original_aspect_ratio=decrease[fg];\
[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[v]" \
  -map "[v]" -map 0:a -c:v libx264 -crf 20 -preset medium -c:a aac vertical_blur.mp4
```

`decrease` 等比缩到框内（不裁切）；`increase` 撑满后 `crop` 裁掉溢出；`pad` 的
`(ow-iw)/2:(oh-ih)/2` 是居中偏移；`boxblur=20:2` = 亮度半径:强度；`setsar=1` 归一像素宽高比，
否则部分平台会按 SAR 拉伸播放。

预期：`ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 vertical.mp4`
输出 `1080,1920`。失败分支：`Invalid too big or non positive size` → 源文件宽高异常，先 `ffprobe` 确认。

## 6. 静音段检测与裁剪

```bash
ffmpeg -nostdin -i in.mp4 -af silencedetect=noise=-35dB:d=0.4 -f null - 2> silence.log
grep -E "silence_(start|end)" silence.log
```

预期出现成对行：`silence_start: 3.204` / `silence_end: 5.881 | silence_duration: 2.677`。
结果写在 **stderr**，必须重定向；`-f null -` 不可省，否则会真的生成输出文件；`noise` 是判定阈值
（越小越严格），`d` 是最短判定持续时长。

裁掉首尾静音（保留中间）：

```bash
ffmpeg -y -nostdin -i in.wav -af "\
silenceremove=start_periods=1:start_duration=0.2:start_threshold=-40dB:detection=peak,areverse,\
silenceremove=start_periods=1:start_duration=0.2:start_threshold=-40dB:detection=peak,areverse" trimmed.wav
```

`silenceremove` 只能从**开头**移除；用 `areverse` 倒放处理一次即可裁尾部，最后再 `areverse` 还原。
参数名随版本有差异，执行前先 `ffmpeg -h filter=silenceremove` 核对（VERIFY BEFORE USE）。

## 7. 抽帧

```bash
ffmpeg -y -nostdin -ss 00:00:03 -i in.mp4 -frames:v 1 -q:v 2 frame.png   # 单帧（快）
ffmpeg -y -nostdin -i in.mp4 -vf "fps=1,scale=480:-2" thumb_%04d.jpg      # 每秒 1 张
```

`-ss` 放在 `-i` **前**是快速定位（关键帧精度），放在后是精确但慢；`-frames:v 1` 只取 1 帧；
`-q:v 2` 是 JPEG/PNG 质量（2≈高）；`scale=480:-2` 用 `-2`（而非 `-1`）保证高度为偶数，
H.264 要求偶数边长。

预期：当前目录出现 `frame.png` 或 `thumb_0001.jpg`、`thumb_0002.jpg`……
失败分支：抽到全黑帧 → 时间戳落在片头黑场，把 `-ss` 加大到 1–3 秒重试。

## 8. 字幕：硬烧录与软挂载

```bash
# 8a) 硬烧录（内嵌画面，任何平台都能显示）
ffmpeg -y -nostdin -i in.mp4 -vf "subtitles=subs.srt" -c:v libx264 -crf 20 -c:a copy burned.mp4

# 8b) 指定中文字形与描边
ffmpeg -y -nostdin -i in.mp4 -vf \
  "subtitles=subs.srt:force_style='FontName=Noto Sans CJK SC,FontSize=22,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,Shadow=1,MarginV=60'" \
  -c:v libx264 -crf 20 -c:a copy burned_zh.mp4

# 8c) 软挂载（可开关；MP4 用 mov_text，MKV 用 -c:s srt）
ffmpeg -y -nostdin -i in.mp4 -i subs.srt -c:v copy -c:a copy -c:s mov_text \
  -metadata:s:s:0 language=chi soft.mp4
```

`subtitles=` 走 libass；`force_style` 用 ASS 字段，颜色为 `&HAABBGGRR`（与常见 `#RRGGBB` 相反）；
`MarginV` 是距底部像素；`mov_text` 是 MP4 唯一广泛支持的字幕编码。

中文烧录前置检查（两者任一为空则失败或出方块字）：

```bash
ffmpeg -filters 2>/dev/null | grep " subtitles "   # 有输出 = 编译了 libass
fc-list :lang=zh | head -5                          # 有输出 = 系统装了中文字体
```

失败分支：`No such filter: 'subtitles'` → 缺 libass；`Unable to open subs.srt` → 路径错（相对路径
相对**当前目录**）；中文方块 → `FontName` 不存在，换成 `fc-list :lang=zh` 实际输出的名字；文件名
含空格或冒号 → 用 `subtitles=filename='my subs.srt'` 形式，或改名。

## 9. 报错处置表

| 报错原文（关键片段） | 原因 | 处置 |
|---|---|---|
| `Unsafe file name` | concat 清单用绝对路径/特殊字符且未开 `-safe` | 加 `-safe 0` 或改相对路径 |
| `Could not find tag for codec ... in stream #0` | 容器不支持该编码 | MP4 用 `-c:a aac -c:v libx264` |
| `Unknown encoder 'libx264'` | 该构建无 x264 | `ffmpeg -encoders \| grep 264` 查可用项 |
| `Automatic encoder selection failed` | 未指定编码器且无默认 | 显式 `-c:v` / `-c:a` |
| `Stream mapping:` 后输出缺音轨 | 用滤镜但未 `-map` | 显式 `-map 0:v -map "[a]"` |
| xfade `timebase ... do not match` | 两输入时间基不同 | 前置 `settb=AVTB` |
| `Invalid data found when processing input` | 文件不存在/损坏/扩展名不符 | `ls -l` + `ffprobe -v error -show_format in.mp4` |
| `Too many packets buffered for output stream` | 时间戳错乱或速率差异大 | 加 `-max_muxing_queue_size 1024` 兜底，优先查源时间戳 |
| `silencedetect` 无任何输出 | 结果在 stderr 且漏了 `-f null -` | 重定向 `2> silence.log` |
| 字幕中文方块/乱码 | 缺中文字体或字幕非 UTF-8 | 装 `fonts-noto-cjk`；字幕存 UTF-8（无 BOM 优先） |
| 循环里命令被跳过 | ffmpeg 吃掉 stdin | 加 `-nostdin` |
