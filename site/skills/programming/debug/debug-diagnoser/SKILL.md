---
name: debug-diagnoser
description: "Parse stack traces and error logs, identify root cause from 10+ known patterns, suggest minimal fix. Outputs structured diagnosis consumable by code-generator. Use when a crash/bug report needs triage before fixing. 当用户要求 排查报错 / 定位崩溃原因 / 看这个 traceback / debug 一下 时使用。 Do NOT use for fixing the code itself (diagnosis and hypothesis ranking only)."
license: Apache-2.0
compatibility: Pure Python standard library (re). No external dependencies.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: programming/debug
  pattern: single-task
  tier: standard
  verified-date: "2026-09-09"
---

# Debug Diagnoser

对报错做分诊：解析堆栈 → 匹配已知错误模式 → 按严重度排序 → 给出最小修复建议，产出结构化诊断 JSON 供 code-generator 消费。只诊断与排序，不改代码。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| `--trace` | 二选一 | 堆栈/报错文本（引号包裹，可含换行转义） |
| `--file` | 二选一 | 报错日志文件路径；与 `--trace` 至少提供一个 |
| `--output` | 可选 | 诊断结果落盘路径；缺省打印 stdout |

缺失输入时一次性问齐：「请提供：①完整 traceback 文本或错误日志文件路径 ②（可选）结果是否落盘。其余我采用默认值：诊断结果打印到终端。」

## 前置自检

运行前探测环境，任一失败→给出修复并 STOP：

```bash
python3 --version   # 预期 3.8+；失败：安装 python3
python3 scripts/diagnoser.py --help >/dev/null 2>&1   # 预期退出码 0；失败：脚本缺失 → 核对技能目录
test -f <用户给的 --file 路径>   # 预期退出码 0；失败：日志文件不存在 → 改用 --trace 直接贴文本
```

## 工作流

### 步骤 1：收集完整报错

预期：拿到含异常类型与 `File "...", line N` 的完整 traceback（截断的堆栈会丢失匹配线索）。
若失败：用户只给了报错截图/描述 → 请其粘贴文本日志；日志文件过大 → 先 `grep -n "Traceback\|Error" error.log` 定位关键段。

### 步骤 2：运行诊断

```bash
python3 scripts/diagnoser.py --trace "Traceback ... TypeError: 'NoneType' object is not callable"
python3 scripts/diagnoser.py --file error.log --output diagnosis.json
```

预期：stdout（或 `--output` 文件）输出 JSON，`status` 为 `diagnosed`，含 `issues[]`（每项有 `error_type`/`likely_cause`/`fix_suggestion`/`severity`）、`locations[]`（`file:line`，最多 5 条）、`top_severity`、`recommendation`、`next_skill`。

### 步骤 3：核验匹配结果

预期：`top_severity` 与报错内容一致（critical > high > medium）；无匹配时 `status` 为 `no_match` 且 `recommendation` 提示人工排查。
若失败：`no_match` 但报错明显 → 查 [references/error-patterns.md](references/error-patterns.md) 全量模式库，人工按模式分诊后在报告中注明为人工诊断。

### 步骤 4：按建议排序并交接

预期：多问题时按 `severity` 从高到低逐项向用户报告；需要自动修复时按 `next_skill` 交接 code-generator。

## 错误模式速查表

| 模式（脚本正则匹配，忽略大小写） | 严重度 | 修复方向 |
|------|--------|----------|
| `TypeError` + None/undefined/not callable/argument | high | 空值检查、初始化 |
| `KeyError` | medium | `.get(key, default)`、核对数据结构 |
| `ModuleNotFoundError` / `ImportError` | medium | 安装依赖或修 import 路径 |
| `IndexError` / list index out of range | high | 边界检查、安全索引 |
| `ValueError` / could not convert / invalid literal | medium | 类型转换、输入校验 |
| `ConnectionError` / ECONNREFUSED | high | 查服务存活、host/port、重试退避 |
| `FileNotFoundError` | medium | 绝对路径、确认文件存在 |
| `PermissionError` | high | 检查用户权限与 umask |
| `MemoryError` | critical | 分块处理 |
| `TimeoutError` | medium | 加大超时、优化慢路径 |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| `status: no_match` | 报错不在 10 个已知模式内 | 读 references/error-patterns.md 人工分诊；向用户说明为人工结论 |
| `locations` 为空 | 堆栈无 `xxx.py:NN` 格式的文件行号 | 属预期；从 traceback 文本人工定位后补充 |
| `--trace` 传参报 shell 错误 | 文本含引号/特殊字符未转义 | 改存为日志文件用 `--file` 传入 |
| `--file` 读不到内容 | 路径错误或无读权限 | 核对路径与权限；或改用 `--trace` |
| 输出未落盘 | 未传 `--output` | 属预期（打印 stdout）；需落盘时加 `--output diagnosis.json` |

## 交付标准

成功定义：输出 JSON `status=diagnosed`，每个 issue 有 cause/fix/severity 三要素，多问题已按 severity 排序。
产物命名：诊断报告 `diagnosis.json`（经 `--output` 落盘时）。
保存位置：与报错日志同目录或工作目录根。
验证完整性：`issues` 与日志中的异常类型一一对应；`locations` 的 file:line 可在源码中打开核对；`no_match` 时已明确告知用户。

## 安全红线

- 本技能只诊断，不修改任何代码文件；修复由 code-generator 或人工完成。
- `--output` 会覆盖同名文件；目标路径已存在时先向用户确认。
- 诊断结论是假设排序而非确证根因；向用户交付时必须标注"建议按序验证"。

## 参考

- [references/error-patterns.md](references/error-patterns.md) —— 遇到 `no_match` 或需要完整模式库与变体时读
- [references/debug-checklist.md](references/debug-checklist.md) —— 脚本分诊后仍需人工复现排查时读

定位根因并修复后，**接着说："诊断已定位根因，继续调用 code-reviewer 复核修复改动，或 code-generator 直接生成修复补丁"——链条自动展开**。
