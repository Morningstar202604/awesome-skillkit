---
name: pdf-pipeline
description: "学术论文 PDF 后处理流水线工具。当需要把多个 PDF 合并成投稿包、拆分章节/ supplementary、提取参考文献页或图表页、修正元数据（标题/作者/关键词）、旋转页面、加水印/盲审匿名化、批量压缩以满足投稿系统大小限制时使用。适配 academic-format-guardian，负责 PDF 合并/拆分/提取/元数据/旋转/压缩/匿名化的规范操作与质量校验。也用于 合并 PDF / 拆分 PDF / 提取 PDF 文字 / pdf 元数据 / rotate pages / merge PDFs / split a PDF。不用于生成 Word 文档（docx-writer）、编辑幻灯片或图像处理。"
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

# PDF Pipeline（PDF 投稿页级处理流水线）

对已有 PDF 做合并、拆分、取文、改元数据、旋转这五类页级操作。
核心判断：**先判定 PDF 类型**——文本型直接处理；扫描型（无文本层）
先走 OCR；表单型用字段探测确认结构再动手。

本 skill 供「格式规范卫士」（academic-format-guardian）使用。投稿系统拒收的原因里，PDF 后处理问题占一大类：页数不对、合并顺序错、元数据里留着真名（盲审穿帮）、文件超 20MB、章节顺序乱。本 skill 把 PDF 操作标准化，每步可回查。

## 这是什么

覆盖六类操作：
1. **合并**：正文 + supplementary + 推荐审稿人信，按投稿系统要求顺序拼成一个或多个 PDF。
2. **拆分**：从合订本里抽出某几页做单独材料（如 Graphical Abstract、封面、 highlights 页）。
3. **提取**：从 PDF 里抽文字/图片/表格页，做引用核对、查重前自查。
4. **元数据**：查看/写入 PDF 文档属性（Title/Author/Subject/Keywords），盲审前必须清空 Author。
5. **匿名化**：删除批注、隐藏图层、元数据、链接里的身份信息。
6. **压缩**：在不糊文字的前提下把文件压到投稿系统限制内。

页级脚本另覆盖**旋转**（rotate）与表单字段探测（AcroForm probe）。

## 何时使用

- 投稿前组装最终 PDF 包。
- 盲审版制作（要匿名）。
- 从期刊模板 PDF 里抽某页格式参考。
- 文件超大被投稿系统退回。
- 团队 W5 投稿定稿、W1 Phase 8 交付前。
- 不用于生成 Word 文档、编辑幻灯片或图像处理。

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
python3 scripts/pdf_ops.py meta assets/sample.pdf   # 随包样例 PDF；你的真实文件换成 input.pdf
```

预期输出：页数、元数据、`form fields: ...` 三段。判读：

- `form fields` 列出字段 → 表单 PDF：先与用户确认是"只读字段结构"
  还是"要填值"；填值超出本技能范围，给出字段清单后转告用户用专业
  表单工具，不要猜值硬填。
- 需要提取文字时先跑步骤 4 的 `extract` 探测文本层。

预期：一段明确结论（文本型 / 扫描型 / 表单型）。
若失败（文件读不开）：大概率加密或损坏，见失败处置表。

同时按方法论层盘点所有源 PDF 及页数、是否扫描件、是否加密；扫描件无法直接抽文字，需 OCR，单独标注。

### 步骤 2：文本型——合并 / 拆分 / 旋转

```bash
python3 scripts/pdf_ops.py merge a.pdf b.pdf --output merged.pdf
python3 scripts/pdf_ops.py split merged.pdf --ranges "1-2,3" --outdir split_out
python3 scripts/pdf_ops.py rotate assets/sample.pdf --degrees 90 --pages 1-2 --output rotated.pdf   # 随包样例；你的真实场景用上一步的 merged.pdf
```

预期：merge 打印逐文件页数与总页数；split 逐文件列出输出路径；
rotate 打印被旋转的页号。
若失败：页码范围越界会报 `out of bounds`，先用 meta 的页数核对范围。

合并/拆分纪律：合并前先按页号排序，输出后抽查首页、接缝页、末页；拆分保留原页码标注，避免"supp 第 3 页"对不上。

### 步骤 3：扫描型——OCR 转线提示

`extract` 对无文本层的文件会输出 `[warn] no text layer ...` 到 stderr。
确认是扫描件后，本脚本止步，转 OCR 路线（提示用户）：

- `ocrmypdf in.pdf out.pdf`（生成可搜索文本层，之后回到步骤 2/4）
- 纯取字可用 `tesseract in.pdf out -l chi_sim+eng`
- OCR 质量依赖扫描分辨率，300dpi 以下效果差，需向用户说明。

预期：用户确认后才执行外部 OCR 命令；本技能不代装 OCR 工具。
若失败：用户机器上没有 `ocrmypdf`/`tesseract` → 给出安装命令（`pip install ocrmypdf`、
`brew install tesseract tesseract-lang`）并说明本技能不代装，请用户装好或改用其他路径；
OCR 结果仍是乱码 → 扫描分辨率不足或语言包缺失，回到步骤 2 换成"先截图再 OCR"。

### 步骤 4：提取文本（带页码标注）

```bash
python3 scripts/pdf_ops.py extract merged.pdf --pages 1-2 --output out.txt
```

预期：每页以 `=== page N/M ===` 起头；stdout 直出或写入 `out.txt`。
若失败：提取出乱码多为内嵌字体缺 ToUnicode 映射（见处置表）。

### 步骤 5：读/写元数据

```bash
python3 scripts/pdf_ops.py meta assets/sample.pdf                          # 只读（随包样例）
python3 scripts/pdf_ops.py meta merged.pdf --set Title="Q3 报告" \
    --set Author="团队名" --output final.pdf                        # 写入
