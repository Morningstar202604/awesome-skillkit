---
name: dependency-auditor
description: >-
  Audit and manage dependencies across multi-language projects. Identifies
  vulnerabilities, license conflicts, transitive dependency risks, and
  safe-upgrade paths. Use when auditing third-party packages before release,
  investigating a CVE, planning a major version bump, or running a license
  compliance review. Examples: 'audit our npm dependencies', 'do we have GPL
  contamination', 'plan the upgrade to React 19', 审计依赖 / 依赖安全与许可证 /
  检查过期包 / 升级风险评估. Do NOT use for upgrading dependencies (audit and
  advisory only).
license: Apache-2.0
compatibility: Pure Python 3.10+; the three scripts are offline pattern-matchers over manifests and lockfiles. No network and no API keys required. Pair their findings with `npm audit` / `pip-audit` / `cargo audit` for live CVE coverage.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: code-quality
  pattern: single-task
  tier: powerful
  verified-date: "2026-09-09"
---

# Dependency Auditor

离线、确定性的依赖审计，覆盖 8+ 包生态。三个脚本只对清单/锁文件做模式匹配——**不会**调用在线漏洞公告 API；把它们的发现与 `npm audit` / `pip-audit` / `cargo audit` 搭配使用，才能覆盖最新 CVE。

---

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 项目路径 | 是 | 仓库根，或含清单/锁文件的目录。 |
| 输出格式 | 否 | `json`（脚本场景默认）或 `text`。 |
| 失败阈值 | 否 | `--fail-on-high` 让扫描器在出现 high 级别时以非零码退出。 |
| 风险阈值（planner） | 否 | `low` \| `medium` \| `high`（默认 `medium`）。 |
| 时间窗（planner） | 否 | 升级计划的天数窗口（默认 `90`）。 |

项目路径缺失时，只问一次：

> 请提供：① 项目路径（含 package.json / requirements.txt / go.mod 等的目录）。
> 其余我采用默认值：format=json、risk-threshold=medium、timeline=90 天。

## 前置自检

```bash
# 1. 脚本齐全？
test -f scripts/dep_scanner.py && test -f scripts/license_checker.py \
  && test -f scripts/upgrade_planner.py && echo "scripts-ok" \
  || { echo "ERROR: scripts/ missing — bundle incomplete"; exit 1; }

# 2. Python 可用？
command -v python3 >/dev/null 2>&1 || { echo "ERROR: python3 not found"; exit 1; }

# 3. 目标目录里有可识别的清单？
ls "$PROJECT"/*.json "$PROJECT"/go.mod "$PROJECT"/Cargo.toml \
  "$PROJECT"/Gemfile "$PROJECT"/pom.xml "$PROJECT"/composer.json 2>/dev/null \
  | grep -q . || { echo "WARN: no known manifest found in $PROJECT"; }
```

## 受支持的生态（可解析）

| 语言 | 解析的清单文件 |
|---|---|
| JavaScript/Node | package.json, package-lock.json, yarn.lock |
| Python | requirements.txt, pyproject.toml, Pipfile.lock, poetry.lock |
| Go | go.mod, go.sum |
| Rust | Cargo.toml, Cargo.lock |
| Ruby | Gemfile, Gemfile.lock |
| Java | pom.xml, gradle.lockfile |
| PHP | composer.json, composer.lock |
| C#/.NET | packages.config, project.assets.json |

## 工作流

### 步骤 1：扫描漏洞

```bash
python3 scripts/dep_scanner.py /path/to/project --format json --fail-on-high -o scan.json
```

预期：`scan.json` 含逐包发现项；设置 `--fail-on-high` 时，存在任一 `high` 级别发现即以非零码退出。若失败：找不到清单时扫描器报 0 发现——用正确的项目路径重跑。

### 步骤 2：核查许可证合规

```bash
python3 scripts/license_checker.py /path/to/project --policy strict --format json -o licenses.json
```

预期：`licenses.json` 列出许可证分类与冲突对（如宽松项目里混入 GPL）。若失败：`--policy strict` 会把未知许可证列为人工复核项——核实前一律按冲突处理。

### 步骤 3：规划升级

