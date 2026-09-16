---
name: skill-tester
description: "Validate, test, and score the quality of skills within the claude-skills ecosystem. Comprehensive meta-skill: structure validation, Python script testing (syntax + imports + runtime + output format), multi-dimensional quality scoring with letter grades and tier classification (BASIC/STANDARD/POWERFUL). Use when authoring a new skill, auditing existing skills for tier promotion, setting up pre-commit hooks for skill quality, or integrating skill QA into CI. 当用户要求 测试技能 / 校验 skill 是否合规 / 给技能打分 时使用。 Do NOT use for fixing the skills it audits (this skill only audits and scores)."
license: Apache-2.0
compatibility: Pure prompt-based; may read project structure via Bash.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: ai-engineering
  pattern: single-task
  tier: expert
  verified-date: "2026-09-09"
---

# Skill Tester

Validate, test, and score the quality of a skill directory with four tools (structure validation, script testing, quality scoring, security scoring), all runnable from the repo root.

> **Scope note:** this skill's tier line-count minimums measure *legacy* skills. For authoring *new* skills, `engineering/write-a-skill` (SKILL.md under ~100 lines, Matt Pocock doctrine) is the binding standard — do not pad a new skill to satisfy a tier minimum here.

## 输入清单

| 输入 | 必需 | 说明 |
|---|---|---|
| 被审计技能路径 | 是 | 仓库内技能目录，如 `skills/programming/api/api-design-reviewer` |
| 目标最低分 | 否 | `quality_scorer.py --minimum-score`，CI 常用 75 |
| 目标 tier | 否 | `skill_validator.py --tier BASIC\|STANDARD\|POWERFUL`，缺省从 SKILL.md 行数推断 |
| 是否含安全评分 | 否 | 加 `--include-security`（或单独跑 `security_scorer.py`） |

输入缺失时一次性问齐："请提供：① 要审计的技能目录路径；② 目标最低分（不填默认 75）；③ 是否需要安全评分。"

## 前置自检

逐条执行，任一失败 → 按修复处置后 STOP：

```bash
# 1. Python 3 可用
python3 --version
# 预期：Python 3.8+。失败→安装 Python 3 后重试。

# 2. 四个工具脚本存在
ls skills/programming/ai-engineering/skill-tester/scripts/{skill_validator,script_tester,quality_scorer,security_scorer}.py
# 预期：四个 .py 文件名。失败→确认在仓库根目录执行；仍缺→STOP 并回报仓库不完整。

# 3. 目标技能目录存在且含 SKILL.md
cat <技能路径>/SKILL.md > /dev/null && echo OK
# 预期：OK。失败→向用户确认正确路径后 STOP。
```

## 工作流

全部命令在**仓库根目录**执行。

### 步骤 1：结构校验

```bash
python3 skills/programming/ai-engineering/skill-tester/scripts/skill_validator.py <技能路径> --json
```

- **动作**：校验 frontmatter、必需章节、tier 行数下限、目录结构（README/scripts/references）、脚本 stdlib-only。
- **预期**：退出码 0；JSON 中 `compliance_level` 非 `FAIL`。
- **若失败**：退出码非 0 → 读 JSON `checks{}` 里 `passed:false` 的条目，逐项报告给用户（本技能只审计不修复），STOP。

### 步骤 2：脚本测试

```bash
python3 skills/programming/ai-engineering/skill-tester/scripts/script_tester.py <技能路径> --json
```

- **动作**：对技能内每个 Python 脚本做 AST 语法检查、import 分析（标记外部依赖）、受控运行（默认 30s 超时，`--timeout` 可调）、`--help` 验证、按 `expected_outputs/` 比对样例输出。
- **预期**：所有脚本 PASS，无 timeout/import 失败。
- **若失败**：timeout → 用 `--timeout 60` 复跑一次；import 失败 → 脚本引入了非 stdlib 依赖，属仓库政策违规，报告为 FAIL。

