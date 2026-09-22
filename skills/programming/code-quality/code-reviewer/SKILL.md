---
name: code-reviewer
description: >-
  Automated static-analysis engine for code changes and files in TypeScript,
  JavaScript, Python, Go, Swift, Kotlin, C#, .NET, Java, C, C++, Rust, Ruby,
  PHP, and Dart/Flutter. Detects complexity, risk, hardcoded secrets, SQL
  injection, and SOLID violations; generates review reports. Use when the user
  asks to 审查代码 / code review / 帮我看这段代码 / 检查这段代码的风险 / 静态分析
  / 生成审查报告. Do NOT use for fixing the issues it reports (static analysis
  only) — that is code-generator's job.
license: Apache-2.0
compatibility: Pure prompt-based; may read project structure via Bash. The three bundled scripts require Python 3.10+.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: code-quality
  pattern: code-reviewer
  tier: powerful
  verified-date: "2026-09-09"
---

# Code Reviewer

确定性的多语言静态分析：跑内置脚本标记风险，再加载语言/规则参考生成审查报告。本文件是调度表——保持精简；重型规则在 `rules/` 和 `languages/`。

---

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 目标路径 | 是 | 仓库根、目录或单个文件（绝对或相对路径）。 |
| 范围 | 否 | `diff`（默认：当前分支 vs `main`）或 `files`（整树扫描）。 |
| 语言 | 否 | 按下方扩展名表自动识别；可用 `--language` 覆盖。 |
| 输出格式 | 否 | `markdown`（默认）或 `json`。 |
| 预计算结果 | 否 | `pr_results.json` / `quality_results.json` 路径，跳过重复分析。 |

必需输入缺失时，按此模板只问一次：

> 请提供：① 目标路径（仓库/目录/文件）；② 范围（diff 还是整树扫描）。
> 其余我采用默认值：scope=diff（当前分支 vs main）、format=markdown、语言自动识别。

## 前置自检

任何分析前先跑。任一失败 → 打印修复方法并 STOP。

```bash
# 1. 脚本齐全？
test -f scripts/pr_analyzer.py && test -f scripts/code_quality_checker.py \
  && test -f scripts/review_report_generator.py && echo "scripts-ok" \
  || { echo "ERROR: scripts/ missing — bundle is incomplete"; exit 1; }

# 2. Python 可用？
command -v python3 >/dev/null 2>&1 || { echo "ERROR: python3 not found"; exit 1; }

# 3. 通用规则文件在位？
test -f rules/universal.md || { echo "ERROR: rules/universal.md missing"; exit 1; }

# 4. 目标存在？
test -e "$TARGET" || { echo "ERROR: target $TARGET not found"; exit 1; }
```

## 技能目录结构

```text
code-reviewer/
  SKILL.md                        ← 你在这里（工具 + 调度表）
  rules/
    universal.md                  ← 安全、异步、资源、异常、性能——全语言通用
  languages/
    python.md  typescript.md  go.md  swift.md  kotlin.md  csharp.md
    java.md  c.md  cpp.md  rust.md  ruby.md  php.md  dart.md
  scripts/
    pr_analyzer.py  code_quality_checker.py  review_report_generator.py
  assets/  expected_outputs/       ← 回归夹具（C#、Java、C）
```

### 加载顺序（始终恰好多读 2 个文件）

1. `SKILL.md` — 工具与阈值（本文件）。
2. `rules/universal.md` — 每种语言都要读。
3. 一份 `languages/<ext>.md` — 按下表选。

| 扩展名 | 加载 |
|---|---|
| `.py` | `languages/python.md` |
| `.ts`, `.tsx`, `.js`, `.jsx`, `.mjs` | `languages/typescript.md` |
| `.go` | `languages/go.md` |
| `.swift` | `languages/swift.md` |
| `.kt`, `.kts` | `languages/kotlin.md` |
| `.cs`, `.csx`, `.razor`, `.cshtml` | `languages/csharp.md` |
| `.java` | `languages/java.md` |
| `.c`, `.h` | `languages/c.md` |
| `.cpp`, `.cc`, `.cxx`, `.hpp`, `.hh`, `.hxx` | `languages/cpp.md` |
| `.rs` | `languages/rust.md` |
| `.rb`, `.rake`, `.gemspec`, `.ru` | `languages/ruby.md` |
| `.php`, `.phtml` | `languages/php.md` |
| `.dart` | `languages/dart.md` |

## 工作流

### 步骤 1：分析变更 / 目录树

```bash
# diff 模式——当前分支对比 main
python scripts/pr_analyzer.py ../../../..   # 仓库根（git 仓库）；也可指向任意 git 仓库路径
# 指定分支
python scripts/pr_analyzer.py ../../../.. --base main --head feature-branch   # 对仓库根比较分支
# 输出 JSON 给下游工具
python scripts/pr_analyzer.py ../../../.. --json
```

