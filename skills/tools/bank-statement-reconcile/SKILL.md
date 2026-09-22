---
name: bank-statement-reconcile
description: >
  Reconcile a bank/credit-card statement CSV against a billing/expense CSV:
  match transactions by amount + month + optional counterparty, then hand the
  human three lists (matched / only-in-statement / only-in-billing). Use when
  the user asks to 对账 / 流水核对 / 账单核对 / 信用卡账单 vs 银行流水 /
  reconcile statements / match transactions / 找漏记的账. Do NOT use for
  importing from a bank account (no network/credentials here) or for
  accounting journal entries (this is matching, not bookkeeping).
license: Apache-2.0
compatibility: 纯本地 CSV；不联网、不连银行；默认 dry-run；匹配是启发式（金额+月+对方），需人工复核未匹配项
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: tools
  pattern: script
  tier: standard
  verified-date: "2026-09-20"
---

# Bank Statement Reconcile（流水 vs 账单对账）

把"银行流水 CSV"和"账单/记账 CSV"逐笔对，给你三张清单：**匹配成功、
流水有但账单没有、账单有但流水没有**。解决的是：月底对账时"哪笔漏记了、
哪笔金额对不上"——这是纯死流程，人肉对 500 笔会疯。

> 红线：纯本地 CSV，**不连银行、不发网络、不用凭证**；默认 dry-run 只打印
> 摘要，`--write` 才落 JSON 报告；匹配是启发式（金额 + 同月 + 可选对方名），
> **未匹配项必须人工复核**。

## 输入清单

| 输入 | 必填 | 说明 |
|---|---|---|
| 流水 CSV | 是 | 银行/卡导出的流水 |
| 账单 CSV | 是 | 你的记账 / 账单 |
| 金额列名 | 否 | 默认 `amount`，自动探测"金额/amt" |
| 日期列名 | 否 | 默认 `date`，自动探测"日期" |
| 对方列名 | 否 | 传了才参与匹配（增强精度） |

两个 CSV 列名最好对齐；没对齐用 `--amount-col`/`--date-col` 指定。

## 前置自检

1. 两个 CSV 的**金额单位一致**吗（都是元 / 都有相同小数位）？不一致先统一。
2. **日期格式**能归一化吗？脚本支持 `YYYY-MM-DD` / `YYYY/MM/DD` / `MM/DD/YYYY`，
   其他格式先在 CSV 里转成 `YYYY-MM-DD`。
3. 有"交易对方"列吗？有的话传 `--party-col`，匹配更准；没有就纯按金额+月。

## 工作流

```bash
# 1. 干跑：看匹配率 + 未匹配示例
python3 scripts/reconcile.py --statement assets/sample-statement.csv --billing assets/sample-billing.csv

# 2. 指定列名 + 落 JSON 报告
python3 scripts/reconcile.py --statement assets/sample-statement.csv --billing assets/sample-billing.csv \
  --amount-col 金额 --date-col 日期 --party-col 对方 \
  --write -o ./reconcile.json

# 3. 把未匹配清单导成 CSV 给人工
python3 -c "import json;r=json.load(open('reconcile.json'));" 
```

匹配率 < 90% 属正常（说明有不少漏记/差异），逐条看 `unmatched_*` 清单。

## 交付标准

- 三张清单齐全：`matched` / `unmatched_statement` / `unmatched_billing`
- `match_rate` 给得出来（matched / 较大一方行数）
- 未匹配项带原始行，可直接人工核对

## 失败处置表

| 现象 | 根因 | 处置 |
|---|---|---|
| `cannot locate amount/date columns` | 列名探测不到 | `--amount-col`/`--date-col` 显式指定 |
| 匹配率 0% | 金额单位/日期格式不一致 | 先统一单位与日期格式 |
| 大量"流水未匹配" | 账单漏记 | 正常，逐条补记 |
| 同金额多笔混淆 | 没传对方列 | 加 `--party-col` 增强区分 |
| 想要"自动补账" | 超出范围 | 本技能只匹配，补账是人工/会计动作 |

## 参考

- 匹配策略与列名约定：[references/reconcile-rules.md](references/reconcile-rules.md)

## 链路位置

- 上游：银行 App / 网页导出的流水 CSV（先下载到本地）
- 下游：人工把 `unmatched_*` 补进记账；或喂给 `invoice-organizer` 建台账
