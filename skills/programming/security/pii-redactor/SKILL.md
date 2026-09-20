---
name: pii-redactor
description: >
  Detect and redact personally identifiable information (PII) in logs, chat
  transcripts, files, and structured data before sharing or logging. Use when
  the user asks to 脱敏 / 去敏 / PII 检测 / 打码 / 隐私清洗 / 合规日志 / GDPR 脱敏 /
  anonymize logs / mask PII / redact personal data / scrub PII / 身份证 / 手机号 /
  邮箱脱敏. Do NOT use for encryption at rest, key management, or secret
  rotation (use secrets-vault-manager / env-secrets-manager); this skill
  redacts already-visible text and structured fields.
license: Apache-2.0
compatibility: Pure Python 3 stdlib (no third-party deps). Read-only scan by default; redaction writes a NEW output file, never mutates the source. Credentials not required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: security
  pattern: script
  tier: powerful
  verified-date: "2026-09-20"
---

# PII Redactor

面向日志、聊天记录、工单、结构化数据（CSV/JSON）的 PII 检测与脱敏。
覆盖 8 类 PII：身份证 / 手机号 / 邮箱 / 银行卡 / 姓名 / 住址 / 车牌 / 统一社会信用代码。
核心原则：**默认 dry-run 只读扫描，脱敏产出新文件，源文件永不改写。**

**区别于 secrets-vault-manager**：那个管密钥基础设施。本技能管"已经可见的文本"里的个人数据脱敏，
不碰密钥、不做加密、不联网。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 目标文件 / 目录 | 是 | 待检测的路径；目录则递归扫描文本文件 |
| PII 类别 | 否 | 默认全 8 类；可指定子集（如只脱 `id_card` + `phone`） |
| 脱敏策略 | 否 | `mask`（保留前后 1-4 位）/ `hash`（SHA-256 前 8 位）/ `replace`（替换为占位符），默认 `mask` |
| 输出文件 | 否 | 脱敏结果写入路径；缺省为 `<原文件>.redacted` |
| 干跑 | 否 | `--dry-run`（默认开）：只报告命中，不写文件 |

（缺失询问模板：「请提供：①待检测的文件或目录路径；②需要脱敏的 PII 类别（默认全部 8 类）；③脱敏策略（mask / hash / replace，默认 mask）。其余采用默认值：dry-run 开、输出 `<原文件>.redacted`。」）

## 前置自检

```bash
python3 -c "import sys; sys.exit(0 if sys.version_info>=(3,8) else 1)" \
  && echo "python>=3.8 OK" || echo "需要 Python 3.8+"
```
预期：打印 `python>=3.8 OK`。若失败 → 提示升级 Python 或改用兼容环境，终止。
无需网络、无需环境变量凭据（红线：本技能不读取任何密钥）。

## 工作流

### 步骤 1：确定输入形态
判定是单文件还是目录。
预期：拿到文件列表（目录时递归 `*.log *.txt *.json *.csv *.md`，跳过二进制与隐藏文件）。
若失败：路径不存在 → 报 `PATH NOT FOUND: <path>`，终止。

### 步骤 2：dry-run 扫描（默认）
运行 `scripts/pii_scan.py --dry-run <path> [--categories phone,id_card]`。
预期：stdout 每行一条命中 `L<行号>\t<类别>\t<原值脱敏预览>\t<文件>`；末行 `SUMMARY: N hits across M files`。
若失败：脚本报 `SYNTAX` 或依赖缺失 → 见失败处置表。

### 步骤 3：复核命中
人工抽查 3-5 条命中，确认无大量误报（如 `1001234` 被误判为手机号）。
预期：误报率 <10%；若某类误报高 → 调 `--no-heuristics` 收紧规则或排除该类别。
若失败：误报严重 → 改用 `--categories` 只保留高置信类别，重跑步骤 2。

### 步骤 4：落盘脱敏（非 dry-run）
确认后运行 `scripts/pii_scan.py <path> --strategy mask --out <输出文件>`（去掉 `--dry-run`）。
预期：stdout `REDACTED: <输出文件> (N hits masked)`，源文件字节不变（用 `diff` 或 `git status` 复核）。
若失败：输出目录不可写 → 报 `PERM` 并提示改 `--out` 到可写路径。

## 检测规则速查

| 类别 | 正则特征 | 默认 mask 形态 |
|------|---------|---------------|
| `id_card` | 18 位 `\d{17}[0-9Xx]`，校验位通过 | `1101***********123` |
| `phone` | `1[3-9]\d{9}`（含 `+86`） | `138****5678` |
| `email` | 标准邮箱 | `j***@example.com` |
| `bank_card` | 13-19 位 Luhn 校验通过 | `6222********0123` |
| `plate` | 车牌 `[京津沪...][A-Z]\d{5,6}[挂学警港]` | `京A*****1` |
| `credit_code` | 统一社会信用代码 18 位 | `91110000***` |
| `address` | 省/市/区/路号组合（启发式） | `[ADDR MASKED]` |
| `name` | 仅启发式（上下文含"姓名/联系人"键） | `[NAME MASKED]` |

> `name` 与 `address` 为启发式类，误报率最高，默认不单独启用，需显式 `--categories name,address`。

## 失败处置表

| 现象 / 错误码 | 原因 | 处置 |
|---|---|---|
| `PATH NOT FOUND` | 输入路径不存在或拼错 | 核对路径，用 `ls` 确认；目录则去掉文件名 |
| `PERM` | 输出路径不可写 | 改 `--out` 到用户可写目录 |
| 命中率 0 但肉眼有 PII | 类别未启用 / 文本被转义 | 显式 `--categories` 加全；检查是否 URL 编码或 JSON 转义（`\u00XX`）需先解码 |
| 大量误报 | 数字串巧合命中 | 加 `--no-heuristics` 只保留正则强校验类（id_card/phone/bank_card/credit_code/plate） |
| `SYNTAX` | Python 版本过低 | 步骤 1 前置自检重跑，升级至 3.8+ |

## 交付标准

- dry-run：stdout 命中清单 + `SUMMARY` 行，不落盘。
- 非 dry-run：产出 `<输出文件>`（默认 `<原文件>.redacted`），stdout `REDACTED: <file> (N hits)`。
- 验证方法：对输出文件重跑 dry-run，命中数应为 0（强校验类）；源文件 `git diff` 无变化。

## 参考

- `references/pii-rules.md` —— 8 类 PII 的正则全集、校验位算法（Luhn / 身份证 mod11）、误报案例对照、JSON/转义文本预处理。
- `scripts/pii_scan.py` —— 执行入口：`--dry-run` 报告、`--out` 脱敏落盘、`--categories` 选择、`--no-heuristics` 收紧。运行它而非手抄算法。
