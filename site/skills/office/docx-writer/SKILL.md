---
name: docx-writer
description: >
  Generate and audit real Word (.docx) files from a markdown-ish draft or
  structured JSON, with correct heading levels, lists, tables, bold spans,
  and CJK font setup. Use when the user asks to 写文档 / 写个 Word / 生成
  word 文档 / 出一份 docx 报告 / create document / make a Word report /
  export to docx, or wants to inspect or restyle an existing .docx. Do NOT
  use for PDF manipulation (use pdf-pipeline), spreadsheets, or slide decks.
license: Apache-2.0
compatibility: 需要 python3 + python-docx（pip 可装）；无则降级为只产出 markdown
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: office-productivity
  pattern: single-task
  tier: standard
  verified-date: "2026-09-16"
---

# DOCX Writer（Word 文档生成与审读）

把一份结构化草稿变成真正的 .docx：标题层级、列表、表格、粗体一次到位，
并用中文正文字体（宋体/黑体）统一排版。核心判断：**内容源必须是结构化的**，
拿到需求先定大纲再渲染，禁止凭空即兴排版。

## 输入清单

| 输入 | 必填 | 说明 |
|---|---|---|
| 文档主题与用途 | 是 | 写什么、给谁看（报告/纪要/通知/说明书） |
| 内容草稿或要点 | 是 | 用户给的素材；没有则先和用户逐节确认大纲 |
| 目标文件名 | 否 | 默认 `output.docx`，保存在当前工作目录 |
| 是否需要封面标题 | 否 | 默认加 Title 段 |
| 中文字体偏好 | 否 | 默认正文宋体、标题黑体 |

缺输入时，一次性问齐（不要挤牙膏式追问）：

> 请提供：1) 文档主题与用途；2) 内容素材或让我按你给的大纲起草；
> 3) 目标文件名（默认 output.docx）。字体有偏好吗（默认宋体正文/黑体标题）？

## 前置自检

```bash
python3 -c "import docx; print('python-docx ok')"
test -f scripts/docx_ops.py && echo "script ok"
```

- 两条都通过 → 走完整流程（步骤 2 起）。
- 第一条报 `ModuleNotFoundError` → 告知用户 `pip install python-docx`
  可启用 .docx 导出；未经用户同意不要擅自安装，此时降级为只产出
  markdown 草稿并在交付时说明。
- 第二条失败（脚本不在）→ 在当前工作目录用同样功能内联 python-docx
  代码代替，见步骤 3 的等效写法。

## 工作流

### 步骤 1：定大纲与内容源

把内容整理成 markdown-ish 草稿（约定见下表），存为 `content.md`。
这是唯一事实源，后续渲染只是机械执行。

| 草稿语法 | 映射结果 |
|---|---|
| `# / ## / ###` | Heading 1 / 2 / 3 |
| `- ` 或 `* ` 开头 | 项目符号列表 |
| `1. ` 开头 | 编号列表 |
| `\|\|` 分隔的行块 | 表格（首行为表头） |
| `**文字**` | 粗体 run |
| 其余普通行 | 正文段落 |

预期：`content.md` 覆盖全部章节，无空节。
若失败（内容素材不足）：回到输入清单，向用户一次性补问缺失章节。

### 步骤 2：生成 .docx

```bash
python3 scripts/docx_ops.py create --input content.md --output output.docx --title "文档标题"
```

结构化来源（比如程序流水线）可用 JSON：每块 `{"type": "h1|h2|h3|
para|bullet|number|table", "text": "...", "rows": [[...]]}`，
同样走 `create --input content.json`。

预期输出：`created: output.docx`。
若失败：检查草稿语法是否混入全角 `＃`、表格行是否以 `|` 开头；
修正后重跑。

### 步骤 3：统一中文样式

```bash
python3 scripts/docx_ops.py styles output.docx --body-font 宋体 --heading-font 黑体
```

预期输出：`saved: output.docx` 加逐样式清单，每行形如
`Heading 1 -> eastAsia=黑体`。
若失败：字体名必须是 Word 认识的中文字体名（宋体/黑体/楷体/仿宋），
不要填英文名；样式清单为空说明文档没有可改段落样式。

### 步骤 4：读回验证

生成后必须读回检查，不许只看脚本退出码：

```bash
python3 scripts/docx_ops.py inspect output.docx --preview 12
```

预期：段落数/表格数符合草稿；样式统计里标题、列表各就各位；
预览文本无乱码、无丢段。
若失败：常见错位见下方失败处置表；改 `content.md` 后回到步骤 2。

### 步骤 5：交付

告知用户文件绝对路径、章节结构（把 inspect 的样式统计转述成一段话），
并说明：内容源在 `content.md`，后续改动优先改草稿再重渲染。

预期：用户拿到能直接打开的 .docx 与可复用的 `content.md`。
若失败：用户打开后发现排版不符 → 别改 .docx，回到步骤 1 改 `content.md` 后重跑步骤 2-4；
`inspect` 与用户所见不一致 → 以用户所见为准，按失败处置表逐条排查。

## 交付标准

- 产物：一个可被 Word/WPS 打开的 .docx 文件。
- 位置：当前工作目录（或用户指定路径）。
- 完整性验证（三选一，至少做 inspect）：
  - `inspect` 输出的样式统计与草稿大纲一致；
  - `unzip -l output.docx` 里存在 `word/document.xml` 与 `word/styles.xml`；
  - 用户侧能正常打开且标题导航窗格有层级。
- 脚本无残留临时文件；草稿文件在交付说明中提及而非删除。

## 失败处置表

| 现象 | 原因 | 处置 |
|---|---|---|
| 打开后中文全是方块/乱码 | 样式未设 eastAsia 字体，Word 用了默认西文字体 | 跑步骤 3 的 `styles`；验证 `word/styles.xml` 中 `w:eastAsia` 值 |
| 标题不在导航窗格出现 | 标题用了普通段落加粗而非 Heading 样式 | 草稿里必须用 `#` 语法，禁止手工加粗模拟标题 |
| 表格丢失或挤成一列 | 表格行未用 `\|` 开头，或分隔行格式不对 | 每个表格行都以 `\|` 开头，分隔行用 `\|---\|` |
| 大文档生成很慢或卡住 | 段落数上万，逐段 API 调用开销大 | 拆章节分文件生成再人工合并；或精简草稿 |
| 图片丢失 | 本脚本不含图片插入能力 | 用 python-docx 的 `add_picture` 单独补一步，或告知用户图片需后期插入 |
| 打开提示文件损坏 | 生成过程被中断，ZIP 不完整 | 删除后从步骤 2 重新生成，勿手工修补 |

## 参考

- 方法论与来源声明：`references/sources-and-methodology.md`
- 脚本帮助：`python3 scripts/docx_ops.py --help`
