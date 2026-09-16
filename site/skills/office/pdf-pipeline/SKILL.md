---
name: pdf-pipeline
description: >
  Page-level PDF processing: merge multiple PDFs, split by page ranges,
  extract text with page tags, read/write metadata, rotate pages, and
  probe AcroForm fields or detect scanned (no text layer) files. Use when
  the user asks to 合并 PDF / 拆分 PDF / 提取 PDF 文字 / rotate pages /
  merge PDFs / split a PDF / pdf 元数据. Do NOT use for generating Word
  documents (use docx-writer), editing slide decks, or image editing.
license: Apache-2.0
compatibility: 需要 python3 + pypdf（pip 可装）；无则只能给出操作思路与命令清单
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: office-productivity
  pattern: single-task
  tier: standard
  verified-date: "2026-09-16"
---

# PDF Pipeline（PDF 页级处理流水线）

对已有 PDF 做合并、拆分、取文、改元数据、旋转这五类页级操作。
核心判断：**先判定 PDF 类型**——文本型直接处理；扫描型（无文本层）
先走 OCR；表单型用字段探测确认结构再动手。

## 输入清单

| 输入 | 必填 | 说明 |
|---|---|---|
| PDF 文件路径 | 是 | 一个或多个；相对路径基于当前工作目录 |
| 要做的操作 | 是 | merge / split / extract / meta / rotate |
| 目标文件名 | 否 | merge/rotate 必填 `--output`；meta 缺省原地写 |
| 页码范围 | 否 | `1-3,5` 这种 1-based 写法，缺省全部页 |

缺输入时，一次性问齐：

> 请提供：1) PDF 文件路径；2) 要做什么（合并/拆分/提取文字/改元数据/旋转）；
> 3) 输出文件名；4) 若是拆分或提取：页码范围（缺省全部页）。

## 前置自检

```bash
python3 -c "import pypdf; print('pypdf ok')"
test -f scripts/pdf_ops.py && echo "script ok"
```

- 两条都通过 → 按工作流执行。
- 第一条报 `ModuleNotFoundError` → 提示用户 `pip install pypdf`；
  未经同意不要自行安装，此时只输出操作方案不产出文件。
- 第二条失败 → 按 `references/sources-and-methodology.md` 里的 pypdf
  文档链接内联等价代码。

## 工作流

### 步骤 1：判定 PDF 类型（决定走哪条线）

```bash
python3 scripts/pdf_ops.py meta input.pdf
```

预期输出：页数、元数据、`form fields: ...` 三段。判读：

- `form fields` 列出字段 → 表单 PDF：先与用户确认是"只读字段结构"
  还是"要填值"；填值超出本技能范围，给出字段清单后转告用户用专业
  表单工具，不要猜值硬填。
- 需要提取文字时先跑步骤 4 的 `extract` 探测文本层。

预期：一段明确结论（文本型 / 扫描型 / 表单型）。
若失败（文件读不开）：大概率加密或损坏，见失败处置表。

### 步骤 2：文本型——合并 / 拆分 / 旋转

```bash
python3 scripts/pdf_ops.py merge a.pdf b.pdf --output merged.pdf
python3 scripts/pdf_ops.py split merged.pdf --ranges "1-2,3" --outdir split_out
python3 scripts/pdf_ops.py rotate merged.pdf --degrees 90 --pages 1-2 --output rotated.pdf
```

预期：merge 打印逐文件页数与总页数；split 逐文件列出输出路径；
rotate 打印被旋转的页号。
若失败：页码范围越界会报 `out of bounds`，先用 meta 的页数核对范围。

### 步骤 3：扫描型——OCR 转线提示

`extract` 对无文本层的文件会输出 `[warn] no text layer ...` 到 stderr。
确认是扫描件后，本脚本止步，转 OCR 路线（提示用户）：

- `ocrmypdf in.pdf out.pdf`（生成可搜索文本层，之后回到步骤 2/4）
- 纯取字可用 `tesseract in.pdf out -l chi_sim+eng`
- OCR 质量依赖扫描分辨率，300dpi 以下效果差，需向用户说明。

预期：用户确认后才执行外部 OCR 命令；本技能不代装 OCR 工具。

### 步骤 4：提取文本（带页码标注）

```bash
python3 scripts/pdf_ops.py extract merged.pdf --pages 1-2 --output out.txt
```

预期：每页以 `=== page N/M ===` 起头；stdout 直出或写入 `out.txt`。
若失败：提取出乱码多为内嵌字体缺 ToUnicode 映射（见处置表）。

### 步骤 5：读/写元数据

```bash
python3 scripts/pdf_ops.py meta merged.pdf                          # 只读
python3 scripts/pdf_ops.py meta merged.pdf --set Title="Q3 报告" \
    --set Author="团队名" --output final.pdf                        # 写入
```

预期：写入后打印逐键清单；可再跑一次只读版读回验证。
若失败：键名限 Title/Author/Subject/Keywords/Creator/Producer。

### 步骤 6：交付

报出每个产物路径 + 页数，并用一句话说明来源（哪个文件、哪些页）。
写操作默认不覆盖原文件（rotate/split/merge 都要求显式 `--output`），
原地写（meta 缺省）要先提醒用户已备份或确认。

## 交付标准

- 产物：新 PDF 文件或文本文件，均在用户可见路径。
- 验证：页级操作后用 `meta` 读回页数核对；文本提取抽查首尾页内容
  与页码标注；rotate 后可读 `/Rotate` 标志确认。
- 多文件合并时逐个报出来源页数，方便用户对账。

## 失败处置表

| 现象 | 原因 | 处置 |
|---|---|---|
| 提取出乱码或空白但非扫描件 | 内嵌字体缺 ToUnicode 映射 | 提示用户换 pdfminer.six 重提，或对页面截图走 OCR |
| 打开报"未解密/密码保护" | PDF 有用户口令或权限限制 | 让用户提供口令；不带口令硬解属违规，直接拒绝 |
| merge 后页序不对 | 输入文件顺序与预期不一致 | 核对命令行里文件名顺序，merge 按参数顺序拼接 |
| 拆分报页码越界 | 范围超出实际页数 | 先 `meta` 看页数，改用 `1-N` 写法 |
| 大文件合并慢 | 页级对象逐一拷贝 | 正常现象，告知进度；超过 10 分钟建议分批合并 |
| 旋转后查看器里方向没变 | 部分查看器缓存旧渲染 | 重新打开文件；用读回 `/Rotate` 标志确认已写入 |

## 参考

- 方法论与来源声明：`references/sources-and-methodology.md`
- 脚本帮助：`python3 scripts/pdf_ops.py --help`
