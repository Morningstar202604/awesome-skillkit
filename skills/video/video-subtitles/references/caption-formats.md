# 字幕格式对照（video-subtitles）

四种常用字幕载体：**SRT**（最通用）、**ASS**（要样式就用它）、**VTT**（Web）、
**JSON 逐字时间戳**（程序生成/动画字幕）。每种给最小可运行示例 + 字段说明 +
踩坑点 + ffmpeg 烧录/软挂命令。

## Table of Contents

0. 选型与通用规则 / 1. SRT / 2. ASS / 3. WebVTT / 4. JSON 逐字时间戳
5. 编码与 BOM / 6. ffmpeg 烧录与软挂 / 7. 中文断句规则

## 0. 选型与通用规则

| 格式 | 用途 | 样式能力 | 备注 |
|---|---|---|---|
| SRT | 平台上传、字幕轨软挂 | 无 | 兼容性最好，先做这个 |
| ASS | 硬烧录、特效字幕 | 强（字体/颜色/位置/动画） | 平台上传通常不支持，只用于烧进画面 |
| VTT | 网页播放器、Web 端 | 弱（有限 cue 设置） | 头部必须有 `WEBVTT` |
| JSON 逐字 | "卡拉 OK 式"逐字高亮 | 由渲染端决定 | 无统一标准，schema 以你的工具为准 |

通用规则：时间轴**单调递增**、相邻 cue 不重叠（重叠时部分播放器只显示后一条）；
精度到毫秒且起 < 止；文件统一 UTF-8（BOM 取舍见第 5 节）；中文一条 cue ≤15 字、
最多两行，英文一行 ≤42 字符（经验值，非硬标准）。

## 1. SRT

```
1
00:00:00,000 --> 00:00:03,000
你们猜我花了多少钱？

2
00:00:03,000 --> 00:00:08,000
八千九！就这个？
```

| 元素 | 写法 | 说明 |
|---|---|---|
| 序号 | `1`、`2`… | 从 1 递增；部分解析器忽略，但不要省 |
| 时间行 | `HH:MM:SS,mmm --> HH:MM:SS,mmm` | **毫秒分隔符是英文逗号**，不是点号 |
| 文本 | 1–2 行 | 第三行起多数播放器不认 |
| 分隔 | 空行 | 每条 cue 之间必须有且仅有一个空行，文件末尾也要换行 |

常见坑：写成 `00:00:00.000`（点号）→ 被当成 VTT 解析或直接报错；
最后一条 cue 后没空行 → 部分解析器丢最后一条；写 `\n` 字面量不会换行，必须真换行。

## 2. ASS

```
[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Noto Sans CJK SC,64,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,3,1,2,60,60,120,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:03.00,Default,,0,0,0,,你们猜我花了多少钱？
Dialogue: 0,0:00:03.00,0:00:08.00,Default,,0,0,0,,八千九！就这个？
```

| 字段 | 含义 |
|---|---|
| `PlayResX/Y` | 逻辑分辨率，坐标与字号基于它；竖屏设 `1080` / `1920` |
| `Fontsize` | 基于 PlayRes 的字号；1080 宽竖屏 56–72 较常见（经验值） |
| `PrimaryColour` | 主体色，格式 `&HAABBGGRR`（**与 `#RRGGBB` 通道相反**） |
| `Outline` / `Shadow` | 描边/阴影宽度（像素）；黑底白字 `3` / `1` 起步 |
| `Alignment` | 小键盘方位：1=左下 2=下中 3=右下 5=正中；竖屏常用 `2` |
| `MarginV` | 垂直边距；竖屏底部要给平台 UI 留 200+ 像素 |
| `Start` / `End` | `H:MM:SS.cc`，**百分秒两位**，不是毫秒 |

常见坑：时间写三位毫秒（`0:00:03.000`）→ ASS 只认两位百分秒，会解析错；
缺 `[V4+ Styles]` 或 `Format:` 行 → 解析直接失败；字体名系统里不存在 → 中文变方块，
用 `fc-list :lang=zh` 取真实名字。

## 3. WebVTT

```
WEBVTT

1
00:00:00.000 --> 00:00:03.000 line:85% align:center
你们猜我花了多少钱？

2
00:00:03.000 --> 00:00:08.000 line:85% align:center
八千九！就这个？
```

| 元素 | 写法 | 说明 |
|---|---|---|
| 文件头 | `WEBVTT`（首行） | **必须有**，缺了整个文件不生效 |
| 时间 | `HH:MM:SS.mmm` 或 `MM:SS.mmm` | **毫秒分隔符是点号**（与 SRT 相反） |
| Cue 设置 | 追加在时间行末尾 | 常用 `line:85%`、`position:50%`、`align:center` |
| 序号 | 可选 | 写了无害 |

常见坑：把 SRT 改扩展名当 VTT 用 → 逗号毫秒 + 缺 `WEBVTT` 头，播放器静默不显示。

