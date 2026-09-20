# 周报段落与 JSON 字段

## 三段结构（所有公司通用）
- **做了什么**：`git log --since=N days` 自动拉出，按 `date author: subject` 逐条
- **卡在哪**：默认 `[待填]`，人工补（阻塞点 / 风险 / 需要协调的事）
- **下周计划**：默认 `[待填]`，人工补

## `--input report.json` 字段
```json
{
  "done": ["可选，覆盖自动拉出的 commit 列表"],
  "blockers": "字符串",
  "next": "字符串"
}
```
- 不传 `done` 就完全用 git 自动结果
- 传了 `done` 就**只**用你给的（不再拉 git）

## 段落名对齐
公司周报模板的段落名不一样？改 `TEMPLATE` 里的 `## 1. 本周完成` 等标题，
或把 `done/blockers/next` 喂进 `--input`。
