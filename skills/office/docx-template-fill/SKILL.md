---
name: docx-template-fill
description: >
  Fill an existing Word template's {{placeholders}} with JSON data, optionally
  append a review note, and keep the original template untouched. Use when the
  user asks to 套模板 / 填模板 / 批量生成合同/报告/通知 docx / fill template /
  populate a docx / 批注修订. Do NOT use for generating a brand-new document
  from scratch (use docx-writer), spreadsheets, or slide decks.
license: Apache-2.0
compatibility: 需要 python3 + python-docx（pip install python-docx）；缺失时降级为"只打印占位符清单"
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: office-productivity
  pattern: script
  tier: standard
  verified-date: "2026-09-20"
---

# DOCX Template Fill（Word 模板填写与批注）

把一份**已有**的 Word 模板里的 `{{占位符}}` 用 JSON 数据填上，并可选追加
一条修订批注。核心判断：**模板已存在、只差数据**才用本技能；要凭空造一份
文档请用 `docx-writer`。

> 红线（SKILL-STANDARD-v2）：默认 **dry-run** 只打印将填什么、不写文件；
> 加 `--apply` 才落到新文件，**源模板永不改动**；零网络、零拷贝。

## 输入清单

| 输入 | 必填 | 说明 |
|---|---|---|
| 模板 .docx | 是 | 含 `{{name}}` 式占位符 |
| 数据 JSON | 是 | key 与占位符同名；缺失 key 会留空并告警 |
| 输出文件名 | apply 时必填 | 默认 `filled.docx` |
| 批注作者/文字 | 否 | `--note-author` / `--note-text` |

缺输入一次性问齐：模板路径 + 数据文件路径 + 是否要加批注。

## 前置自检

1. `python3 -c "import docx"` 通吗？不通 → 提示 `pip install python-docx`，
   或先 `--list-only` 看占位符（list-only 也需 docx 解析；无 docx 时脚本降级打印数据 keys）。
2. 占位符是否全是大写下划线命名（`EMP_NAME`）还是小写（`emp_name`）？JSON key 必须**精确匹配**。

## 工作流

```bash
# 1. 干跑：看会填什么、有哪些占位符没数据
python3 scripts/fill_template.py --template assets/sample-template.docx --data assets/sample-data.json

# 2. 真写（输出到新文件，模板不动）
python3 scripts/fill_template.py --template assets/sample-template.docx --data assets/sample-data.json \
  --apply -o ./out.docx

# 3. 加一条修订批注
python3 scripts/fill_template.py --template assets/sample-template.docx --data assets/sample-data.json \
  --apply -o ./out.docx --note-author 张审 --note-text "第三条金额请复核"

# 4. 只看占位符清单
python3 scripts/fill_template.py --template assets/sample-template.docx --data assets/sample-data.json --list-only
```

批量场景：脚本单次只处理一份模板。要一份模板 + N 份数据 → 在 bash 里
`for f in data/*.json; do python3 scripts/fill_template.py --template tpl.docx \
  --data "$f" --apply -o "out/$(basename "${f%.json}").docx"; done`。

## 交付标准

- 每个占位符要么被填、要么被明确列出在 `[NOTICE]` 里
- 源模板 md5 前后不变（可用 `md5sum` 校验）
- 输出文件能被 Word/WPS 打开且样式未崩（段落样式保留，不重建）

## 失败处置表

| 现象 | 根因 | 处置 |
|---|---|---|
| `[DEGRADE] python-docx not installed` | 没装依赖 | `pip install python-docx` 后重跑 |
| 占位符没被替换 | JSON key 大小写/拼写与 `{{}}` 内不一致 | 对齐 key 名；用 `--list-only` 核对 |
| 表格内没填到 | 占位符在表格里 | 脚本已覆盖 `doc.tables`，确认占位符确在单元格文字内 |
| 输出文件 Word 打不开 | 源模板本身损坏/非真 docx | 用另一个合法 .docx 当模板 |
| 想加真·Word 批注（comment 对象） | 本技能降级为脚注式批注段 | 需手改 docx parts（OXML），超出本技能范围 |

## 参考

- 占位符命名与降级策略：[references/fill-rules.md](references/fill-rules.md)

## 链路位置

- 上游：`docx-writer`（生成初稿模板）
- 下游：`pdf-pipeline`（docx → pdf 终稿）
