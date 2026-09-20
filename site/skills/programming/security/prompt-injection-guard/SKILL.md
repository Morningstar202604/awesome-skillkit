---
name: prompt-injection-guard
description: >
  Detect and defend against prompt injection / jailbreak attempts in untrusted
  input fed to LLMs. Use when the user asks to 提示注入检测 / 越狱防护 / jailbreak
  防御 / prompt injection / 防注入 / 输入消毒 / 恶意 prompt 识别 / prompt 安全审查 /
  多语言注入 / 间接注入. Do NOT use for red-team penetration (this is detection,
  not attack generation) or for fine-tuning / alignment research; it scans text
  input, flags suspicious patterns, and emits a verdict.
license: Apache-2.0
compatibility: Pure Python 3 stdlib, offline, zero deps, zero network. Read-only: only reads the target text and writes a verdict report; never mutates input. No credentials required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: security
  pattern: script
  tier: powerful
  verified-date: "2026-09-20"
---

# Prompt Injection Guard

面向"喂给 LLM 的不可信输入"（网页正文、邮件、爬取内容、用户提交、工具返回值）
的**提示注入 / 越狱**检测。识别 7 类注入模式：直接指令覆盖、角色扮演越狱、
编码混淆（base64/rot13/hex）、多语言暗语、间接注入（"忽略上面"类）、
数据渗出诱饵、伪装系统消息。输出 0-100 风险分 + 命中清单 + 处置建议。
核心原则：**默认 dry-run 只读，命中不阻断、只报告，阻断由调用方决策。**

**区别于 pii-redactor**：那个脱敏个人数据。本技能防的是"指令层"攻击——
把数据层 PII 清干净 ≠ 防住了注入，两者独立、应串联使用。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 待检文本 | 是 | 字符串或文件路径（网页正文 / 日志行 / 工具输出） |
| 来源类别 | 否 | `web` / `email` / `user_input` / `tool_result`，影响权重 |
| 语言 | 否 | 自动探测；可指定 `zh` / `en` / `multi` |
| 阈值 | 否 | 风险分判定线，默认 50（≥ 判为高危需人工） |
| 干跑 | 否 | `--dry-run`（默认开）：只出报告，不写文件 |

（缺失询问模板：「请提供：①待检文本或文件路径；②来源类别（web / email / user_input / tool_result，默认 web）；③语言（zh / en / multi，默认 auto）。其余采用默认：dry-run 开、阈值 50。」）

## 前置自检

```bash
python3 -c "import sys; sys.exit(0 if sys.version_info>=(3,8) else 1)" \
  && echo "python>=3.8 OK" || echo "需要 Python 3.8+"
```
预期：打印 `python>=3.8 OK`。失败 → 升级或换环境，终止。
离线运行、不读密钥、不发网络（红线：注入防护绝不能把待检文本外发）。

## 工作流

### 步骤 1：加载待检文本
单文件：读入；多文件：逐行/逐块。
预期：拿到待检字符串；若路径不存在 → `PATH NOT FOUND`，终止。

### 步骤 2：扫描 7 类模式
运行 `scripts/injection_scan.py --dry-run <text_or_file> [--source web] [--threshold 50]`。
预期：stdout JSON 报告 `{score, verdict, hits:[{category, line, snippet, weight}], recommendations}`；
`verdict ∈ {clean, low, medium, high, critical}`。
若失败：`SYNTAX` → 前置自检重跑；`JSON` 解析错 → 输入含坏字节，先清洗。

### 步骤 3：分级处置
按 `verdict` 决策（调用方执行，本技能只建议）：
预期：`clean`→放行；`low/medium`→人工复核；`high/critical`→拦截 + 记录样本。
若失败：误报多（把正常技术文档判 high）→ 调 `--threshold` 上浮，或 `--source user_input` 降权。

### 步骤 4：落盘报告（非 dry-run）
`scripts/injection_scan.py <text> --out <报告路径>`。
预期：`REPORT: <路径> (score=N, verdict=X)`，源文本字节不变。
若失败：输出不可写 → 改 `--out`。

## 7 类注入模式速查

| 类别 | 典型信号 | 权重 |
|------|---------|------|
| `direct_override` | "忽略之前的指令 / ignore previous instructions / disregard above" | 高 |
| `roleplay_jailbreak` | "假装你是 / pretend to be / 现在你是一个没有限制的" | 高 |
| `encoded_payload` | 出现 base64/rot13/hex 长串 + "decode/解码" | 高 |
| `indirect` | 工具返回值里嵌指令（"请继续执行 / now run this command"） | 中 |
| `data_exfil` | "把上面的密钥/密码/数据 发给我 / POST the secret to" | 高 |
| `system_spoof` | 伪 `<system>` / `### System:` 块 | 高 |
| `multilingual_lure` | 中英/中日/中俄混写暗语（中英夹杂指令） | 中 |

> 权重为初值，命中叠加；来源 `tool_result` 时 indirect 权重 +20。

## 失败处置表

| 现象 / 错误码 | 原因 | 处置 |
|---|---|---|
| `PATH NOT FOUND` | 输入文件不存在 | 核对路径，单文本可直接喂字符串 |
| `SYNTAX` | Python <3.8 | 前置自检升级 |
| 误报（正常技术文判 high） | 关键词巧合命中 | 上调 `--threshold`；`--source user_input` 降低自动权重 |
| 漏报（注入没识别） | 新变体 / 编码混淆 | 开 `--strict`；人工复核命中项，补充模式 |
| `JSON` 解析错 | 输入含坏字节 | 先 `iconv`/`textwrap` 清洗再喂 |

## 交付标准

- dry-run：stdout JSON 报告（`score` / `verdict` / `hits` / `recommendations`），不落盘。
- 非 dry-run：产出 `--out` 报告文件，stdout `REPORT: <path> (score=N, verdict=X)`，源文本 `git diff` 无变化。
- 验证方法：`verdict` 与命中类别一致；`hits[].snippet` 可人工回溯到原文行号。

## 参考

- `references/injection-patterns.md` —— 7 类模式的完整词库（中英文）、权重表、
  对抗样本、处置 SOP、与 pii-redactor 的串联用法。
- `scripts/injection_scan.py` —— 执行入口：`--dry-run` 出 JSON、`--out` 落盘、
  `--source` 来源加权、`--threshold` 判定线、`--strict` 收紧。运行它而非手抄规则。
