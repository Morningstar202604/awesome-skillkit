# 发票归档规则

## 默认类别（文件名正则 → 类别）
| 关键词 | 类别 |
|---|---|
| 餐饮/餐/coffee/咖啡/food | 餐饮 |
| 打车/出租/taxi/滴滴/uber | 交通 |
| 酒店/住宿/hotel | 住宿 |
| 办公/文具/耗材/打印/paper | 办公 |
| 话费/流量/网络/宽带 | 通讯 |
| 报销/发票/invoice/receipt/ticket | 发票 |
| 其他 | 未分类 |

## 月份
- 文件名含 `YYYY-MM` / `YYYYMM` / `YYYY.MM` → 按那个月
- 没有 → 当前月

## 回滚
`--apply` 用 `shutil.move`（不删），想撤销就把目标目录的文件拖回源目录。

## Boundaries
- 不读文件内容、不做 OCR（金额/日期靠文件名或人工补）
- 移动操作**不删**，可手动回滚
- 台账 CSV 含 `file/month/category/source_dir` 四列，注意别含敏感金额