预期：脚本输出复杂度评分（1–10）、风险级别（critical/high/medium/low）、文件优先级排序与提交信息校验；`--json` 把同样内容打到 stdout。若失败：非零退出或 traceback → 确认路径存在且 Python ≥3.10；改用 `--json` 重跑以隔离解析错误。

### 步骤 2：跑质量检查器

```bash
# 整目录，自动识别语言
python scripts/code_quality_checker.py ../../../..   # 仓库根；也可指向任意代码目录
# 指定语言（取值：python, typescript, javascript, go, swift,
#   kotlin, csharp, java, c, cpp, rust, ruby, php, dart）
python scripts/code_quality_checker.py ../../../.. --language python
# JSON 输出
python scripts/code_quality_checker.py ../../../..   # 仓库根；也可指向任意代码目录 --json
```

检查器使用的通用阈值：

| 问题 | 阈值 |
|------|------|
| 长函数 | >50 行 |
| 大文件 | >500 行 |
| 上帝类 | >20 个方法 |
| 参数过多 | >5 个 |
| 嵌套过深 | >4 层 |
| 复杂度过高 | >10 个分支 |

预期：逐文件输出发现项，按上述阈值计分。若失败：语言无法识别时脚本回退到 Python 模式并记一条 warning——用显式 `--language` 重跑。

### 步骤 3：生成审查报告

```bash
# 当前仓库的 Markdown 报告
python scripts/review_report_generator.py /path/to/repo
# 显式格式 + 输出文件
python scripts/review_report_generator.py . --format markdown --output review.md
# 复用预计算结果
python scripts/review_report_generator.py . \
  --pr-analysis pr_results.json --quality-analysis quality_results.json
```

结论映射（两项分析都完成后套用）：

| 评分 | 结论 |
|------|------|
| 90+ 且无 high 问题 | Approve |
| 75+ 且 ≤2 个 high 问题 | Approve with suggestions |
| 50–74 | Request changes |
| <50 或存在任一 critical 问题 | Block |

预期：报告包含结论、逐文件发现项与建议。若失败：先确认两个上游脚本产出过结果，或显式传 `--pr-analysis` / `--quality-analysis`。

## 参数速查表

| 脚本 | 关键参数 | 取值 |
|------|----------|------|
| `pr_analyzer.py` | `--base` / `--head` | 分支名（base 默认 `main`） |
| `pr_analyzer.py` | `--json` | 向 stdout 输出 JSON |
| `code_quality_checker.py` | `--language` | 14 种受支持语言之一 |
| `review_report_generator.py` | `--format` | `markdown` \| `json` |
| `review_report_generator.py` | `--output` | 文件路径 |

## 失败处置表

| 症状 | 原因 | 处置 |
|------|------|------|
| `ModuleNotFoundError` / `SyntaxError` | Python <3.10 或脚本缺失 | 升级 Python；重新确认脚本在位 |
| 报告为空 / 零发现 | 目标路径错误 | 用确实存在的文件或目录重跑 |
| 语言信号错乱 | 扩展名不在表内 | 显式传 `--language` |
| 分析器把未知语言当 Python | 回退模式 | 把该语言加进 `code_quality_checker.py` 的 `LANGUAGE_EXTENSIONS` |

## 交付标准

成功 = 存在一份审查报告，含上述映射得出的结论，且逐文件发现项与 `rules/universal.md` + 对应 `languages/*.md` 交叉核对过。

- 保存位置：仓库根的 `review.md`（或调用方指定的 `--output`）。
- 完整性核验：报告必须列出 (a) 结论；(b) 每个被标记的文件及规则 id；(c) 是否存在 `critical`/`high` 问题。
- 绝不改用户的代码——本技能只分析。

## 参考

- `rules/universal.md` — 每次审查都读：适用于所有语言的安全、异步、资源、异常、性能规则。
- `languages/<ext>.md` — 读与目标扩展名匹配的那一份，获取语言专属检测与惯用法（见上方加载表）。
- `assets/` + `expected_outputs/` — 回归夹具（C#、Java、C）；用来确认分析器行为未漂移：

```bash
python scripts/code_quality_checker.py assets/sample_java_smells.java --json \
  | diff - expected_outputs/sample_java_smells_quality.json
```

---

## 扩展新语言

1. 参照任一现有语言文件创建 `languages/<name>.md`。必须包含这些小节：PR Analyzer Signals, Code Quality Checks, Security, Async, Resource Management, Exception Handling, Performance, Idioms。
2. 把扩展名行加进上方调度表。
3. （可选，让确定性检查器给它计分）把扩展名加进 `scripts/code_quality_checker.py` 的 `LANGUAGE_EXTENSIONS` 和函数/类/方法正则，新增一个 `check_<name>_specific_smells(...)` 检测器，并在 `assets/` 提交一对 `<name>_smells.<ext>` + `_clean` 夹具，在 `expected_outputs/` 提交对应的 `--json`。