```

预期：写入后打印逐键清单；可再跑一次只读版读回验证。
若失败：键名限 Title/Author/Subject/Keywords/Creator/Producer。

### 步骤 6：交付

报出每个产物路径 + 页数，并用一句话说明来源（哪个文件、哪些页）。
写操作默认不覆盖原文件（rotate/split/merge 都要求显式 `--output`），
原地写（meta 缺省）要先提醒用户已备份或确认。

预期：每个产物路径都由 `meta` 读回核对过页数，用户能对着来源页号自行抽查。
若失败：产物路径写不出来（如用户只要 stdout 结果）→ 直接把 stdout 内容作为交付物，
说明"未落盘"；用户对页数有异议 → 回到对应步骤重跑并附上 `meta` 读回结果。

## 核心步骤：投稿场景方法论

1. **先盘点再动手**：列出所有源 PDF 及页数、是否扫描件、是否加密；扫描件无法直接抽文字，需 OCR，单独标注。
2. **确定输出清单**：投稿系统通常要哪些文件（Main manuscript / Supplementary / Cover letter / Figures separate），一个都不能错。
3. **合并/拆分**（推荐 pypdf / qpdf / pdftk 脚本化操作，不用手工拖）：合并前按页号排序，输出后抽查首页、接缝页、末页；拆分保留原页码标注。
4. **元数据与匿名化**：用脚本读出现有元数据，盲审版把 Author/Creator/Producer 清空或改为占位；删除批注、附件、隐藏图层；检查文档属性里是否还有机构名、邮箱；首页脚注、致谢、自引段落按盲审规则涂黑或删除。
5. **压缩**：先判断瓶颈是图还是全文；图大图多就回 figure-maker 重出低 dpi 版本（文字图必须保留矢量），再用 ghostscript 重采样；压缩后文字层必须可选中、不糊。
6. **交付前质检**：页数、文件大小、文件命名（按投稿系统要求 `LastName_FirstInitial_JournalName_ManuscriptID.pdf`）；打开全文翻一遍：图位、表位、页眉页脚、页码连续。

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

## 清单

- [ ] 源 PDF 清单与页数已登记，扫描件已标注需 OCR。
- [ ] 输出文件清单与投稿系统要求一一对应。
- [ ] 合并/拆分后接缝页、首页、末页已抽查。
- [ ] 元数据 Title/Author/Keywords 已核对；盲审版 Author 已清空。
- [ ] 批注、附件、隐藏图层已删除，无身份残留。
- [ ] 文件大小在投稿系统上限内，文字层仍可选中复制。
- [ ] 文件命名符合该刊投稿要求。
- [ ] 终版全文通读一遍，页码连续、图表无错位。

## 易错点

- **用打印扫描件冒充可检索 PDF**：投稿系统查重、审稿人复制都要文字层；扫描件必须先 OCR。
- **盲审只删首页名字**：元数据 Author、文档属性、批注、论文里致谢段、自引"我们前期工作[12]"都可能穿帮。
- **合并后页码断裂**：不同来源 PDF 自带页码样式不一，合并后要么统一重排，要么在衔接处明确标注。
- **压缩过头**：ghostscript 默认档把矢量图压成模糊位图，放大就糊；文字类线条图务必保留矢量。
- **忘记密码/加密**：加密 PDF 投稿系统读不出来；交付前确认输出文件未加密。
- **手工 GUI 操作不留记录**：合并拆分手工拖一次，下次改顺序又重来；写成脚本可复现。

## 参考

- 方法论与来源声明：[references/sources-and-methodology.md](references/sources-and-methodology.md)
- 脚本帮助：`python3 scripts/pdf_ops.py --help`
