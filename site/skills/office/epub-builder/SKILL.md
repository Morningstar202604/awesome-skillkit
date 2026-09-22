---
name: epub-builder
description: >
  Convert a Markdown manuscript into a valid EPUB 3 e-book with correct
  mimetype/container.xml/content.opf/toc.ncx/nav.xhtml structure, then read the
  EPUB back to verify metadata and chapter order. Uses only the Python standard
  library because EPUB is just a zip plus XML. Use when the user asks to
  生成 epub / 把 markdown 做成电子书 / 转成 epub 电子书 / 检查这个 epub 文件 /
  电子书章节拆分 / build an epub / make an e-book from markdown / inspect an
  epub file. Do NOT use for Word documents (use docx-writer) or PDF generation
  (use pdf-pipeline).
license: Apache-2.0
compatibility: 需要 python3 3.8+；脚本纯标准库（zipfile + ElementTree），无第三方依赖。
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: office
  pattern: single-task
  tier: standard
  verified-date: "2026-09-17"
---

# EPUB Builder（电子书生成）

把一份 Markdown 原稿打成**能被阅读器接受的** EPUB 3。EPUB 本质就是
「一个 zip + 一组 XML」，所以本技能只用 Python 标准库：`zipfile` 打包、
手写 OPF/NCX/NAV，Markdown 转换用内置的轻量解析器。

核心判断：**规范细节决定成败**。EPUB 有一处硬性要求——
`mimetype` 必须是 zip 里的**第一个**条目且**不压缩**（`ZIP_STORED`），
内容恰为 `application/epub+zip` 且不带换行。做错这一条，
多数阅读器会直接拒收，而文件看起来「生成成功」。
因此本技能把校验内建进 `build`，并在 `inspect` 里可复查。

本技能**不做** Word（用 `docx-writer`）、**不做** PDF（用 `pdf-pipeline`），
也**不做**排版美化（EPUB 的样式由阅读器决定，过度指定样式反而在不同设备上崩版）。

## 输入清单

| 输入 | 必需 | 默认 | 说明 |
|---|---|---|---|
| Markdown 源文件 | 是 | — | 首个 H1 作为书名与首章标题 |
| 书名 | 否 | 首个 H1 或文件名 | 写入 `dc:title` |
| 作者 | 否 | 佚名 | 写入 `dc:creator` |
| 语言 | 否 | `zh` | 写入 `dc:language`，影响断字与朗读 |
| 输出路径 | 否 | `book.epub` | 单文件产物 |

缺输入时，一次性问齐：

> 请提供：① Markdown 文件在哪？② 书名与作者（不给我就取首个 H1 和「佚名」）？
> ③ 输出文件名（默认 book.epub）？④ 有封面图吗（本技能不插图，需要则说明）？

## 前置自检

逐条执行，任一失败 → 按处置动作做：

```bash
# 1. Python 版本（需 3.8+）
python3 --version
# 预期：Python 3.8+。失败→STOP。

# 2. 脚本可用
# 自检：python3 scripts/epub_build.py --help 应打印 build/inspect 用法（以 # 开头不作为场景命令执行）
# 预期：script ok。失败→核对 scripts/ 路径。

# 3. 源文件存在且非空
test -s <input.md> && head -3 <input.md>
# 预期：能看到内容。失败→脚本会报「是空文件」，先找用户要原稿。

# 4. 章节结构可用（有几个 H1？）
grep -c '^# ' <input.md>
# 预期：≥1。0 个 → 脚本会把整篇当作单章「正文」，不报错但导航只有一项。
```

## 工作流

### 步骤 1：确认章节结构

**一级标题（H1）即章节边界**，这是本技能的切分约定：

| Markdown | 变成什么 |
|---|---|
| `# 标题` | 新章节；成为章节文件名与目录项 |
| `## / ###` | 章内小节（保留为 h2/h3） |
| 文档开头的 H1 之前的内容 | 「前言」章（若非空） |
| 完全没有 H1 | 整篇作为单章「正文」 |
| 章节内的 H1 | 丢弃（章名已是 H1，避免重复） |

- **预期**：能列出章节清单，章节名适合做文件名。
- **若失败**：只有一个 H1 但内容很长 → 提示用户用 H2 分节、
  或按内容拆成多个 H1；**不要**擅自改用户的结构。

### 步骤 2：生成 EPUB

```bash
python3 scripts/epub_build.py build references/sources-and-methodology.md --out book.epub --title "书名" --author "作者名"   # 真实输入示例：包内 sources-and-methodology.md；你的书稿换成 input.md
```

产出结构（符合 EPUB 3 规范）：

```
mimetype                    ← 第一条目，STORED 不压缩
META-INF/container.xml      ← 指向 OPF
OEBPS/content.opf           ← manifest + spine（章节顺序以 spine 为准）
OEBPS/toc.ncx               ← EPUB2 兼容目录（老阅读器）
OEBPS/nav.xhtml             ← EPUB3 原生目录
OEBPS/style.css             ← 最小样式
OEBPS/chap01-*.xhtml …      ← 每章一个文件
```

