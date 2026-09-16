---
name: journal-adapt
description: "Adapt a draft to a target venue's writing conventions: IEEE / ACM / NeurIPS / ACL / Nature, including banned-phrase screening (e.g. Nature dislikes 'In this paper we' / 'Novel') and section-shape checks. Use when the user asks 投 IEEE / 改成 Nature 风格 / 期刊格式适配 / 换会议模板 / 适配 ACL 格式. 当用户要求 按 venue 改稿 / 查禁词 时使用。Do NOT use for LaTeX template mechanics (use latex-formatter)."
license: Apache-2.0
compatibility: Stdlib only; requires python3; static text checks against per-venue rule tables.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-15"
---

# Journal Adapt

Retarget an existing draft to a venue's voice and section structure.

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 草稿文件 | 是 | `--input draft.tex` 读草稿（.tex / 纯文本均可） |
| 目标 venue | 否 | `--target ieee_conf`/`acm`/`neurips`/`acl`/`nature`，默认 `ieee_conf` |
| 输出路径 | 否 | `--output report.json`，缺省打印到 stdout |

缺失时一次性问齐：「请提供：① 草稿文件路径 `--input` ② 目标 venue（`ieee_conf`/`acm`/`neurips`/`acl`/`nature`）③ 是否落盘 `--output`。其余用默认：target=ieee_conf，输出 JSON 到 stdout。」

## 前置自检
```bash
python3 --version                          # 预期 >= 3.8，否则报错并 STOP
test -f scripts/journal_adapt.py && echo OK   # 预期打印 OK，否则脚本缺失 STOP
test -f draft.tex && echo SRC_OK            # 仅当用 --input 时；缺失则 STOP
```
若 `python3` 不存在 → 提示安装 Python ≥3.8；若脚本缺失 → 提示目录不完整；若 `--input` 文件不存在 → 报错并 STOP。

## 工作流

### 步骤 1：按目标 venue 检测
```bash
python3 scripts/journal_adapt.py --input draft.tex --target ieee_conf
python3 scripts/journal_adapt.py --input draft.tex --target nature
python3 scripts/journal_adapt.py --input draft.tex --target neurips --output adapt_report.json
```
预期：输出 JSON 含 `target`、`score`、`status`、`issues[]`、`words`、`est_pages`。
若失败：`invalid choice` → `--target` 取值不在 5 个合法 venue 内，核对取值。

### 步骤 2：判读 verdict 并改稿

- `status == "pass"`（`issues` 为空）→ 通过，无需调整。
- `status == "adjust_needed"` → 按 `issues[]` 逐条处理：`page_limit`（页数超）、`banned`（禁词命中，如 Nature 的 "Novel"）、`missing_section`（缺章节）。
预期：每条 issue 给出 `type` 与可定位信息（如具体禁词、缺失章节名）。
若失败：改稿后仍 `adjust_needed` → 优先补 `missing_section`，再清 `banned` 禁词。

### 步骤 3：存档（可选）

预期：`--output` 指向的 JSON 文件存在且合法。
若失败：路径不可写 → 换可写目录重试。

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| `--input` | 路径 | 草稿文件（必填） |
| `--target` | ieee_conf / acm / neurips / acl / nature | 目标 venue，默认 ieee_conf |
| `--output` | 路径 | 结果 JSON 输出路径 |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| `invalid choice: '<x>'` | `--target` 非法 | 改用 5 个合法 venue 之一 |
| `issues` 全为 banned | 命中 venue 禁词 | 按 issue.phrase 逐条替换/删除 |
| 输出非 JSON | 写入中断 | 检查 `--output` 可写后重试 |

## 交付标准

成功定义：`status == "pass"`，或已据 `adjust_needed` 的 `issues[]` 完成改稿。
产物命名：`adapt_report.json`（若指定 `--output`）。
保存位置：调用方当前目录或 `--output` 指定路径。
验证方法：`python3 -c "import json;d=json.load(open('<output>'));assert d['status'] in ('pass','adjust_needed')"` 通过。

## 参考

无外部 references 文件；venue 规则表内置在 `scripts/journal_adapt.py` 的 `JOURNAL_SPECS`（含 class / columns / page_limit / section_order / ban）。

## 链路位置

上游接 self-reviewer 的 ready 判定；语气打磨可续接 anti-defensive 与 ai-humanizer，最终 tex-cleaner 收口提交包。