## 4. JSON 逐字时间戳

**没有统一标准**。下面是一种常见形态，字段名必须与你的 ASR / 渲染工具一致
（**VERIFY BEFORE USE**：先跑一次你的工具看它实际输出什么，再照抄它的 schema）。

```json
{
  "duration": 8.0,
  "cues": [
    {
      "index": 1,
      "start": 0.0,
      "end": 3.0,
      "text": "你们猜我花了多少钱？",
      "words": [
        {"word": "你们", "start": 0.10, "end": 0.42},
        {"word": "猜",   "start": 0.42, "end": 0.58},
        {"word": "我",   "start": 0.58, "end": 0.70}
      ]
    }
  ]
}
```

`start`/`end` 用浮点秒（不要写 `HH:MM:SS` 字符串，浮点更好算）；`words[].start/end`
是单字或词的时间，用于逐字高亮，中文按**词**切比按字更自然。

生成后自检（防止时间轴错乱，失败就不要继续下游）：

```bash
python3 - <<'PY'
import json
d, prev = json.load(open("subs.json")), -1.0
for c in d["cues"]:
    assert prev <= c["start"] < c["end"], f"时间轴异常: {c}"
    prev = c["end"]
print("OK cues =", len(d["cues"]))
PY
```

预期输出 `OK cues = N`。

## 5. 编码与 BOM

**首选 UTF-8 无 BOM**。BOM 是兼容性问题的主要来源：部分解析器把 BOM 当成第一条
cue 的一部分，表现为"第一条字幕不显示"或"首行乱码"。

```bash
# 检测：前 3 字节 EF BB BF 即带 BOM
head -c 3 subs.srt | xxd
file subs.srt            # 含 "with BOM" 即带 BOM

# 去 BOM（先备份，原地改写）
cp subs.srt subs.srt.bak
python3 -c "
import pathlib
p = pathlib.Path('subs.srt')
p.write_bytes(p.read_bytes().lstrip(b'\xef\xbb\xbf'))"

# 源为 GBK 时转码：iconv -f GBK -t UTF-8 subs_gbk.srt > subs.srt
```

例外：个别 Windows 端旧工具反而要 BOM 才认中文——先试无 BOM，
第一条不显示或首行乱码时再补 BOM。

## 6. ffmpeg 烧录与软挂

```bash
# 硬烧录（任何平台都能看到）
ffmpeg -y -i in.mp4 -vf "subtitles=subs.srt" -c:v libx264 -crf 20 -c:a copy burned.mp4

# 硬烧录并覆盖样式（SRT 也能用，force_style 走 ASS 字段）
ffmpeg -y -i in.mp4 -vf \
  "subtitles=subs.srt:force_style='FontName=Noto Sans CJK SC,FontSize=64,PrimaryColour=&H00FFFFFF,Outline=3,MarginV=200'" \
  -c:v libx264 -crf 20 -c:a copy burned_zh.mp4

# 软挂到 MP4（可开关；mov_text 不支持 ASS 样式）
ffmpeg -y -i in.mp4 -i subs.srt -c:v copy -c:a copy -c:s mov_text \
  -metadata:s:s:0 language=chi soft.mp4

# 软挂到 MKV（保留 ASS 样式用 -c:s ass，纯文本用 -c:s srt；WebVTT 进 WebM 用 -c:s webvtt）
ffmpeg -y -i in.mp4 -i subs.ass -c:v copy -c:a copy -c:s ass soft.mkv
```

前置检查（缺任一项则烧录失败或出方块字）：

```bash
ffmpeg -filters 2>/dev/null | grep " subtitles "   # 有输出 = 编译了 libass
fc-list :lang=zh | head -5                          # 有输出 = 有中文字体
```

失败分支：`No such filter: 'subtitles'` → 缺 libass，改走软挂或换构建；
`Unable to open subs.srt` → 路径错（相对路径相对**当前目录**）；
容器不支持该字幕编码 → MP4 用 `mov_text`，MKV 用 `srt`/`ass`。

格式互转（转换后必查头部与实际播放效果，工具不保证时间轴零误差）：
`ffmpeg -y -i subs.srt subs.vtt` / `ffmpeg -y -i subs.srt subs.ass`。

## 7. 中文断句规则

| 规则 | 取值（经验值） | 理由 |
|---|---|---|
| 单条 cue 字数 | ≤15 字 | 竖屏一行放不下更多，超过就断成两条 |
| 单行行数 | ≤2 行 | 三行会盖住画面主体 |
| 最短显示时长 | ≥0.8s | 短于 0.8s 来不及读，等于没加 |
| 最长显示时长 | ≤6s | 超过说明该断句了 |
| 相邻 cue 间隔 | 0.1–0.3s | 留间隙避免"连闪"，但不影响阅读 |

断句位置：优先在标点（，。！？）处断，其次在主谓/动宾之间断；
**不要**把词从中间劈开（"我花八千/九百"错，"我花了八千九/买了这个"对）。
