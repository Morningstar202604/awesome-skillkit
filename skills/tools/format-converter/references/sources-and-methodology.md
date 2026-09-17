# 方法论来源与设计取舍

> 何时读：想新增一条转换管线、调整依赖探测行为，或理解"为什么跨管线转换被拒绝"时读本文件。
> CLI 参数见 SKILL.md，此处只讲设计依据。

## 思想来源（公开方法论蒸馏，非代码搬运）

| 本脚本的做法 | 蒸馏自的思想 |
|--------------|--------------|
| 依赖先探测、缺失给安装命令 | Unix `autoconf`/`./configure` 的"能力探测再决定"传统；现代 CLI 的 actionable error 理念（错误信息里直接给出修复动作） |
| 一条命令多个子命令 | `git` / `docker` / `ffmpeg` 的子命令组织法：减少用户记忆的顶层入口，把差异收进子命令 |
| 拒绝输入输出同路径 | `mv`/`cp` 保护机制的显式化；"源与目标同一文件"是数据丢失的经典事故 |
| 批量默认 dry-run | 与同域 file-organizer 保持一致的操作契约（见该技能 `references/`） |
| 按扩展名推断管线 | `pandoc` 的格式自动识别、`ImageMagick` 的输出格式推断——但本脚本把推断结果**显式打印**，避免静默猜错 |

## 关键取舍

**为什么拒绝跨管线转换？** `.mp4 → .jpg` 实际是**抽帧**（需选时间点、选第几帧），
`.md → .jpg` 实际是**渲染**（需排版引擎）。这两件事的语义与"换个容器格式"完全不同：
前者有无限种合理结果，后者依赖浏览器/LaTeX 环境。放进同一个 `batch` 会产出用户不想要的垃圾。
拒绝比猜错好——错误信息里直接给出正确做法（`ffmpeg -frames:v 1`）。

**为什么 `-f`/`-t` 要显式传给 pandoc？** pandoc 对 `.tex`、`.rst` 的自动识别在部分版本上
不一致，且 `-t latex` 与 `-t pdf` 的行为差异大（后者需要外部 LaTeX 引擎）。显式传参让
脚本行为跨版本稳定，也让打印出来的命令可被用户直接复制复现。

**为什么批量模式单个失败不中断？** 批量场景下用户关心的是"100 个文件里坏了几个"，
而不是"第 3 个坏了所以全部白跑"。失败项逐个打印并在结尾计数，用户可只重跑失败的那几个。

**为什么 `--kind` 手动覆盖存在？** 扩展名→管线的映射表是硬编码的闭集：遇到未登记的新格式
（如 `.avif`、`.heic` 的不同实现），用户可用 `--kind image` 强制走某条管线，无需改脚本。

## 官方文档

- pandoc 用户指南（`-f`/`-t`、`--pdf-engine`）：<https://pandoc.org/MANUAL.html>
- pandoc 支持的格式清单：<https://pandoc.org/MANUAL.html#option--list-input-formats>
- Pillow `Image.resize`（`LANCZOS` 重采样）：<https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.resize>
- Pillow `Image.save` 与 `quality` 参数：<https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#jpeg>
- Pillow 模式转换（RGBA → RGB）：<https://pillow.readthedocs.io/en/stable/handbook/concepts.html#concept-modes>
- FFmpeg 官方文档：<https://ffmpeg.org/ffmpeg.html>
- FFmpeg 编解码器选择指南：<https://trac.ffmpeg.org/wiki/Encode/H.264>