```bash
python3 scripts/upgrade_planner.py scan.json --risk-threshold medium --timeline 90 --format json -o plan.json
```

预期：`plan.json` 按风险排序升级项，每项附回滚说明。`--quick-scan` 跳过传递依赖；`--security-only` 把计划限定为安全修复。若失败：planner 依赖步骤 1 的 `scan.json`——确认文件存在。

### 验证闭环

应用升级后重跑步骤 1，断言 **0 条 high 级别发现**，才可关闭本次审计。

## 许可证分类

- **宽松（Permissive）**：MIT, Apache 2.0, BSD (2/3-clause), ISC
- **强 Copyleft**：GPL v2/v3, AGPL v3 — 在宽松项目中标记污染风险
- **弱 Copyleft**：LGPL v2.1/v3, MPL 2.0
- **专有 / 双许可 / 未知** — 未知许可证会浮出供人工复核

检查器沿依赖链分析许可证继承，输出冲突对与整改建议。

## 升级风险矩阵

| 风险 | 更新类型 | 处置 |
|---|---|---|
| Low | Patch、安全修复 | 立即应用 |
| Medium | 带新功能的 Minor | 并入例行更新批次 |
| High | Major 版本、API 变更 | 单独立迁移任务 + 补测试 |
| Critical | 已知破坏性变更 | 计划内迁移，附回滚流程 |

优先级：安全补丁 > 缺陷修复 > 功能更新 > 大规模重写。

## 脚本（如实的能力声明）

- **`scripts/dep_scanner.py`** — 多格式解析器；内置离线漏洞模式集（约 16 条 CVE 模式——烟雾层，替代不了在线公告）；从锁文件解析传递依赖；JSON + text 输出。
- **`scripts/license_checker.py`** — 从包元数据检测许可证；覆盖 20+ 许可证类型的兼容矩阵；`--policy permissive|strict`；冲突检测并附整改建议。
- **`scripts/upgrade_planner.py`** — 基于 semver 预测破坏性变更；输出按风险排序的迁移计划，含测试清单与时间估算。

样例夹具：本目录下的 `test-project/` 与 `test-inventory.json`；期望输出形态在 `expected_outputs/`。

## CI 集成

```bash
# CI 里的安全门禁
python3 scripts/dep_scanner.py . --format json --fail-on-high
python3 scripts/license_checker.py . --policy strict --format json
```

## 失败处置表

| 症状 | 原因 | 处置 |
|------|------|------|
| 明明有依赖却报 0 发现 | 项目路径错误 | 改用清单所在目录重跑 |
| `high` 发现卡住 CI | `--fail-on-high` 的预期行为 | 分诊 scan.json；合并前 patch/pin |
| 未知许可证冲突 | SPDX id 无法识别 | 人工核实后，白名单并附书面理由 |
| Planner 报输入缺失 | `scan.json` 不存在 | 先跑步骤 1 |

## 交付标准

成功 = 三份产物齐备且相互对账：

- `scan.json` — 发现项决定现在 pin/patch 哪些包。
- `licenses.json` — 冲突作为法律风险清单交给用户。
- `plan.json` — 按风险排序的升级计划，附回滚说明。

核验：升级后重跑步骤 1，确认 0 条 high 级别发现。产物存项目的 `audit/` 或 CI artifact 目录。本技能只审计——绝不改写用户的清单文件。

## 参考

- `references/vulnerability_assessment_guide.md` — 解读扫描器发现、判断哪些 CVE 模式可信时读。
- `references/license_compatibility_matrix.md` — 处理 `licenses.json` 冲突与污染标记时读。
- `references/dependency_management_best_practices.md` — 了解节奏与误报处置（白名单、联系维护者）时读。

在线漏洞公告命令（不随包附带——在目标仓库里跑，覆盖最新 CVE）：

| 生态 | 审计命令 |
|------|----------|
| Node.js | `npm audit` |
| Python | `pip-audit` |
| Go | `govulncheck` |
| Rust | `cargo audit` |
| Java | `dependency-check` |
| Ruby | `bundle audit` |
| PHP | `composer audit` |
| .NET | `dotnet list package --vulnerable` |