- **预期**：输出书名、作者、章节数与逐章清单，并在结尾打印
  `mimetype : 第一个条目=True 存储方式=STORED ✓`。这一行是规范自检，必须为 ✓。
- **若失败**：若出现 `✗ 违反 EPUB 规范`，说明打包顺序或压缩方式被改坏，
  不要交付该文件，检查 `write_epub()` 是否先写了 mimetype。

### 步骤 3：读回验证

```bash
python3 scripts/epub_build.py inspect examples/sample.epub   # 随包样例（真实产物）；你构建的 book.epub 同样如此验证
```

检查元数据、**按 spine 顺序**的章节清单、以及 `toc.ncx` / `nav.xhtml` 是否齐备。
章节顺序之所以读 spine 而不是遍历 manifest，是因为 manifest 顺序无规范保证，
spine 才是阅读器的实际读取顺序。

- **预期**：元数据四项齐全；章节数等于步骤 2 报的章节数；两份目录都在。
- **若失败**：章节数为 0 → OPF 的 spine 为空，检查 `content_opf()` 的 itemref 生成。

### 步骤 4：独立交叉验证（推荐做）

不要只信自己脚本的结论，用 `zipfile` 直接核对规范：

```bash
python3 -c "
import zipfile
z = zipfile.ZipFile('book.epub'); i = z.infolist()[0]
print('① 第一个条目是 mimetype :', i.filename == 'mimetype')
print('② 未压缩(ZIP_STORED)    :', i.compress_type == zipfile.ZIP_STORED)
print('③ 内容精确匹配          :', z.read('mimetype') == b'application/epub+zip')
print('④ 条目数                :', len(z.namelist()))
"
```

- **预期**：前三项全 `True`（`③` 的字节串不带换行）。
- **若失败**：任一为 `False` → 该 EPUB 不合规，按步骤 2 的失败分支处理。

### 步骤 5：交付

说明：文件**绝对路径**、书名/作者/语言、章节数、`mimetype` 合规结论，
以及一个提醒——**本技能不插图、不加封面**，需要封面要另做
（应改用带图片支持的方案，或在 EPUB 生成后用专门工具追加）。

## 交付标准

- 产物：一个 `.epub` 文件，可被主流阅读器（Calibre / Apple Books / 多看）打开。
- 位置：用户指定的 `--out` 路径；默认当前目录 `book.epub`。
- 完整性验证（必须全做）：
  - `build` 结尾的 `mimetype` 自检行为 `✓`；
  - `inspect` 的章节数等于源文件的 H1 数（无 H1 时为 1）；
  - 交叉验证中「第一个条目是 mimetype」「未压缩」「内容精确匹配」三项均为 `True`。
- 交付说明里要交代章节切分依据（H1），因为用户下次改稿需要按同一规则写。

## 失败处置表

| 现象 / 错误 | 原因 | 处置 |
|---|---|---|
| `Markdown 文件不存在：...` | 路径拼错 | 核对路径；注意是 `.md` 不是 `.docx` |
| `... 是空文件` | 源文件零字节 | 确认原稿已保存内容 |
| `没有解析出任何章节` | 切分后无有效章节 | 极少见；检查源文件是否只有空白 |
| `... 不是合法 zip/EPUB` | 传给 inspect 的不是 EPUB | 确认文件后缀与实际内容一致（改名的 txt 也过不了） |
| 阅读器提示「无法打开」 | mimetype 顺序或压缩方式错 | 跑交叉验证三项；本脚本按规范写，若失败说明打包逻辑被改 |
| 目录为空但章节有内容 | spine 缺 itemref | 检查 `content_opf()` 的 spine 生成 |
| 章节顺序与预期不符 | 依赖了 manifest 顺序 | manifest 顺序无规范保证，章节顺序以 spine 为准 |
| 章名重复导致文件覆盖 | 两个 H1 同名 | `slugify` 会加序号前缀（`chap01-`、`chap02-`），不会覆盖；但要提醒用户改名 |
| 中文标题在旧阅读器乱码 | 编码声明缺失 | 每个 XHTML 都带 `<meta charset="utf-8"/>`；若仍乱码属阅读器问题 |
| 需要封面/插图 | 本脚本不含图片支持 | 明确告知不含；建议改为生成 HTML 后由专门工具加工，不要假装支持 |
| 表格/代码在阅读器里变形 | 阅读器覆盖了样式 | EPUB 样式由阅读器主导，属预期行为；只保证文本结构正确 |

## 参考

- `references/sources-and-methodology.md` —— EPUB 3 规范的三个硬性要点、
  Markdown 解析取舍、以及为什么只用标准库。
- `scripts/epub_build.py --help` —— build / inspect 两个子命令。
- 相关技能：`docx-writer`（Word 文档）、`pdf-pipeline`（PDF 处理）、
  `article-drafter`（先写稿再成书）。
