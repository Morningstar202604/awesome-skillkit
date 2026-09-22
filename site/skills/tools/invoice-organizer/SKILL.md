---
name: invoice-organizer
description: >
  Sort a pile of loose invoice/receipt/expense files into a month/category
  tree and emit a CSV ledger, so reimbursement filing stops being a mess.
  Use when the user asks to 整理发票 / 报销归档 / 发票分类 / 流水台账 /
  organize receipts / sort invoices / 报销材料按月份归档. Do NOT use for
  OCR / reading amounts off images (this works on filenames + an optional
  ledger, not pixels) or for actually submitting a reimbursement (human step).
license: Apache-2.0
compatibility: 纯本地文件系统 + CSV；不联网；默认 dry-run；移动操作可手动回滚
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: tools
  pattern: script
  tier: standard
  verified-date: "2026-09-20"
---

# Invoice Organizer（发票/报销归档与台账）

把一堆零散的发票、收据、报销文件，按 **月份/类别** 归档成目录树，并出一份
**台账 CSV**。解决的是：报销季"发票散落各处、找不全、对不上"。

> 红线：默认 **dry-run** 只打印"会怎么分"；`--apply` 才真移动（源目录清空，
> 目标目录保留）；**不删任何文件**，移动可手动回滚；纯本地、无网络。

## 输入清单

| 输入 | 必填 | 说明 |
|---|---|---|
| 发票源目录 | 是 | 散落的发票文件 |
| 目标根目录 | 否 | 默认 `organized/` |
| 自定义类别映射 | 否 | `--map-json` 传 `[[正则, 类别], ...]` |
| 台账 CSV 路径 | 否 | 默认 `ledger.csv`，仅 `--apply` 时写 |

## 前置自检

1. 文件名里有没有能推断类别/月份的词？（餐饮/打车/酒店/话费…）
   全没有 → 会归到"未分类"，可用 `--map-json` 补规则。
2. 月份从哪来？文件名含 `YYYY-MM` 就按那个；否则用当前月。
3. 这些文件里有没有**敏感金额信息**？有的话 `--apply` 后台账 CSV 注意别传远端。

## 工作流

```bash
# 1. 干跑：看会怎么分
python3 scripts/organize_invoices.py --src assets/sample-invoices

# 2. 真归档 + 出台账
python3 scripts/organize_invoices.py --src assets/sample-invoices --dst ./organized \
  --apply --ledger ./organized/ledger.csv

# 3. 自定义类别（公司自己的口径）
python3 scripts/organize_invoices.py --src assets/sample-invoices \
  --map-json ./rules.json --apply
```

`rules.json` 示例：
```json
[["差旅|出差|高铁|机票", "差旅"], ["云|服务器|域名", "IT"]]
```

## 交付标准

- 归档目录树：`organized/<YYYY-MM>/<类别>/<文件>`
- 台账 CSV 每行 = 文件名 / 月份 / 类别 / 源相对路径
- 源目录在 `--apply` 后被清空，所有文件可数、不丢

## 失败处置表

| 现象 | 根因 | 处置 |
|---|---|---|
| 全进"未分类" | 文件名无类别词 | 传 `--map-json` 补正则 |
| 月份全一样 | 文件名无日期 | 按文件名/内容补 `YYYY-MM`，或接受当前月 |
| 想加回 | 移错了 | `--apply` 是 `shutil.move`，手动从目标拖回源即可 |
| 台账想含金额 | 本技能不读文件内容 | 金额需另配 OCR/人工填 |

## 参考

- 类别规则与回滚说明：[references/invoice-rules.md](references/invoice-rules.md)

## 链路位置

- 上游：手机/邮箱下载的发票原件（先下到本地目录）
- 下游：人工把台账贴进报销系统（本技能**不自动提交**，合规留给人）