### 步骤 3：质量评分

```bash
python3 skills/programming/ai-engineering/skill-tester/scripts/quality_scorer.py <技能路径> --json --detailed --minimum-score 75
```

- **动作**：按 Documentation / Code Quality / Completeness / Usability 四维（各 25%）打分，输出 0-100 分、A-F 等级、tier 建议、`improvement_roadmap`。
- **预期**：退出码 0（分数 ≥ 75）。
- **若失败**：退出码非 0 → 按 `improvement_roadmap` 自顶向下列出改进项（只报告，不代改）。

### 步骤 4：安全评分（可选）

```bash
python3 skills/programming/ai-engineering/skill-tester/scripts/security_scorer.py <技能路径> --json
```

- **动作**：对脚本做安全态势评分（0-100）。
- **预期**：输出 JSON `overall_score`。
- **若失败**：`--verbose` 查看逐条 finding，原样报告。

### 步骤 5：汇总裁决

- **动作**：汇总三/四项结果向用户报告。仓库级批量审计用 `scripts/audit_skills.py`（在本技能 scripts/ 内，父目录 + `--batch` 模式的 `quality_scorer.py` 亦可）。
- **预期**：三项全绿才可称 "passes"——任一步骤失败绝不报部分通过。

## 参数速查表

| 参数 | 取值 | 说明 |
|---|---|---|
| `--tier` | BASIC / STANDARD / POWERFUL | 校验目标 tier（默认按 SKILL.md 行数推断） |
| `--timeout` | 秒数（默认 30） | script_tester 每脚本运行超时 |
| `--minimum-score` | 0-100（默认无门槛） | quality_scorer 低于该值退出码非 0，用作 CI 门禁 |
| `--include-security` | 布尔 | quality_scorer 附加安全维度 |
| `--batch` | 布尔 | quality_scorer 批量模式，skill_path 传父目录 |
| `--json` | 布尔 | 所有工具均支持，机器可读输出 |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|---|---|---|
| script_tester timeout | 脚本运行超 30s | `--timeout 60` 复跑；仍超时报告为失败 |
| import failures | 检出外部依赖 | 仓库政策为 stdlib-only，报 FAIL 不修复 |
| tier 误判 | 行数/LOC 与 tier 表不符 | 对照 tier 矩阵（见参考）；新技能适用 write-a-skill 豁免 |
| validator 报 README 缺失 | 技能目录无 README.md | 报告扣分项，由技能作者补齐 |
| `FileNotFoundError` | 不在仓库根目录执行 | `cd` 到仓库根目录，路径改用仓库相对路径 |

## 交付标准

- 成功定义：步骤 1-3 全部退出码 0（含安全评分时四项全 0）。
- 产物：对话内报告即可；如需留档，保存为 `skill-audit-<技能名>-<YYYYMMDD>.json`（各工具 `--json` 输出拼接），放仓库外或用户指定位置。
- 完整性验证：报告含每个工具的 `overall_score` 与 FAIL 明细；无任何 "partial pass" 表述。

## 参考

- `references/skill-structure-specification.md` — 校验器实现的结构规范；解读步骤 1 的 FAIL 项时读。
- `references/tier-requirements-matrix.md` — tier 与行数/LOC 对照；步骤 1 tier 争议时读。
- `references/quality-scoring-rubric.md` — 四维评分细则；向用户解释扣分原因时读。

## CI Integration

```yaml
# GitHub Actions: gate changed skills
- name: "validate-changed-skills"
  run: |
    for skill in $changed_skills; do
      python3 skills/programming/ai-engineering/skill-tester/scripts/skill_validator.py "$skill" --json
      python3 skills/programming/ai-engineering/skill-tester/scripts/script_tester.py "$skill"
      python3 skills/programming/ai-engineering/skill-tester/scripts/quality_scorer.py "$skill" --minimum-score 75
    done
```

Pre-commit hook: run the validator on the staged skill directory and block the commit on non-zero exit.
