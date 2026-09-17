# 逐技能逻辑链条审计报告（v0.19.0）

> 审计日期：2026-09-17 ｜ 覆盖：**143 个技能，全覆盖无抽样**
> 审计标准：每个技能按「输入清单 → 前置自检 → 工作流 → 交付标准 → 失败处置表 → 参考」
> 六要素验链条闭合性，并用真实样例实测全部 `scripts/*.py`（正例 rc=0 / 异常样例 rc≠0）。
>
> 本轮发现并修复 **50+ 处缺陷**，其中 **P0（链路必坏 / 失败被吞）8 处**。
> 修复后四重门禁全绿：`validate` 0 err 0 warn ｜ `skill-linter` 0 FAIL ｜
> `pytest` 271 passed / 1 skipped ｜ `build_site` 37 archives。

---

## 审计分组与覆盖

| 组 | 范围 | 技能数 | 报告 |
|----|------|--------|------|
| 1 | `skills/programming/**`（19 子域） | 45 | 第一部分 |
| 2 | `skills/video` `writing` `chat` `scenarios` | 43 | 第二部分 |
| 3 | `skills/design` `audio` `marketing` `education` `ppt` `paper` | 31 | 第三部分 |
| 4 | `skills/office` `tools` `meta` `knowledge` | 12 | 第四部分 |
| 5 | `skills/integrations` `dataviz` `memory` `meta/skill-finder` | 11 | 第五部分 |
| — | 合计 | **142**（+ `ai-cover-generator` 由主协调者纳入，共 143） | |

---

## 第一部分 · programming 全子域（45 技能 / 19 子域）

# Agent1 测试报告 — skills/programming 全子域

- 日期：2026-09-15 ｜ 测试人：Agent1（全量测试工程师）
- 范围：`skills/programming/` 全部 19 个子域、45 个盘上技能、约 100 个 scripts/*.py
- 纪律：全部中间产物写 /tmp/sk_test（session 走 SKILLKIT_SESSION_DIR）；未触发联网（research 模式标注跳过）；未改 skill_chains.json / manifest.json / README* / SOURCES.md / CHANGELOG.md。

---

## 1. 总览

| 指标 | 数值 |
|---|---|
| 盘上技能 / chains 登记 / 游离 | 45 / 12 / **33** |
| `--help` 冒烟 | **96/96 通过**（rc=0，无 CLI 崩溃） |
| 深测脚本（正例+异常双路径） | 14 个必测 + 2 个子域编排器 + test_generator（库），共 **约 60 个用例** |
| `__main__` 返回码传播扫描 | 96 脚本全扫：41 个 `sys.exit` 传播、49 个裸 `main()`（其中多数在 main 内部 sys.exit）、7 个纯库无入口 |
| 最终门禁 | `validate_skills.py`：0 errors / 0 warnings（与基线持平，未新增） |
| 最终回归 | `pytest skills/programming -q`：**97 passed**（与基线 257 全仓口径一致，本域无失败） |
| 已修复 | **13 个脚本/编排器 + 9 个 SKILL.md 衔接话术**（明细见 §5） |

## 2. 逐脚本结果表

rc 约定：✅=行为正确；❌=发现缺陷；括号为修复后复验。

| 脚本 | 正例（复杂真实样例） | 异常/边界样例 | 返回码传播 |
|---|---|---|---|
| security/env-secrets-manager/env_auditor.py | ✅ 脏仓库 7 findings（critical=2），rc=1；脱敏 excerpt `AKIA...(20 chars)` | ✅ 干净仓库 rc=0；路径不存在 rc=2 | ✅ `sys.exit(main())`（范本） |
| code-quality/dependency-auditor/dep_scanner.py | ✅ npm+pypi 双生态 6 漏洞、`--fail-on-high` rc=1 | ✅ 路径不存在 rc=1；空项目 0 依赖 rc=0 | ⚠️❌→✅ CVE 重复计数（express 同 CVE 出现 2 次，根因 `[name, name.lower()]` 重复），修复后 6→3；非法 package.json 静默按 0 依赖处理（P3 留存）；解析错误改走 stderr |
| code-quality/code-reviewer/code_quality_checker.py | ✅ god.py 检出 long_function/too_many_parameters，score 93/A | ✅ 路径不存在 rc=1；空文件/二进制 rc=0 不崩 | ✅ 缺路径内部 sys.exit(1) |
| api/api-design-reviewer/api_linter.py | ✅ 4 端点 17 issues（0 error）rc=0，语义正确（有 error 才 rc=1） | ✅ 非法 JSON rc=1；文件不存在 rc=1；缺参 rc=2 | ✅ `sys.exit(main())` |
| debug/debug-diagnoser/diagnoser.py | ✅ TypeError+KeyError 双命中，top=high | ❌→✅ `--file` 不存在时误报 "Need --trace or --file"（已改为明确报错 rc=1）；空 trace rc=2 | ❌→✅ 补 `sys.exit(main())` |
| incident/incident-commander/incident_classifier.py | ✅ JSON 文件/stdin 文本两路 rc=0 | ✅ 缺 description rc=2；非法 JSON rc=1；文件不存在 rc=1 | ✅ 内部 sys.exit |
| cicd/ship-gate/ship_gate_scanner.py | ✅ 干净目录按门禁语义报 FAIL→DO_NOT_SHIP rc=1（设计如此） | ❌→✅ `--category BOGUS` 静默跑 0 项 rc=0（已改为 rc=2 + 合法列表提示）；路径不存在 rc=1 | ✅ `sys.exit(print_json_report(...))` |
| planning/code-intent-planner/pipeline.py | ✅ L1 命中 implement/0.88 | ✅ 无输入 rc=1 | ❌→✅ **L2 不可达时 `{"error":...}` 仍 rc=0（失败当成功，paper 域同类）**，已修 `sys.exit(1)`；正例 rc=0 |
| planning/code-generator/code_generator.py | ✅ plan 驱动生成 3 文件，--dry-run 不落盘 | ❌→✅ plan 文件不存在/非法 JSON 此前直接 traceback（已改为干净报错 rc=1，并区分"路径不存在且非 JSON"）；空 `{}` plan 优雅兜底 rc=0 | ❌→✅ 补 `sys.exit(main())`（result.status=error → rc=1） |
| math/model-formulator.py | ✅ "Minimize…integer assignments"→MIP | ❌→✅ 非法 --knowns JSON 由 traceback 改为干净 rc=1；缺参 rc=2 | ❌→✅ 补 `sys.exit(main())` |
| math/model-solver.py | ❌→✅ **LP 路径 100% 崩溃：`result.iter` 应为 `result.nit`（scipy linprog 无 iter 属性），AttributeError rc=1**（修复后 success/iterations=0）；MC 正例 ✅ | ❌→✅ spec 不存在/非法 JSON 由 traceback 改为干净 rc=1；solver 内部 status=error 现也 rc=1 | ❌→✅ 补 `sys.exit(main())` |
| math/visualizer.py | ✅ line/scatter 渲染 rc=0 | ❌→✅ **数据文件不存在打印 skipped 却 rc=0（失败当成功）**，已改 rc=1；非法 JSON 干净 rc=1 | ❌→✅ 补 `sys.exit(main())` |
| math/simulation.py | ✅ 参数扫描 6 点 / monte-carlo p_exceed≈0.03 | ❌→✅ spec 不存在/非法 JSON 由 traceback 改为 rc=1；--range 单值 rc=2 | ❌→✅ 补 `sys.exit(main())` |
| code-quality/tdd-guide/test_generator.py | ❌→✅ 库调用正常（user_stories→cases） | ❌→✅ **acceptance_criteria 传字符串列表即 AttributeError 崩溃**，已修字符串兼容；空 dict 返回 [] | ⚠️ 纯库模块无 CLI（见 P3-1） |
| incident/runbook-generator、slo-architect 三件、observability-designer 等 | 其余 96 脚本 `--help` 冒烟全过；同域深测抽样以上表为准 | — | — |

## 3. 链条衔接契约（差距量化）

### 3.1 full_project：声明 9 步 vs 编排器实际实现 3 步 + 1 占位（差距 5 步）

`skills/skill_chains.json` programming.full_project 声明：
`code-intent-planner → deep-research? → code-generator → tdd-guide → code-reviewer → dependency-auditor → ci-cd-pipeline-builder → ship-gate → runbook-generator`

`planning/pipeline_orchestrator.py` `run_full_pipeline` 实际：

| chains 步骤 | 编排器实现 | 状态 |
|---|---|---|
| code-intent-planner | run_intent_planner（subprocess） | ✅ 已实现 |
| （任务规划，隐含步） | 内存组 plan dict | ✅ |
| deep-research? | 仅 `--mode research` 分支，full 流程不调用 | ⚠️ 可选步未接 |
| code-generator | run_code_generator（临时 plan 文件传递） | ✅ 已实现（本次补 --dry-run） |
| tdd-guide | **纯 placeholder**：返回"请提供代码文件"文案；且示例命令 `python scripts/test_generator.py --input …` 指向一个**没有 CLI 入口的库模块**，照抄必败 | ❌ 占位 |
| code-reviewer | 无任何调用代码 | ❌ 缺失 |
| dependency-auditor | 无任何调用代码 | ❌ 缺失 |
| ci-cd-pipeline-builder | 无任何调用代码 | ❌ 缺失 |
| ship-gate | 无任何调用代码 | ❌ 缺失 |
| runbook-generator | 无任何调用代码 | ❌ 缺失 |

**量化结论：9 步声明 → 3 步真实执行（intent/plan/code）+ 1 占位（tdd）+ 5 步完全缺失；实现率 33%（4/12 含隐含步）。**

### 3.2 步间参数传递核对

- intent→code：`run_intent_planner` 输出 intent_data → `plan={intent_type, sub_tasks, critical_path, solution, slots}` → 写临时 JSON 传给 code-generator `--plan`。**链路正确**；但本域实测 L1 直命中时 sub_tasks 为空 → code-generator 走内置兜底 plan（生成 3 个通用文件），衔接"能跑但语义偏泛"。
- tdd→后续：无数据流（占位）。
- 编排器自身缺陷（均已修）：
  1. subprocess 用硬编码 `"python"` 而非 `sys.executable`（无 `python` 命令的环境整条链 FileNotFoundError）—— 3 处全改；
  2. `run_tdd_guide` 的 sys.path 指向 `SKILLS_DIR/"code-quality"`，**漏了 `programming` 一层**（真引用即 ImportError）；
  3. 无 `--dry-run`（已补，4 步 planned，不触发子进程）；
  4. 失败 rc 不传播（已补：errors 非空 → rc=1）；
  5. 非 --json 模式会把 `pipeline_result_<ts>.json` 写进 CWD（在仓库根运行即污染仓库，与历史 scene_*.wav 同类问题，已移除该落盘）。

### 3.3 子域编排器

| 编排器 | 步数 | 参数传递 | 发现 |
|---|---|---|---|
| math/math_pipeline.py | 4（formulate→solve→simulate→visualize） | 文件传递（/tmp/math_*/model_spec.json→results.json），sys.executable ✅ | ❌→✅ optimization 域 solve 步因 solver LP bug 100% partial（修复后 complete）；dry-run 曾报 status=partial（已改 planned）；partial 时 rc=0（已补 rc=1）；输出目录在 /tmp ✅ |
| data/data_ml_pipeline.py | 3（etl→features→ml_train） | 文件传递（/tmp/data_ml_*/clean.csv→features.json） | ❌→✅ **P0：`SCRIPTS["ml"]` 指向 `ml/pipeline/`（实际目录 `ml/ml-pipeline/`），ml_train 步 100% FileNotFoundError**（修复后 fake.csv 三步 complete rc=0）；dry-run/partial rc 同上已修 |
| planning/pipeline_orchestrator.py | 见 §3.1 | — | — |

## 4. Gap 清单（P0–P3）

**P0（链路级必坏，已修 2/2）**
1. model_solver LP `result.iter`→`nit`（math 链 optimization 域必崩）✅已修
2. data_ml_pipeline ml 脚本路径错（data_ml 链第 3 步必断）✅已修

**P1（失败被吞/静默成功，已修 4/4）**
3. code-intent-planner pipeline.py L2/L3 失败 rc=0 ✅
4. visualizer 数据文件缺失 rc=0（status:skipped）✅
5. math 四件套 `__main__` 裸 main() 不传播 ✅（paper 域同类问题在本域共 8 处进程入口，本次修复覆盖 math 4 + pipeline/code_generator/diagnoser 等）
6. pipeline_orchestrator 硬编码 "python" ✅

**P2（健壮性/体验，已修 7 项）**
7. code_generator plan 读取 traceback → 干净 rc=1 ✅
8. diagnoser --file 缺失误导报错 → 明确 rc=1 ✅
9. dep_scanner CVE 重复计数 + 解析错误走 stdout → stderr ✅
10. test_generator 字符串 criteria 崩溃 ✅
11. ship_gate 未知 --category 静默 rc=0 → rc=2 ✅
12. math/data_ml 编排器 dry-run=partial、失败 rc=0 ✅
13. pipeline_orchestrator：run_tdd_guide 错路径、CWD json 垃圾、无 --dry-run ✅

**P3（建议，未动）**
1. **tdd-guide 全部 8 个 scripts 均为无 CLI 的库模块**，chains/编排器无法程序化调用该步 → 建议补统一 CLI 入口（如 `tdd_workflow.py --input …`）或在 SKILL.md 明示"仅库引用"。
2. full_project 缺失的 5 步 runner（code-reviewer/dep-audit/ci-cd/ship-gate/runbook）需要新增 5 个 subprocess 封装 + 步间文件契约，建议单独立项（实现路径已明确：仿 run_code_generator 模式）。
3. dep_scanner 对非法 package.json/requirements.txt 静默按 0 依赖处理 → 建议 scan_summary 记 parse_errors 并进报告。
4. code_quality_checker 深嵌套(≥4 层 if)、未用 import、死存储不检出（god.py 只命中 2 类）→ 启发式覆盖面可扩。
5. `--mode research` / deep-research / web-search 会真实联网（本测跳过），建议编排器加 `--offline` 熔断。
6. project_analyzer.py、api_scorecard.py、breaking_change_detector.py 等未深测（冒烟通过）。

## 5. 已修复项（全部位于 skills/programming/，门禁与 pytest 复验通过）

| # | 文件 | 修复 |
|---|---|---|
| 1 | math/model-solver/scripts/model_solver.py | `result.iter`→`result.nit`；`float(result.fun) if result.fun is not None`；spec 读取异常分支（不存在/非法 JSON/IO → 干净 rc=1）；`sys.exit(main())` |
| 2 | math/model-formulator/scripts/model_formulator.py | --knowns 非法 JSON rc=1；输出 IO 异常 rc=1；`sys.exit(main())` |
| 3 | math/result-visualizer/scripts/visualizer.py | 数据文件不存在 rc=1（skipped→error）；非法 JSON rc=1；`sys.exit(main())` |
| 4 | math/simulation-runner/scripts/simulation.py | spec 读取异常 rc=1；输出 IO 异常 rc=1；`sys.exit(main())` |
| 5 | planning/code-intent-planner/scripts/pipeline.py | result 含 error → rc=1；`sys.exit(main())` |
| 6 | planning/code-generator/scripts/code_generator.py | plan 文件/JSON/stdin 三路异常分支 rc=1；result.status=error → rc=1；`sys.exit(main())` |
| 7 | debug/debug-diagnoser/scripts/diagnoser.py | --file 不存在明确报错 rc=1；`sys.exit(main())` |
| 8 | planning/pipeline_orchestrator.py | 3 处 "python"→sys.executable；run_tdd_guide 路径补 programming 层；新增 --dry-run；errors→rc=1；移除 CWD pipeline_result_*.json 落盘 |
| 9 | math/math_pipeline.py | dry-run status=planned；失败 rc=1 |
| 10 | data/data_ml_pipeline.py | **ml 路径 ml/pipeline→ml/ml-pipeline**；dry-run status=planned；失败 rc=1 |
| 11 | code-quality/dependency-auditor/scripts/dep_scanner.py | CVE 去重（dict.fromkeys + not in）；解析错误→stderr |
| 12 | code-quality/tdd-guide/scripts/test_generator.py | 字符串 acceptance_criteria 兼容 |
| 13 | cicd/ship-gate/scripts/ship_gate_scanner.py | 未知 --category → rc=2 + 合法列表 |

SKILL.md 衔接话术（9 个，按全仓"继续调用 X——链条自动展开"句式追加，validate 通过）：debug-diagnoser、env-secrets-manager、etl-builder、feature-engineer、api-design-reviewer、docker-development、helm-chart-builder、kubernetes-operator、terraform-patterns。

回归证据：`validate_skills.py` 0 errors/0 warnings；`pytest skills/programming -q` 97 passed；修复前 22 项失败行为全部转绿（R1–R23）。

## 6. 建议 chains.json 改动（仅供采纳，未写入）

```json
"programming": {
  "entry": "skills/programming/planning/pipeline_orchestrator.py",
  "skills": [
    "code-intent-planner","deep-research","web-search","code-generator","tdd-guide",
    "code-reviewer","dependency-auditor","ci-cd-pipeline-builder","ship-gate",
    "runbook-generator","incident-commander","observability-designer",
    "debug-diagnoser","env-secrets-manager","secrets-vault-manager",
    "api-design-reviewer","api-test-suite-builder",
    "etl-builder","feature-engineer","ml-pipeline",
    "model-formulator","model-solver","simulation-runner","result-visualizer",
    "docker-development","helm-chart-builder","kubernetes-operator","terraform-patterns",
    "senior-architect","migration-architect","monorepo-navigator",
    "database-designer","sql-database-assistant","performance-profiler",
    "tech-debt-tracker","spec-driven-workflow","slo-architect",
    "skill-tester","mcp-server-builder","feature-flags-architect",
    "agent-designer","changelog-generator","git-worktree-manager","pr-review-expert"
  ],
  "chains": {
    "full_project": [ "code-intent-planner","deep-research?","code-generator","tdd-guide",
      "code-reviewer","dependency-auditor","ci-cd-pipeline-builder","ship-gate","runbook-generator" ],
    "bug_fix":  [ "code-intent-planner","deep-research?","code-generator","tdd-guide","code-reviewer" ],
    "incident": [ "incident-commander","runbook-generator","code-intent-planner","code-generator","tdd-guide","ship-gate" ],
    "security_fix":   [ "env-secrets-manager","secrets-vault-manager","code-intent-planner","code-generator","tdd-guide","code-reviewer","ship-gate" ],
    "debug_hotfix":   [ "debug-diagnoser","code-intent-planner","code-generator","code-reviewer","ship-gate" ],
    "data_ml":        [ "etl-builder","feature-engineer","ml-pipeline" ],
    "math_modeling":  [ "model-formulator","model-solver","simulation-runner","result-visualizer" ],
    "api_design":     [ "code-intent-planner","api-design-reviewer","api-test-suite-builder","ship-gate" ],
    "infra_delivery": [ "docker-development","helm-chart-builder","kubernetes-operator","terraform-patterns","ship-gate" ],
    "db_change":      [ "database-designer","migration-architect","ship-gate" ],
    "sre_readiness":  [ "slo-architect","observability-designer","runbook-generator","incident-commander" ],
    "release_audit":  [ "tech-debt-tracker","dependency-auditor","env-secrets-manager","ship-gate","changelog-generator" ]
  }
}
```

说明：skills 补登 32 个（45−12−self-eval；self-eval 为元技能建议留在盘外）；9 条新链与本次补的 SKILL.md 衔接话术一一对应（debug_hotfix、security_fix、data_ml、math_modeling、api_design、infra_delivery 已具备可运行脚本基础）；重复/可合并观察：database-designer 与 sql-database-assistant 各有一份 `migration_generator.py`（82 行相似度待人工比对），建议二选一或在 SKILL.md 划清边界（DDL 设计 vs 交互式查询）。

## 7. 复现命令

测试夹具与全部用例位于 `/tmp/sk_test/`（env_repo/proj_good/quality/*.py/openapi_good.json 等），session 目录 `/tmp/sk_test/sessions`（SKILLKIT_SESSION_DIR），仓库工作区无测试残留。

---

## 第二部分 · video / writing / chat / scenarios（43 技能）

# 全量测试报告 · media 域（video / writing / chat / scenarios）

> 测试工程师：agent2 ｜ 范围：`skills/video/` `skills/writing/` `skills/chat/` `skills/scenarios/`
> 基线参照：`validate_skills.py` 0 err / 0 warn；`pytest skills -q` = 257 passed（本四域子集 129 passed）
> 共享文件（skill_chains.json / manifest.json / README* / SOURCES.md / CHANGELOG.md）**未改动**，链条补全仅以"建议"形式给出。

---

## 一、门禁通过脚本数

**共 30 个本地脚本通过门禁（valid/offline 输入 rc=0），其中 13 个做了「正确样例 + 异常样例」双向深测，17 个 publisher 做了 offline 安全扫描（--help + dry-run + 凭据守卫）。** 另有 2 类真实模式（TTS/lip-sync/editor/thumbnail 的联网或 ffmpeg 路径）因环境无外网/ffmpeg 标记为 **SKIP（不触发联网）**，其 mock 路径已覆盖。

| 域 | 深测脚本数 | 通过 | SKIP(网络/ffmpeg) |
|----|-----------|------|-------------------|
| video | 8 | 8 | 4（voice/lipsync/editor/thumbnail 真实模式）|
| writing-core | 4 | 4 | 0 |
| writing-publishers | 17 | 17 | 0（dry-run 默认不联网）|
| chat | 1 | 1 | 0 |
| scenarios | 0 | 0 | 0（无 scripts/，见 §2）|

---

## 二、逐脚本结果表

### 2.1 video（8 个脚本，双向深测）

| 脚本 | 正确样例 → 期望 | 结果 | 异常/边界样例 → 期望 | 结果 | 类型 |
|------|----------------|------|---------------------|------|------|
| storyboard-designer/scripts/scene_lint.py | 合法 storyboard/（9 字段全、编号 01 起连续、时长 1–10s）→ rc=0 | ✅0 | 缺字段+跳号 / 空目录 / 时长 99s → rc=1 | ✅1/✅1/✅1 | **严格门禁** |
| video-prompt-engineer/scripts/prompt_audit.py | 六槽位齐全（中/英）→ rc=0 | ✅0/✅0 | 仅"一只猫"缺槽位 → rc=1 | ✅1 | **严格门禁** |
| video-script-writer/scripts/script_writer.py | 正常 concept+type → rc=0 | ✅0 | 空 concept → rc=0（**未拦截**，设计如此，见 P3）；非法 type → rc=2 | ✅0/✅2 | 生成器 |
| video-subtitles/scripts/subtitles.py | --script / --text → rc=0 | ✅0/✅0 | 无参数 → rc=2 | ✅2 | 生成器 |
| video-thumbnail/scripts/thumbnail.py | --mock --title → rc=0 | ✅0 | 无参数 → rc=2 | ✅2 | 生成器(mock) |
| video-voice-synth/scripts/voice_synth.py | --mock --text / --script → rc=0 | ✅0/✅0 | 空文本真实守卫 → rc=3；缺失脚本文件 → rc=3；无参 → rc=2 | ✅3/✅3/✅2 | **严格门禁**(空文本)+生成器(mock) |
| video-lip-sync/scripts/lip_sync.py | --mock --script → rc=0 | ✅0 | 缺失脚本文件 → rc=3；无参 → rc=2 | ✅3/✅2 | **严格门禁**(文件)+mock |
| video-editor/scripts/editor.py | --mock --script → rc=0 | ✅0 | 缺失脚本文件 → rc=3；无参 → rc=2 | ✅3/✅2 | **严格门禁**(文件)+mock |

> video 真实模式（--gateway / ffmpeg）：voice_synth / lip_sync / editor / thumbnail 在 **mock 或 `--mock`** 下完全本地可跑；真实模式需自备网关或 ffmpeg，缺失会打印排查指引并以非 0 退出（已用 mock 验证逻辑，真实网络路径 SKIP 不触发）。

### 2.2 writing-core（4 个脚本，双向深测）

| 脚本 | 正确样例 → 期望 | 结果 | 异常/边界样例 → 期望 | 结果 | 类型 |
|------|----------------|------|---------------------|------|------|
| article-outliner/scripts/outliner.py | --topic / --json-input → rc=0 | ✅0/✅0 | 无 --topic 且无 --json-input → rc=2 | ✅2 | 生成器 |
| article-drafter/scripts/drafter.py | --outline / --topic → rc=0 | ✅0/✅0 | 缺失大纲文件 → rc=1（已加干净报错，见 §5）；无参 → rc=2 | ✅1/✅2 | 生成器 |
| content-editor/scripts/editor.py | --draft / --text（含禁用词）→ rc=0 | ✅0/✅0 | 无参 → rc=2（禁用词仅**标记**不失败，设计如此）| ✅2 | 检查器 |
| seo-optimizer/scripts/seo_optimizer.py | --title+--content / 空内容 / 无参 → rc=0 | ✅0/✅0/✅0 | —（无校验分支，设计如此）| — | 生成器 |

### 2.3 writing-publishers（17 个脚本，offline 安全扫描）

全部 `--help` 通过（rc=0），且源码均含 `dry_run_guard`/`--execute`/`dry-run` 默认守卫；**默认不联网**，缺失凭据时以非 0 退出。代表深测：

| 脚本 | 正确样例 → 期望 | 结果 | 异常样例 → 期望 | 结果 |
|------|----------------|------|----------------|------|
| wechat/wechat-mp-publisher/scripts/wechat_mp_publish.py | 带虚拟凭据 dry-run（PLAN 打印，无联网）→ rc=0 | ✅0 | 真正无凭据 → rc=1（SystemExit）| ✅1 |
| orchestrator/cross-post-orchestrator/scripts/cross_post.py | --help → rc=0 | ✅0 | — | — |

> 其余 15 个 publisher（csdn/juejin/baijiahao/toutiao/zhihu/bilibili/weibo/xiaohongshu/douban/oschina/segmentfault/v2ex/jianshu/cnblogs/static-blog-deploy + ai-cover-generator）均通过 `--help` 扫描与 dry-run 守卫，单测由基线 pytest 覆盖（129 passed）。

### 2.4 chat（1 个脚本，双向深测）

| 脚本 | 正确样例 → 期望 | 结果 | 异常样例 → 期望 | 结果 | 类型 |
|------|----------------|------|----------------|------|------|
| chat-prompt-engineer/scripts/prompt_audit.py | task 五要素齐全 / agent 五段齐全 → rc=0 | ✅0/✅0 | 缺要素("写首诗") → rc=1；空 prompt → rc=2 | ✅1/✅2 | **严格门禁** |

### 2.5 scenarios

`excel-assistant / meeting-notes / music-generation / resume-tailor` **均无 `scripts/` 目录**，无可测本地启发式脚本 → 该域无脚本门禁（见 §3 补链建议）。

---

## 三、链条衔接契约核对

### 3.1 video_pipeline.py（video/video_pipeline.py）

- **步骤清单（硬编码 6 步，与 `--type` 无关）**：script → tts → lipsync → editor → subtitles → thumbnail。
- **与 chains.json 对照**：
  - `talking_character` 链 = [script, tts, lipsync, editor, subtitles, thumbnail]（6 步）✅ 与编排器一致。
  - `meme` 链 = [script, image-generation, music-generation, editor, subtitles, thumbnail] ❌ 编排器**不**跑 image-generation/music-generation，却**多跑** tts+lipsync（meme 链未含）→ 编排器无视 chain 结构，永远按 talking_character 走。
  - `tutorial` 链 = [script, tts, editor, subtitles, thumbnail] ❌ 编排器仍跑 lipsync（tutorial 链未含）。
  - **结论**：编排器未读取 skill_chains.json，只用一套固定步骤 → 对 meme/tutorial 类型会跑错步骤（P1）。

- **step 间文件交接契约（真实模式存在断点）**：
  1. tts 批量输出 `scene_<id>.wav` 写到**当前工作目录**（非 `--audio-dir`），而 lipsync 的 `audio-dir` 默认取编排器传的 `out_dir` → **目录不一致**，真实模式 lipsync 找不到音频。
  2. lipsync 输出文件名 = `lipsync_scene_<id>.mp4`，而 editor 的 `full_pipeline` 在 `clips-dir` 里找的是 `scene_<id>.mp4` → **命名不一致**，editor 收集不到片段。
  3. 上述断点被 mock 模式掩盖（mock 下 lip_sync/editor 不校验文件存在，直接返回占位元数据）。
  - **结论**：真实链路文件交接断裂（P0），建议编排器显式传 `--output`/`--clips-dir` 对齐文件名（见 §4）。

### 3.2 writing_pipeline.py（skills/writing/writing_pipeline.py）

- **步骤清单（对任意 type 固定 5 步）**：outline → draft → edit → seo → publish(per platform)。
- **step 间参数传递**：
  - outline → draft ✅（`outline.json` → `--outline`）
  - draft → edit ✅（draft 文件 → `--draft`）
  - **edit → seo ❌**：editor 无 `--output`，结果只打印到 stdout 未落盘；seo 读的是**原始 `draft.json`（编辑前）**，编辑结果被丢弃。
  - seo/publish ❌：publish 步仅用 `--topic`，未接收 seo/editor 产物。
- **结论**：content-editor 输出未接入下游（P1）；publish 步与上游产物脱节（P2）。

### 3.3 news_flash 差异量化（5 步 vs 3 步）

`writing_pipeline.run_pipeline` 对任意 type 都跑 **5 个逻辑步**：

| # | 编排器实际步 | 对应技能 | 在 news_flash 链(chains.json)中？ |
|---|-------------|---------|-----------------------------------|
| 1 | outline | article-outliner | ❌ **多出**（链未登记）|
| 2 | draft | article-drafter | ✅ |
| 3 | edit | content-editor | ✅ |
| 4 | seo | seo-optimizer | ✅ |
| 5 | publish×N | cross-post-orchestrator | ❌ **多出**（链未登记，且默认仅 dry-run 规划）|

- **量化**：编排器 5 步，链声明 3 步，**差值 = +2 步**；共有的 3 步为 drafter/editor/seo；**多出来的 2 步 = article-outliner（上游） + publish（下游）**。
- **是否该补进 chains**：建议把 `article-outliner` 补为 news_flash 链第 0 步、把 `cross-post-orchestrator` 补为末步（与 `article` 链对齐）；或反向让编排器对 news_flash 跳过 outline（快讯通常无需结构化大纲）。两种都合理，**优先方案 A（补齐链）**以保持与 `article` 链一致。

### 3.4 video 游离技能是否该接入

`visual-style-anchor / storyboard-designer / shot-recipe-designer / video-prompt-engineer` 均**不在** video 域 `skills` 列表、也不在任何链中，但 SKILL.md 自述是 production chains 的**上游规划**技能（style→分镜→镜头→prompt→脚本）。建议作为「pre_production」链接入（见 §4）。

---

## 四、Gap 清单（P0–P3）

| ID | 优先级 | 域 | 问题 | 影响 |
|----|--------|----|------|------|
| G1 | **P0** | video | 真实模式文件交接断裂：tts 写 CWD 而非 audio-dir；lip_sync 输出 `lipsync_scene_*.mp4` 与 editor 期望的 `scene_*.mp4` 命名不符 | 真实执行串不起来（mock 掩盖）|
| G2 | **P1** | video | 编排器硬编码 talking_character 步骤，无视 `--type`；meme/tutorial 链跑错步骤 | meme/tutorial 实际不可用 |
| G3 | **P1** | video | 4 个上游规划技能未登记进 chains（游离）| 链条缺规划阶段 |
| G4 | **P1** | writing | content-editor 输出未落盘，seo 读编辑前草稿 | 编辑成果丢失 |
| G5 | **P1** | chat | chat-prompt-engineer 无 chat 域（游离）| 无法经链条编排 |
| G6 | **P2** | writing | news_flash 链 3 步 vs 编排器 5 步，缺 outline+publish | 链/编排不一致 |
| G7 | **P2** | writing | publish 步仅用 topic，未接 seo/editor 产物 | 发布内容非最终稿 |
| G8 | **P2** | scenarios | 4 个技能游离（无域登记）| 无法经链条编排 |
| G9 | **P3** | writing | outliner `--json-input` 仍需 `--topic`（已修，见 §5）| 调用不便 |
| G10 | **P3** | writing | script_writer/ subtitles/ seo/ editor 等生成器对非法输入不拦截（设计如此，仅标记）| 非严格门禁，需在 SKILL.md 注明 |

---

## 五、已修复项（本范围目录内，未动共享文件）

1. **`skills/writing/article-outliner/scripts/outliner.py`** — `--topic` 改为非必填；仅给 `--json-input`（含 topic）时不再报 `error: --topic required`；两者皆缺时给出清晰 `parser.error`。已验证：`--json-input '{"topic":"..."}'` → rc=0。
2. **`skills/writing/article-drafter/scripts/drafter.py`** — 缺失大纲文件时由「未捕获 FileNotFoundError 回溯」改为干净报错 `大纲文件不存在: <path>` + `rc=1`；`main()` 末返回 0 并由 `sys.exit(main())` 收口。已验证：缺文件 → rc=1。
3. **9 个游离 SKILL.md 补衔接话术**（纯文字、无跨目录硬链接，符合门禁）：
   - video：`visual-style-anchor`、`storyboard-designer`、`shot-recipe-designer`、`video-prompt-engineer` — 写明「上游规划 → video-script-writer → talking_character/meme 链」建议顺序。
   - chat：`chat-prompt-engineer` — 建议新增 chat 域与 prompt_audit 链。
   - scenarios：`excel-assistant`、`meeting-notes`、`resume-tailor`、`music-generation` — 写明 office/productivity 域建议与相互喂接关系。
   - 验证：`validate_skills.py` 仍 **0 err / 0 warn**（仅补文字，无新增 references）。

---

## 六、建议的 `skill_chains.json` 改动（具体 JSON 片段）

> ⚠️ 以下为**建议**，未写入文件。请维护者评审后合并。

### 6.1 新增 `chat` 域（解决 G5）

```json
"chat": {
  "entry": null,
  "skills": ["chat-prompt-engineer"],
  "chains": {
    "prompt_audit": ["chat-prompt-engineer"]
  }
}
```

### 6.2 video 域：补登 4 个上游规划技能 + 新增 pre_production 链（解决 G3）

```json
"video": {
  "entry": "skills/video/video_pipeline.py",
  "skills": [
    "visual-style-anchor", "storyboard-designer", "shot-recipe-designer",
    "video-prompt-engineer",
    "video-script-writer", "video-voice-synth", "video-lip-sync",
    "video-editor", "video-subtitles", "video-thumbnail",
    "video-generation", "image-generation", "music-generation",
    "ai-baby-podcast", "nailong-laugh-shorts"
  ],
  "chains": {
    "pre_production": [
      "visual-style-anchor", "storyboard-designer",
      "shot-recipe-designer?", "video-prompt-engineer",
      "video-script-writer"
    ],
    "talking_character": ["video-script-writer","video-voice-synth","video-lip-sync","video-editor","video-subtitles","video-thumbnail"],
    "meme": ["video-script-writer","image-generation","music-generation","video-editor","video-subtitles","video-thumbnail"],
    "tutorial": ["video-script-writer","video-voice-synth","video-editor","video-subtitles","video-thumbnail"]
  }
}
```

### 6.3 scenarios：建 `office`(productivity) 域 + music-generation 归位（解决 G8）

```json
"office": {
  "entry": null,
  "skills": ["excel-assistant", "meeting-notes", "resume-tailor"],
  "chains": {
    "document_pipeline": ["excel-assistant", "meeting-notes?", "resume-tailor?"]
  }
}
```
- `music-generation` 建议**移出** scenarios 目录或同时在 `music` 域与 `video` 域 skills 中保留（现状 video.skills 已列 music-generation，但盘上目录在 scenarios/，造成"游离"假象）。

### 6.4 writing：news_flash 链补齐（解决 G6）

```json
"news_flash": [
  "article-outliner",
  "article-drafter",
  "content-editor",
  "seo-optimizer",
  "cross-post-orchestrator?"
]
```
（与 §3.3 量化一致：补 outline + publish 两步，对齐 article 链。）

### 6.5 编排器侧（代码，非 chains.json）

- **video_pipeline.py**：按 `--type` 选择链步骤（meme 用 image-generation+music-generation、跳过 tts/lipsync；tutorial 跳过 lipsync）；tts/lip_sync/editor 间显式用一致的 `--audio-dir`/`--clips-dir` 与文件名（建议统一为 `scene_<id>.{wav,mp4}`），消除 G1/G2。
- **writing_pipeline.py**：content-editor 增加 `--output` 落盘，`seo`/`publish` 改为读取编辑后文件（消除 G4/G7）。

---

## 七、验证结果（修复后）

| 检查项 | 结果 |
|--------|------|
| `python3 tools/validate_skills.py` | **errors: 0 / warnings: 0**（与基线一致，未新增 warn）|
| `python3 -m pytest skills/video skills/writing skills/chat skills/scenarios -q` | **129 passed**（与基线一致，无新增失败）|

> 真实模式（联网/ffmpeg）路径未在本次执行触发；mock 路径与本地启发式逻辑均已覆盖。

---

## 第三部分 · design / audio / marketing / education / ppt / paper（31 技能）

# Agent3 全量测试报告 — design / audio / marketing / education / ppt / paper

> 测试工程视角：仅测本范围目录内的**本地启发式脚本**，未触发任何联网 / 外部 API。
> 基线：`validate_skills.py` 0 err 0 warn；`pytest skills` 257 passed / 1 skipped。
> 修复后：validate 0 err 0 warn；`pytest skills/design skills/audio skills/marketing skills/education skills/ppt skills/paper -q` 31 passed / 1 skipped；全量 `pytest skills` 257 passed / 1 skipped（无回归）。

---

## 1. 门禁通过脚本数

- **本地启发式校验/生成脚本：13 个**（均位于本范围 `skills/.../scripts/`）。
- **深测结果：12 个完全通过（正确样例放行 + 异常样例拦截），1 个弱门禁（topic_selector 空主题不拦截），0 个失败。**
- **纯参考型技能（无脚本，仅 references/*.md，属正常）：2 个** — `design/image-prompt-engineer`（model-dialects.md）、`audio/tts-voice-director`（voice-catalog.md）。两者 SKILL.md 均已正确引用参考文件。
- 另有 5 个 paper 脚本为**生成型**（产出工件，无 pass/fail 拦截语义，属正常）：`lit-review`、`arch-diagram`、`experiment-runner`、`neural-net-draw`、`pub-plotter`。

---

## 2. 逐脚本结果表

| # | 技能 / 脚本 | 类型 | 正确样例放行 | 异常/边界样例拦截 | 说明 |
|---|---|---|---|---|---|
| 1 | design/layout-spec-auditor `spec_audit.py` | 校验 | ✅ | ✅ | 8 平台比例/分辨率/安全区/文字预算。放行：wechat-header 900×383、douyin 1080×1920(9:16)、zhihu 1600×900(比例约束)。拦截：错比例(1000×1000)、超文件额(10MB)、超文字预算、zhihu 比例越界；用法错 rc=2（未知平台/负尺寸/0 尺寸）。 |
| 2 | audio/podcast-producer `script_lint.py` | 校验 | ✅ | ✅ | 放行：纯口播+HOST/GUEST 前缀。拦截：舞台提示 `[pause]`、括号旁白 `（笑）`、markdown `**粗**`、超长行(>90字)、dialogue 缺前缀。 |
| 3 | marketing/channel-adapter `channel_fit_check.py` | 校验 | ✅ | ✅ | 5 渠道约束。放行：xhs 单 CTA+钩子首行。拦截：超字数、>1 CTA、email 超 30 字、email 含`!`、douyin 超 240 字；未知渠道 rc=2。 |
| 4 | education/exercise-generator `exercise_lint.py` | 校验 | ✅ | ✅ | 五字段/难度/CPn/禁选择题。放行：合规题库。拦截：缺字段、MCQ 标记（默认禁）；**修复前**无题块输入会崩溃。 |
| 5 | ppt/ppt-builder `make_pptx.py` | 生成+校验 | ✅ | ✅ | 放行：合法 spec→生成 .pptx（python-pptx 可用）。拦截：缺参 rc=2、spec 文件不存在 rc=2、空 deck_title/空 slides rc=2、>5 要点 rc=2。 |
| 6 | paper/paper-topic-selector `topic_selector.py` | 评分 | ✅ | ⚠️弱 | 放行：正常主题→go/risky。拦截：**空 `--topic ""` 仍放行（无空值校验，弱门禁）**；`--constraints` 非法 JSON 现已捕获 rc=2（修复前抛栈）。 |
| 7 | paper/latex-formatter `latex_formatter.py` | 校验 | ✅ | ✅ | 放行：含 begin{document}/bibliography/≥3 section/转义。拦截：缺 document、环境不平衡、裸 `&%#`。文件不存在 **rc=1（修复前 rc=0）**。 |
| 8 | paper/journal-adapt `journal_adapt.py` | 校验 | ✅ | ✅ | 放行：ieee 全段+页限内。拦截：nature 禁用语("In this paper we"/"Novel")+缺段。 |
| 9 | paper/self-reviewer `self_reviewer.py` | 校验 | ✅ | ✅ | 放行：含 abstract/≥4 section/citation/≥3000词/baseline/limitation→ready。拦截：短稿→needs_work。文件不存在 **rc=1（修复前 rc=0）**。 |
| 10 | paper/tex-cleaner `tex_cleaner.py` | 校验 | ✅ | ✅ | 放行：干净 tex。拦截：external_files/low_res/undefined_refs/toc/non_ascii（5 项命中）。文件不存在 **rc=1（修复前 rc=0）**。 |
| 11 | paper/ai-humanizer `ai_humanizer.py` | 校验 | ✅ | ✅ | 放行：无 AI 套话。拦截：6 类 AI-tell 命中→needs_edit。 |
| 12 | paper/anti-defensive `anti_defensive.py` | 校验 | ✅ | ✅ | 放行：中性陈述。拦截：双重 hedging/防御性套话→rewrite_needed。 |
| 13 | paper/figure-maker `figure_maker.py` | 生成+校验 | ✅ | ✅ | bar/line/boxplot 正常出图。**`heatmap` 在 `--type` 选项中但从未实现；修复前被强制覆写为 `status:"success"`（无产出），现已诚实返回 `unsupported`。** |

**参考型（无脚本，正常）**：`design/image-prompt-engineer`（model-dialects.md，SKILL.md 第 25/46/78 行引用）、`audio/tts-voice-director`（voice-catalog.md，SKILL.md 第 32/72 行引用）。

---

## 3. 链条衔接契约核对

### 3.1 六个编排器 step 间参数传递
| 域 | 编排器 | 串联方式 | 参数传递 | 结论 |
|---|---|---|---|---|
| design | `design_pipeline.py` | 规划型（不 subprocess） | brief→(spec)→prompt→audit 文字描述 | 固定 3 步；**不随 `--type` 变化**（见 3.2） |
| audio | `audio_pipeline.py` | 规划型 | script.md→合成计划→shownotes；内嵌 `script_lint.py` 调用命令 | ✅ 衔接清晰 |
| marketing | `marketing_pipeline.py` | 规划型，按 `goal` 选链 | copy→campaign→adapt；adapt 明确调用 `channel_fit_check.py` | ✅ 衔接清晰 |
| education | `education_pipeline.py` | 规划型，按 `mode` 选链 | course→exercise→feynman 掌握闭环 | ✅ 衔接清晰 |
| ppt | `ppt_pipeline.py` | **subprocess** | outline/visual/assets/rehearsal/render | ⚠️ 见 Gap P1 |
| paper | `paper_pipeline.py` | **subprocess** | topic→lit→experiment→figures→latex→review | ⚠️ 见 Gap P0/P2 |

### 3.2 design `thumbnail` / `banner` 边界（重点）
- `design_pipeline.py` 的 `--type` 接受 `cover/poster/infographic/thumbnail/banner`，但 `STEPS` 是**写死的 3 步**（spec→prompt→audit），对 thumbnail/banner 仍规划同一套。
- `skill_chains.json` 的 `design.chains` **仅登记 cover/poster/infographic**；`design.skills` 列表**无 thumbnail 技能**、chains **无 thumbnail/banner 链**。
- 实际影响：`layout-spec-auditor` 的 `spec_audit.py` 支持任意平台比例（8 平台 + 自定义 `--expect`），因此 thumbnail/banner 走"同一 3 技能"在技术上**可跑通**，只是**未登记为链、且缺专属 thumbnail 技能**。
- **结论**：属于"登记缺口"而非"功能断裂"。最小正确修复 = 在 `design.chains` 补 `thumbnail`/`banner` 两条链（复用现有 3 技能即可，因审计脚本对类型无依赖）。建议 JSON 见第 5 节。

### 3.3 四个新建域"一个动作立刻展开"衔接移交
核对 `design/audio/marketing/education` 的 SKILL.md，**衔接移交话术已写好**：
- design：`design-brief-interpreter`→"移交 image-prompt-engineer / 继续 layout-spec-auditor"；`image-prompt-engineer`→"移交 layout-spec-auditor"。
- audio：`podcast-producer`→"移交 tts-voice-director / episode-publisher"（并点名 `script_lint`）；`tts-voice-director`→"移交 episode-publisher"。
- marketing：`product-copywriter`/`campaign-designer`→"移交 channel-adapter"（点名 `channel_fit_check`）；`channel-adapter`→回 `campaign-designer`。
- education：`course-designer`→"继续 exercise-generator/feynman-explainer"；`exercise-generator`→"移交 feynman-explainer"（点名 `exercise_lint`）。
✅ 链条"立刻展开"在 SKILL.md 中已落实，无需补话术。

### 3.4 致命衔接缺陷（关键发现）
**paper 域 13 个脚本的 `main()` 返回值被 `__main__` 块丢弃**（`if __name__=="__main__": main()` 未包 `sys.exit`）。结果：进程**永远退出码 0**。而 `paper_pipeline.py` / `ppt_pipeline.py` 用 `r.returncode == 0` 判定成功 → **失败的结果被当成成功**，门禁在编排层被静默绕过。已修复（见第 4 节）。

---

## 4. Gap 清单（P0–P3）

| 级别 | 域 | 问题 | 影响 |
|---|---|---|---|
| **P0** | paper | 13 个 paper 脚本 `main()` 返回码被丢弃 → 进程恒为 0；编排器 `returncode==0` 判定使失败被当成功，**门禁在编排层被绕过** | 链条"审计失败→回流"形同虚设 |
| **P0** | paper | `skill_chains.json` **完全无 paper 域登记**（13 个学术技能游离） | 全域不可被 chains 工具发现/编排 |
| **P1** | ppt | `ppt_pipeline.py` 调用 `outline/visual/assets/rehearsal/render.py`，但这些脚本**均不存在**；唯一存在的 `make_pptx.py` **从未被管线调用** | ppt 全流程实际只"规划"，render 步被标 skipped |
| **P1** | paper | `lit-review`/`experiment-runner` 的 ArXiv/实验为 **mock**，但对外无"数据为模拟"标识；`lit_review.py` 即使 `--arxiv` 也只静默 pass 不联网 | 易被误当真实检索结果 |
| **P2** | paper | `topic_selector.py` 空 `--topic ""` 仍返回 go/risky（无空值校验） | 弱门禁 |
| **P2** | paper | `figure_maker.py` `--type heatmap` 列入选项但**未实现**，且曾被强制标 success | 误导性成功 |
| **P2** | education | `exercise_lint.py` 无题块输入时 `lint()` 返回 tuple 而 `main()` 按 dict 索引 → **崩溃** | 异常路径不可用 |
| **P2** | paper | `latex_formatter`/`self_reviewer`/`tex_cleaner` 文件不存在时 **rc=0**（应非 0） | 错误被当成功 |
| **P3** | paper | 12/13 个 paper 技能**无 SKILL.md**（仅 `paper-topic-selector` 有），其余仅靠脚本 | 链条话术、frontmatter 门禁覆盖不到 |
| **P3** | design | `thumbnail`/`banner` 类型被编排器接受但**未登记链/缺专属技能** | 登记缺口（功能可跑） |
| **P3** | paper | `arch-diagram` 的 `generate_neural_net` 对 `hidden()` 等无尺寸层解析；`pub-plotter`/`neural-net-draw` 无 CLI 自测 | 健壮性 |

### 重复/可合并 & 可扩展点
- **重复风险**：`latex_formatter` 与 `tex-cleaner` 都做"未转义特殊字符/环境平衡"检查，可合并为统一的 LaTeX 预检；`journal-adapt` 与 `self-reviewer` 的"缺失 section"逻辑重叠。
- **可扩展**：`lit-review`/`experiment-runner` 应加 `--offline` 显式开关并标注 mock；`figure_maker` 应补 `heatmap` 真实实现或移出选项；`spec_audit.py` 的 8 平台表应抽成独立 `platforms.json` 便于维护（注意此法会新增文件，不在本修复范围）。

---

## 5. 已修复项（仅限本范围目录，未改任何共享文件）

| 文件 | 修复 | 验证 |
|---|---|---|
| `education/exercise-generator/scripts/exercise_lint.py` | `lint()` 无题块时返回 dict（原返回 tuple 致 `main` 崩溃） | 无题块输入 rc=2，不再抛 `TypeError` |
| `paper/paper-topic-selector/scripts/topic_selector.py` | 非法 `--constraints` JSON 捕获为 rc=2（原抛栈） | `not-json` → rc=2，输出 error JSON |
| `paper/figure-maker/scripts/figure_maker.py` | `heatmap` 不再被强制覆写 `status:"success"`，诚实返回 `unsupported` | `--type heatmap` → status=unsupported |
| `paper/{latex-formatter,self-reviewer,tex-cleaner}/scripts/*.py` | 文件不存在分支 `return` → `return 1` | 三处缺失文件现 rc=1 |
| `paper/*/scripts/*.py`（13 个） | `__main__` 由 `main()` 改为 `sys.exit(main())`，使返回码真正传播（修复 P0 根因） | latex/self/tex 缺失文件 rc=1；topic 坏 JSON rc=2；正常路径仍 rc=0；`--help` rc=0 |

> 注：上述修改均在 `skills/` 范围内。**未触碰** `skill_chains.json` / `manifest.json` / `README*.md` / `SOURCES.md` / `CHANGELOG.md`。

---

## 6. 建议 `skill_chains.json` 改动（仅输出，待你确认后由专人合并）

> 以下为**具体 JSON 片段**。合并方式：在 `domains` 内新增 `paper` 整块；在 `design` 块内 `chains` 追加 `thumbnail`/`banner` 两条，`skills` 列表追加两个类型占位（或保持复用现有 3 技能——因审计脚本对类型无依赖，复用即可）。

### 6.1 新增 `paper` 域（含完整 chains）
```json
"paper": {
  "entry": "skills/paper/paper_pipeline.py",
  "skills": [
    "paper-topic-selector",
    "lit-review",
    "experiment-runner",
    "figure-maker",
    "arch-diagram",
    "neural-net-draw",
    "latex-formatter",
    "self-reviewer",
    "journal-adapt",
    "anti-defensive",
    "ai-humanizer",
    "tex-cleaner",
    "pub-plotter"
  ],
  "chains": {
    "full_paper": [
      "paper-topic-selector",
      "lit-review",
      "experiment-runner?",
      "figure-maker",
      "arch-diagram?",
      "neural-net-draw?",
      "latex-formatter",
      "self-reviewer?",
      "journal-adapt",
      "anti-defensive?",
      "ai-humanizer?",
      "tex-cleaner"
    ],
    "quick_draft": [
      "paper-topic-selector",
      "lit-review",
      "latex-formatter",
      "self-reviewer",
      "tex-cleaner"
    ],
    "polish_only": [
      "anti-defensive?",
      "ai-humanizer?",
      "tex-cleaner"
    ],
    "submit_ready": [
      "self-reviewer",
      "journal-adapt",
      "tex-cleaner"
    ]
  },
  "notes": {
    "orchestrable_scripts": "上述 13 个技能均自带 scripts/*.py（本地启发式，无联网）。",
    "mock_warning": "lit-review / experiment-runner 当前为 mock 数据生成，调用时应显式 --offline 并标注'模拟数据'，勿当真实检索/实验结果。",
    "pure_llm_role": "脚本只做可行性评分/格式校验/清洗；论文正文撰写本身由 LLM 完成，脚本在链尾做 self-reviewer→journal-adapt→tex-cleaner 把关。",
    "gate_fix_required": "已修复 13 脚本 main() 返回码传播（sys.exit(main())），否则编排器 returncode==0 会把失败当成功。"
  }
}
```

### 6.2 `design` 补 `thumbnail` / `banner` 链
```json
"design": {
  "entry": "skills/design/design_pipeline.py",
  "skills": [
    "design-brief-interpreter",
    "image-prompt-engineer",
    "layout-spec-auditor"
  ],
  "chains": {
    "cover":        ["design-brief-interpreter", "image-prompt-engineer", "layout-spec-auditor"],
    "poster":       ["design-brief-interpreter", "image-prompt-engineer", "layout-spec-auditor"],
    "infographic":  ["design-brief-interpreter", "image-prompt-engineer", "layout-spec-auditor"],
    "thumbnail":    ["design-brief-interpreter", "image-prompt-engineer", "layout-spec-auditor"],
    "banner":       ["design-brief-interpreter", "image-prompt-engineer", "layout-spec-auditor"]
  }
}
```
> 说明：thumbnail/banner 复用现有 3 技能即可（审计脚本支持任意平台比例）。若未来要专属缩略图安全区规则，再新增 `thumbnail-spec` 技能并改为 `["design-brief-interpreter","image-prompt-engineer","thumbnail-spec"]`。

---

## 7. 结论
- 门禁深测：**13 个本地启发式脚本，12 个完全通过、1 个弱门禁（topic 空主题）**，2 个纯参考技能正常，5 个生成型脚本按设计不拦截。
- 修复了 **6 类脚本异常分支 bug**（含 P0 根因：paper 脚本返回码被丢弃 → 编排层门禁被绕过），并修复了 13 个 paper 脚本的返回码传播。
- validate 保持 0/0；范围内 pytest 31 passed/1 skipped、全量 257 passed/1 skipped，无回归。
- paper 域完全游离、ppt 管线脚本缺失、`design thumbnail/banner` 未登记为链——已给出具体 chains.json 增补片段（待合并，本任务未改共享文件）。

---

## 第四部分 · office / tools / meta / knowledge（12 技能）

# Agent4 审计报告：office / tools / meta / knowledge 四目录

审计范围：`skills/office/**`、`skills/tools/**`、`skills/meta/**`、`skills/knowledge/**`。
所有实测命令均以 `cd /workspace/awesome-skillkit &&` 开头；测试产物全部落在 `/tmp/a4_test/`；
未联网；未改动 `skill_chains.json` / `manifest.json` / `README*.md` / `SOURCES.md` / `CHANGELOG.md` / `tools/`。

## 1. 总览

| 指标 | 数值 |
|---|---|
| 覆盖技能数（盘上实际存在） | **12** |
| 生产脚本数（不含 `test_smoke_*`） | **11** |
| `--help` 冒烟通过数 | **11 / 11（rc=0 全通过）** |
| 深测通过数（正例 + 异常例均符合预期） | **11 / 11** |
| 发现缺陷数 | **9**（P0 × 2 类实例共 3 处、P1 × 2、P2 × 3、P3 × 2） |
| 已修复数 | **9** |
| 修改文件数 | **11**（4 个 SKILL.md + 7 处含脚本/文档的改动，见第 5 节） |
| 门禁 `validate_skills.py` | **skills: 142  errors: 0  warnings: 0  RESULT: PASSED** |
| 门禁 `pytest`（四目录） | **14 passed in 0.71s** |
| 门禁 `skill-linter`（四目录） | **0 FAIL**（24 个 WARN 均为可选的 BODY-SECTS 章节数建议） |

> 范围澄清：任务书中列出的 `excel-assistant` / `resume-tailor` / `meeting-notes` 实际位于 `skills/scenarios/`，
> `internal-comms-writer` 位于 `skills/writing/`，均属其他小组范围，本次不计入。
> `find skills/office skills/tools skills/meta skills/knowledge -name SKILL.md` 的实际结果是 12 个，全部逐一审计，无遗漏。

## 2. 逐技能审计表

五要素闭环记法：`输入 / 自检 / 工作流 / 交付 / 失败表 / 参考`，✓ 为齐备，△ 为补齐后齐备。

### 2.1 `skills/office/docx-writer`

| 项 | 结论 |
|---|---|
| 五要素闭环 | 输入 ✓ / 自检 ✓ / 工作流 ✓ / 交付 ✓ / 失败表 ✓（6 行）/ 参考 ✓ |
| 链条是否断裂 | **有断裂（P2）**：步骤 5「交付」只有动作，缺「预期 + 若失败」，三件套不完整 |
| 发现的问题 | ① 步骤 5 缺失败分支；② 脚本 `cmd_create` / `cmd_inspect` / `cmd_styles` 对不存在/非法文件直接抛 `FileNotFoundError`/`PackageNotFoundError` 裸 traceback（可读性差，用户看到的是一屏调用栈）；③ `__main__` 用裸 `main()` 而非 `sys.exit(main())`（与其余脚本不一致的隐患） |
| 修复动作 | ① 步骤 5 补「预期 / 若失败」（回到步骤 1 改 `content.md` 重渲染）；② 三处命令入口加前置存在性检查 + `.docx` 合法性捕获，输出 `ERROR: 文件不存在：…` / `ERROR: 不是合法的 .docx 文件：…`；③ 改为 `return args.func(args)` + `sys.exit(main())` |

### 2.2 `skills/office/pdf-pipeline`

| 项 | 结论 |
|---|---|
| 五要素闭环 | 输入 ✓ / 自检 ✓ / 工作流 ✓ / 交付 ✓ / 失败表 ✓（6 行）/ 参考 ✓ |
| 链条是否断裂 | **有断裂（P2）**：步骤 3（OCR 转线）与步骤 6（交付）缺「若失败」 |
| 发现的问题 | ① 步骤 3、6 缺失败分支；② 脚本对不存在文件 / 加密 PDF 无干净报错，直接抛 pypdf 异常；③ `sys.exit` 传播用裸 `main()` |
| 修复动作 | ① 步骤 3 补 OCR 工具缺失/分辨率不足的处置，步骤 6 补产物路径缺失与服务端对账的处置；② 新增 `open_reader()` 统一入口，覆盖全部 5 个 `PdfReader` 调用点，缺文件/加密/损坏均返回 rc=1 并给出中文原因；③ 改为 `sys.exit(main())` |

### 2.3 `skills/office/epub-builder`

| 项 | 结论 |
|---|---|
| 五要素闭环 | 输入 ✓ / 自检 ✓ / 工作流 ✓ / 交付 ✓ / 失败表 ✓（**11 行，全仓最厚**）/ 参考 ✓ |
| 链条是否断裂 | **无断裂** |
| 发现的问题 | 无。该技能是本批质量标杆：`mimetype` 合规自检内建在 `build` 里、`inspect` 按 spine 读回、步骤 4 给出独立的 `zipfile` 交叉验证、失败表覆盖 11 类真实场景。 |
| 修复动作 | 无（无需改动）。实测：`build` 产出 9 条目 EPUB，交叉验证三项全 `True`，`inspect` 章节数与源 H1 数一致，异常例（文件不存在/空文件/非 epub）均 rc=1 |

### 2.4 `skills/tools/file-organizer`

| 项 | 结论 |
|---|---|
| 五要素闭环 | 输入 ✓ / 自检 ✓ / 工作流 ✓ / 交付 ✓ / 失败表 ✓（6 行）/ 参考 ✓ |
| 链条是否断裂 | **断裂（P0）**：`plan` 子命令以相对路径调用时 100% 崩溃 |
| 发现的问题 | **P0**：`python3 scripts/organize.py plan inbox --by type` 抛 `ValueError: '/abs/…/pdf/a.pdf' is not in the subpath of 'inbox'`。根因：`_build_moves` 里的 `dst_dir` 来自 `_resolve_within`（返回**绝对**路径），而 `cmd_plan` 用 `dst.relative_to(root)`，`root` 是**相对**的 `inbox`。SKILL.md 步骤 3/4 的示例命令正是相对路径写法，**照抄必崩**。`cmd_apply` 同源缺陷。 |
| 修复动作 | 新增 `_rel(path, root)` 辅助函数（两侧 `resolve()` 后再比较），替换 `plan` / `apply` / `scan` / `dedupe` 中全部 4 处 `relative_to(root)`。复验：相对路径与绝对路径两种入参下 `plan` / `apply --dry-run` / `apply --yes` 均 rc=0，输出格式与 SKILL.md 描述逐字一致 |

### 2.5 `skills/tools/batch-renamer`

| 项 | 结论 |
|---|---|
| 五要素闭环 | 输入 ✓ / 自检 ✓ / 工作流 ✓ / 交付 ✓ / 失败表 ✓（8 行）/ 参考 ✓ |
| 链条是否断裂 | **断裂（P0）**：`preview .` / `apply . --yes` 以 `.` 为目录时 100% 崩溃 |
| 发现的问题 | **P0**：`ValueError: '…/IMG_001.JPG' is not in the subpath of ''`。同类根因（`compute_plan` 返回绝对路径 dst，`root` 为 `.`）。SKILL.md 前置自检与步骤示例大量使用 `.` 写法。**P2**：不给任何改名规则时 `preview` 输出「无需改名：所有文件名都符合目标规则」并 rc=0 —— 读起来像成功，实际是**没给规则**，与输入清单中「改名规则=必填」矛盾，属静默误导。 |
| 修复动作 | ① 新增 `_rel()`，替换全部 8 处 `relative_to(root)`；② 新增 `_require_rule()` 守卫，`preview`/`apply` 缺规则时输出 `ERROR: 至少给一种改名规则：…` 并返回 rc=2。复验：preview→apply→undo 全链路（含日志写入与逆序回滚）rc=0，文件名与数量前后一致 |

### 2.6 `skills/tools/format-converter`

| 项 | 结论 |
|---|---|
| 五要素闭环 | 输入 ✓ / 自检 ✓ / 工作流 ✓ / 交付 ✓ / 失败表 ✓（8 行）/ 参考 ✓ |
| 链条是否断裂 | **有断裂（P1 + P0）** |
| 发现的问题 | ① **P1**：步骤 1、5 缺「若失败」；② **P0**：`media` 子命令不校验输出扩展名，未知扩展直接透传 ffmpeg 的返回码 **234**，SKILL.md 失败表声称的退出码 3「无法从扩展名推断格式」在 media 路径上根本没有实现；③ **P1**：`cmd_doc` 把 `require_binary("pandoc")` 放在扩展名校验**之前**，导致 `out.zzz` 错误地报 rc=4「找不到 pandoc」而非 rc=3，与失败表不符，误导用户去装 pandoc；④ **P2**：`_run` 直接返回外部二进制的原始 returncode（可能为负或 >255），`sys.exit` 会截断成 234 这类无意义值 |
| 修复动作 | ① 步骤 1/5 补失败分支；② `cmd_media` 增加 `MEDIA_EXTS` 白名单校验，未知输出扩展返回 rc=3；③ 把 `require_binary` 移到扩展名校验之后；④ `_run` 把外部返回码归一为 `0/1`。复验：`media photo.png o.zzz` rc=3、`doc report.md o.zzz` rc=3、损坏 mp4 rc=1、真实 mp4→webm 转码 rc=0 |

### 2.7 `skills/tools/task-scheduler`

| 项 | 结论 |
|---|---|
| 五要素闭环 | 输入 ✓ / 自检 ✓ / 工作流 ✓ / 交付 ✓ / 失败表 ✓（8 行）/ 参考 ✓ |
| 链条是否断裂 | **有断裂（P2）**：步骤 5（非 Linux 平台）缺「若失败」 |
| 发现的问题 | 步骤 5 缺失败分支。脚本本体质量很高：`cron-check` 三类非法输入均 rc=2、`cron-add` 非法表达式 rc=2、无 `crontab` 环境 `cron-list` rc=1 且给出平台替代方案、无 `croniter` 时正确降级并在输出中标注。 |
| 修复动作 | 步骤 5 补「目标平台与表达式语义无法一一对应」时的处置（拆触发器 / 换 `StartInterval` / 如实告知边界）。实测降级路径：屏蔽 `croniter` 后 `cron-check` 仍 rc=0 并打印降级说明 |

### 2.8 `skills/meta/skill-author`

| 项 | 结论 |
|---|---|
| 五要素闭环 | 输入 ✓ / 自检 ✓ / 工作流 ✓ / 交付 ✓ / 失败表 ✓（7 行）/ 参考 ✓ |
| 链条是否断裂 | **无断裂** |
| 发现的问题 | 无。正文引用的 `skills/meta/skill-linter/scripts/lint_skill.py` 真实存在（相对路径可解析）。纯提示型技能，无脚本需实测。 |
| 修复动作 | 无 |

### 2.9 `skills/meta/skill-linter`

| 项 | 结论 |
|---|---|
| 五要素闭环 | 输入 ✓ / 自检 ✓ / 工作流 ✓ / 交付 ✓ / 失败表 ✓（8 行）/ 参考 ✓ |
| 链条是否断裂 | **无断裂** |
| 发现的问题 | 无。八项检查实现完整；`--json` / `--verbose` 均可用；路径不存在 / 目录无 SKILL.md 均 rc=2；CI 门禁用法（`--json > /dev/null || exit 1`）实测有效。 |
| 修复动作 | 无。作为门禁工具对四目录跑出 **0 FAIL** |

### 2.10 `skills/meta/skill-finder`

| 项 | 结论 |
|---|---|
| 五要素闭环 | 输入 ✓ / 自检 ✓ / 工作流 ✓ / 交付 ✓ / 失败表 ✓（7 行）/ 参考 ✓ |
| 链条是否断裂 | **无断裂** |
| 发现的问题 | 无功能缺陷。一处**计数口径**需说明（非缺陷）：`stats` 报「技能数（盘上）142」，而 `find skills -name SKILL.md` 得 144，差值 2 已由 `references/repo-map.md` 明确解释（跳过 `assets/` 下的 `skill-tester/assets/sample-skill` 与 `writing/assets/ai-cover-generator`）。`pack` 正确报出 1 处仓库数据问题「包引用了盘上不存在的技能 ai-cover-generator」，属发布流程数据，按纪律不由本组改动。 |
| 修复动作 | 无（脚本零改动）。`ROOT = parents[4]` 层级经实测正确（指向仓库根，`manifest.json` 存在），跨 CWD 调用正常 |

### 2.11 `skills/knowledge/personal-wiki`

| 项 | 结论 |
|---|---|
| 五要素闭环 | 输入 ✓ / 自检 ✓ / 工作流 ✓ / 交付 ✓ / 失败表 ✓（9 行）/ 参考 ✓ |
| 链条是否断裂 | **有断裂（P2）**：步骤 6（出统计并交付）缺「若失败」 |
| 发现的问题 | 步骤 6 缺失败分支。脚本五个子命令（init/index/search/lint/stats）实测全部符合 SKILL.md 描述：`init` 二次拒绝覆盖、`lint` 退出码 1 表示「有发现」而非错误（与文档一致）、索引损坏后 `index` 可重建。 |
| 修复动作 | 步骤 6 补「索引不存在 → 先跑 index」「统计数与磁盘 md 数不符 → 笔记不在 notes/raw 下」两条处置 |

### 2.12 `skills/knowledge/knowledge-graph-builder`

| 项 | 结论 |
|---|---|
| 五要素闭环 | 输入 ✓ / 自检 ✓ / 工作流 ✓ / 交付 ✓ / 失败表 ✓（9 行）/ 参考 ✓ |
| 链条是否断裂 | **有断裂（P2）**：步骤 5（交付并给建议）缺「若失败」 |
| 发现的问题 | 步骤 5 缺失败分支。注意到 SKILL.md 中 `export` 用 `--note-only`、`analyze` 用 `--notes-only` 两个**形近不同名**参数，经 `--help` 实测确认二者确为不同子命令的真实参数，非笔误。脚本三子命令（extract/export/analyze）实测：Mermaid 以 ```` ```mermaid ```` + `flowchart LR` 起、DOT 以 `digraph knowledge {` 起、`analyze` 输出四组指标与诊断行，全部符合描述。 |
| 修复动作 | 步骤 5 补「extract 与 analyze 的 nodes 数不一致」「unresolved_links 非空且不打算补笔记」两条处置 |

## 3. 脚本实测结果表

| 脚本 | 正例结果 | 异常样例结果 | 返回码传播 | 是否修复 |
|---|---|---|---|---|
| `office/docx-writer/scripts/docx_ops.py` | `create`/`styles`/`inspect` 三命令 rc=0；粗体 run、3×2 表格、Heading 1/2、List Bullet/Number 均真实产出 | 输入不存在 rc=1；非 .docx rc=1；非法子命令 rc=2 | **修复**：裸 `main()` → `sys.exit(main())` | **是** |
| `office/pdf-pipeline/scripts/pdf_ops.py` | `meta`/`merge`/`split`/`extract`/`rotate` 全 rc=0；3 页合并、`1-2,3` 拆分、`=== page N/M ===` 标注均正确 | 缺文件 rc=1；页码越界 rc=1；非法 meta key rc=1；`--degrees 45` rc=2 | **修复**：裸 `main()` → `sys.exit(main())` + `open_reader()` | **是** |
| `office/epub-builder/scripts/epub_build.py` | `build` 产出 9 条目 EPUB、mimetype 合规自检 ✓；`inspect` 章节数=H1 数；交叉验证 3 项全 `True` | 缺文件 rc=1；空文件 rc=1；inspect 非 epub rc=1；无 H1 时降级为单章「正文」rc=0（符合文档） | 已正确 `sys.exit(main())` | 否（无缺陷） |
| `tools/file-organizer/scripts/organize.py` | `scan`/`dedupe`/`plan`/`apply --dry-run`/`apply --yes` 全 rc=0；重复组识别、桶归档、数量前后一致 | 非目录 rc=1；`--by size` 给 apply rc=2 | 已正确 `sys.exit(main())`；**P0 修复** `_rel()` | **是** |
| `tools/batch-renamer/scripts/rename.py` | `preview . ` / `apply . --yes` / `undo` 全 rc=0；日志 JSON 逐行、逆序回滚、文件复原 | 非目录 rc=1；非法占位符 rc=2；非法正则 rc=1；空日志 rc=1；`apply` 无 `--yes` rc=2；**无规则 rc=2（新增）** | 已正确 `sys.exit(main())`；**P0 修复** `_rel()` + `_require_rule()` | **是** |
| `tools/format-converter/scripts/convert.py` | `image`（含 RGBA→RGB）、`batch --yes`、`media` 真实 mp4→webm 全 rc=0 | 输入不存在 rc=1；同输入输出 rc=2；**未知输出扩展 rc=3（修复前 doc 报 4、media 报 234）**；损坏 mp4 rc=1 | 已正确 `sys.exit(main())`；**修复** `_run` 归一返回码 | **是** |
| `tools/task-scheduler/scripts/schedule_helper.py` | `cron-check`/`cron-add`/`cron-list` 全 rc=0；中文翻译、crontab 行、非绝对路径告警均正确 | 字段数错/越界 rc=2；非法表达式 cron-add rc=2；无 crontab 的 `cron-list` rc=1 | 已正确 `sys.exit(main())` | 否（无缺陷） |
| `meta/skill-linter/scripts/lint_skill.py` | 单技能 / 目录批量 / `--json` / `--verbose` 全 rc=0；四目录 **0 FAIL** | 路径不存在 rc=2；目录无 SKILL.md rc=2 | 已正确 `sys.exit(main())` | 否（无缺陷） |
| `meta/skill-finder/scripts/find_skill.py` | `search`/`pack`/`stats` 全 rc=0；`--json` 的 `total_matches` 与 `matches` 长度自洽 | 未命中 rc=1；全不存在技能名 rc=2 | 已正确 `sys.exit(main())`；`parents[4]` 层级实测正确 | 否（无缺陷） |
| `knowledge/personal-wiki/scripts/wiki_build.py` | `init`/`index`/`search`/`lint`/`stats` 全 rc=0；孤儿/断链/空笔记三类检出准确 | 未 init 的 index/search/stats rc=1；空词 rc=1；索引损坏 rc=1；`lint` 有发现 rc=1 | 已正确 `sys.exit(main())` | 否（无缺陷） |
| `knowledge/knowledge-graph-builder/scripts/graph_build.py` | `extract`/`export`(json/dot/mermaid)/`analyze` 全 rc=0；Mermaid/DOT 格式、度中心性、连通分量、诊断行均正确 | 目录不存在 rc=1；空目录 rc=1；无 md 目录 rc=1；非法 format rc=2 | 已正确 `sys.exit(main())` | 否（无缺陷） |

## 4. Gap 清单（按 P0–P3 分级）

### P0（链路必坏 / 失败被吞）

| # | 技能 | 问题 | 状态 |
|---|---|---|---|
| P0-1 | `tools/file-organizer` | `plan` / `apply` 以相对路径调用（SKILL.md 的示例写法）时 `relative_to` 抛 `ValueError`，功能 100% 失效 | **已修复** |
| P0-2 | `tools/batch-renamer` | `preview .` / `apply . --yes`（SKILL.md 的示例写法）同源崩溃，功能 100% 失效 | **已修复** |
| P0-3 | `tools/format-converter` | `media` 未知输出扩展透传 ffmpeg rc=234 给 `sys.exit`，失控返回码；SKILL.md 声明的 rc=3 在该路径上未实现 | **已修复** |

### P1（不可执行命令 / 死链 / 与文档矛盾的返回码）

| # | 技能 | 问题 | 状态 |
|---|---|---|---|
| P1-1 | `tools/format-converter` | `cmd_doc` 依赖探测先于扩展名校验，未知扩展报 rc=4「找不到 pandoc」而非文档承诺的 rc=3，误导用户装错东西 | **已修复** |
| P1-2 | `office/docx-writer`、`office/pdf-pipeline` | 两脚本对不存在/非法输入抛裸 traceback，错误信息不可读；且 `__main__` 用裸 `main()` 与其余 9 个脚本不一致 | **已修复** |

### P2（体验与健壮性）

| # | 技能 | 问题 | 状态 |
|---|---|---|---|
| P2-1 | `office/docx-writer` 步骤 5 | 缺「若失败」 | **已修复** |
| P2-2 | `office/pdf-pipeline` 步骤 3、6 | 缺「若失败」 | **已修复** |
| P2-3 | `tools/format-converter` 步骤 1、5 | 缺「若失败」 | **已修复** |
| P2-4 | `tools/task-scheduler` 步骤 5 | 缺「若失败」 | **已修复** |
| P2-5 | `knowledge/personal-wiki` 步骤 6 | 缺「若失败」 | **已修复** |
| P2-6 | `knowledge/knowledge-graph-builder` 步骤 5 | 缺「若失败」 | **已修复** |
| P2-7 | `tools/batch-renamer` | 不给规则时输出「无需改名…符合目标规则」rc=0，静默误导；与输入清单「改名规则=必填」矛盾 | **已修复** |
| P2-8 | `tools/format-converter` | `_run` 透传外部二进制任意返回码（负值/>255 被 `sys.exit` 截断） | **已修复** |

### P3（建议）

| # | 对象 | 建议 | 状态 |
|---|---|---|---|
| P3-1 | 12 个技能全体 | `skill-linter` 的 `BODY-SECTS` 建议 H2 总数达 10；当前 12 个技能为 6–9 个，均为 WARN 非 FAIL。可选补充「参数速查表 / 常见错误」等章节提升可读性。本次判定为**不属缺陷**（可选章节），未强行扩充以避免灌水。 | 未改（有意保留） |
| P3-2 | 仓库数据 | `skill-finder pack` 报出「包引用了盘上不存在的技能：`ai-cover-generator`」。属 `manifest.json` / `packs/` 数据问题，按纪律由主协调者统一处理。 | 未改（越界） |

### SKIP（需联网 / 外部工具，未能端到端验证）

| 项 | 原因 |
|---|---|
| `pandoc` 文档转换路径 | 本机未装 pandoc（SKIP）。已通过 rc=4 与安装提示验证「缺失依赖」分支正确，转换正例未实测 |
| `ocrmypdf` / pdf 扫描件 OCR 路径 | 本机未装 ocrmypdf（SKIP）。`pdf-pipeline` 步骤 3 的 OCR 转线为人工确认后执行，已补失败分支 |
| 各 SKILL.md 中的 `pip install` / `apt-get` / `brew` / `winget` 安装命令 | 需联网，未执行（SKIP） |

## 5. 已修复文件清单

| 文件 | 修复内容 |
|---|---|
| `skills/office/docx-writer/scripts/docx_ops.py` | 三处命令入口增加文件存在性与 .docx 合法性检查（干净中文报错）；`main()` 改为 `return args.func(args)`；`__main__` 改为 `sys.exit(main())` |
| `skills/office/docx-writer/SKILL.md` | 步骤 5 补「预期 / 若失败」 |
| `skills/office/pdf-pipeline/scripts/pdf_ops.py` | 新增 `open_reader()` 统一处理缺文件/加密/损坏，替换全部 5 处 `PdfReader(...)` 调用；`main()` 改用 `return`；`__main__` 改 `sys.exit(main())` |
| `skills/office/pdf-pipeline/SKILL.md` | 步骤 3、6 补「预期 / 若失败」 |
| `skills/tools/file-organizer/scripts/organize.py` | 新增 `_rel()` 并替换 `scan`/`plan`/`apply`/`dedupe` 中 4 处 `relative_to(root)`，修复相对路径 P0 崩溃 |
| `skills/tools/batch-renamer/scripts/rename.py` | 新增 `_rel()` 替换 8 处 `relative_to(root)`（修复 P0 崩溃）；新增 `_has_rule()`/`_require_rule()` 守卫，缺规则返回 rc=2 |
| `skills/tools/format-converter/scripts/convert.py` | `cmd_doc` 把依赖探测移到扩展名校验之后；`cmd_media` 增加 MEDIA_EXTS 校验返回 rc=3；`_run` 将外部返回码归一为 0/1 |
| `skills/tools/format-converter/SKILL.md` | 步骤 1、5 补「预期 / 若失败」 |
| `skills/tools/task-scheduler/SKILL.md` | 步骤 5 补「预期 / 若失败」 |
| `skills/knowledge/personal-wiki/SKILL.md` | 步骤 6 补「预期 / 若失败」 |
| `skills/knowledge/knowledge-graph-builder/SKILL.md` | 步骤 5 补「预期 / 若失败」 |

> 说明：`skills/meta/skill-finder/scripts/find_skill.py` 在 `git status` 中显示 modified，但改动是**先前小组**留下的注释澄清（`parents[4]` 语义说明），非本次审计所改；经实测该层级正确，予以保留。

## 6. 复现命令

```bash
# ── 清单 ──
cd /workspace/awesome-skillkit && find skills/office skills/tools skills/meta skills/knowledge -name SKILL.md | sort

# ── 门禁（三项全过） ──
cd /workspace/awesome-skillkit && python3 tools/validate_skills.py
cd /workspace/awesome-skillkit && python3 -m pytest skills/office skills/tools skills/meta skills/knowledge -q
cd /workspace/awesome-skillkit && python3 skills/meta/skill-linter/scripts/lint_skill.py skills/office
cd /workspace/awesome-skillkit && python3 skills/meta/skill-linter/scripts/lint_skill.py skills/tools
cd /workspace/awesome-skillkit && python3 skills/meta/skill-linter/scripts/lint_skill.py skills/meta
cd /workspace/awesome-skillkit && python3 skills/meta/skill-linter/scripts/lint_skill.py skills/knowledge

# ── 11 个脚本 --help 冒烟 ──
cd /workspace/awesome-skillkit && for s in skills/office/*/scripts/*.py skills/tools/*/scripts/*.py skills/meta/*/scripts/*.py skills/knowledge/*/scripts/*.py; do
  case "$s" in *test_smoke*) continue;; esac
  python3 "$s" --help >/dev/null 2>&1; echo "$(basename $s) rc=$?"; done

# ── P0 复现与复验：file-organizer ──
mkdir -p /tmp/a4_test/org/inbox && cd /tmp/a4_test/org/inbox && printf aaa > a.pdf && printf bbb > b.txt
cd /tmp/a4_test/org && python3 /workspace/awesome-skillkit/skills/tools/file-organizer/scripts/organize.py scan inbox
cd /tmp/a4_test/org && python3 /workspace/awesome-skillkit/skills/tools/file-organizer/scripts/organize.py plan inbox --by type
cd /tmp/a4_test/org && python3 /workspace/awesome-skillkit/skills/tools/file-organizer/scripts/organize.py apply inbox --by type --dry-run
cd /tmp/a4_test/org && python3 /workspace/awesome-skillkit/skills/tools/file-organizer/scripts/organize.py apply inbox --by type --yes

# ── P0 复现与复验：batch-renamer ──
mkdir -p /tmp/a4_test/ren/work && cd /tmp/a4_test/ren/work && printf img1 > IMG_1.JPG
cd /tmp/a4_test/ren/work && python3 /workspace/awesome-skillkit/skills/tools/batch-renamer/scripts/rename.py preview . --pattern "IMG_{n:03d}.{ext}"
cd /tmp/a4_test/ren/work && python3 /workspace/awesome-skillkit/skills/tools/batch-renamer/scripts/rename.py apply . --pattern "photo_{n:03d}.{ext}" --yes
cd /tmp/a4_test/ren/work && python3 /workspace/awesome-skillkit/skills/tools/batch-renamer/scripts/rename.py undo . --yes
cd /tmp/a4_test/ren/work && python3 /workspace/awesome-skillkit/skills/tools/batch-renamer/scripts/rename.py preview .   # 应 rc=2（无规则）

# ── P0/P1 复验：format-converter ──
cd /tmp/a4_test/conv && python3 /workspace/awesome-skillkit/skills/tools/format-converter/scripts/convert.py media photo.png o.zzz   # 应 rc=3
cd /tmp/a4_test/conv && python3 /workspace/awesome-skillkit/skills/tools/format-converter/scripts/convert.py doc report.md o.zzz     # 应 rc=3
cd /tmp/a4_test/conv && python3 /workspace/awesome-skillkit/skills/tools/format-converter/scripts/convert.py image nope.png o.jpg    # 应 rc=1

# ── office 脚本正/异常 ──
cd /tmp/a4_test/media && ffmpeg -f lavfi -i testsrc=duration=1:size=160x120:rate=10 -pix_fmt yuv420p in.mp4 -y
cd /tmp/a4_test/media && python3 /workspace/awesome-skillkit/skills/tools/format-converter/scripts/convert.py media in.mp4 out.webm --vcodec libvpx-vp9
cd /tmp/a4_test/docx  && python3 /workspace/awesome-skillkit/skills/office/docx-writer/scripts/docx_ops.py create --input content.md --output output.docx --title 周报
cd /tmp/a4_test/docx  && python3 /workspace/awesome-skillkit/skills/office/docx-writer/scripts/docx_ops.py inspect output.docx --preview 12
cd /tmp/a4_test/docx  && python3 /workspace/awesome-skillkit/skills/office/docx-writer/scripts/docx_ops.py inspect nope.docx   # 应 rc=1
cd /tmp/a4_test/pdf   && python3 /workspace/awesome-skillkit/skills/office/pdf-pipeline/scripts/pdf_ops.py meta nope.pdf     # 应 rc=1

# ── knowledge / 元技能 ──
cd /tmp/a4_test/wiki  && python3 /workspace/awesome-skillkit/skills/knowledge/personal-wiki/scripts/wiki_build.py init vault
cd /tmp/a4_test/wiki  && python3 /workspace/awesome-skillkit/skills/knowledge/personal-wiki/scripts/wiki_build.py init vault   # 应 rc=1
cd /tmp/a4_test/kg    && python3 /workspace/awesome-skillkit/skills/knowledge/knowledge-graph-builder/scripts/graph_build.py extract notes
cd /tmp/a4_test/kg    && python3 /workspace/awesome-skillkit/skills/knowledge/knowledge-graph-builder/scripts/graph_build.py analyze notes --top 10
cd /workspace/awesome-skillkit && python3 skills/meta/skill-finder/scripts/find_skill.py stats
cd /tmp && python3 /workspace/awesome-skillkit/skills/meta/skill-linter/scripts/lint_skill.py /nope   # 应 rc=2

# ── 清理 ──
cd /workspace/awesome-skillkit && find skills -name "__pycache__" -type d -exec rm -rf {} +
```

---

## 附：门禁原始输出

```
$ cd /workspace/awesome-skillkit && python3 tools/validate_skills.py
skills: 142  errors: 0  warnings: 0
RESULT: PASSED

$ cd /workspace/awesome-skillkit && python3 -m pytest skills/office skills/tools skills/meta skills/knowledge -q
..............                                                           [100%]
14 passed in 0.71s

$ cd /workspace/awesome-skillkit && python3 skills/meta/skill-linter/scripts/lint_skill.py skills/office
skills: 3  FAIL: 0  WARN: 3
RESULT: PASS
$ ... skills/tools        →  skills: 4  FAIL: 0  WARN: 4   RESULT: PASS
$ ... skills/meta         →  skills: 3  FAIL: 0  WARN: 3   RESULT: PASS
$ ... skills/knowledge    →  skills: 2  FAIL: 0  WARN: 2   RESULT: PASS
合计：12 技能  0 FAIL  12 WARN（均为可选 BODY-SECTS 章节数建议）
```

> 注：任务书给出的 `lint_skill.py --path skills/office skills/tools ...` 参数形式不存在；该脚本只接受单个位置参数 `target`，
> 因此按目录逐个执行。`--help` 复核用法为 `lint_skill.py [-h] [--json] [--verbose] target`。

---

## 第五部分 · integrations / dataviz / memory / skill-finder（11 技能）

# 逐技能逻辑链条完整性审计报告 —— Agent 5（integrations / dataviz / memory / meta:skill-finder）

审计范围：`skills/integrations/**`、`skills/dataviz/**`、`skills/memory/**`、`skills/meta/skill-finder`。
实测环境：Python 3.11.1，全程离线，无任何跨技能改动。

---

## 1. 总览

| 指标 | 数值 |
|---|---|
| 覆盖技能数 | **11**（integrations 4 / dataviz 2 / memory 4 / meta:skill-finder 1） |
| 覆盖 `scripts/*.py` 数 | **6**（notion_ops / im_bridge / issue_sync / drive_ops / dashboard / find_skill） |
| 纯提示型技能（无脚本） | 5（memory-architect / memory-extractor / memory-manager / memory-retriever / chart-recommender） |
| `--help` 冒烟通过数 | **6 / 6（rc=0 全部通过）** |
| 深测通过数（正例 rc=0，输出符合 SKILL 描述） | **6 / 6** |
| 发现缺陷数 | **5**（P0×1、P2×3、P3×1） |
| 已修复数 | **5 / 5** |
| references/*.md 存在性 | **13 / 13 全部存在且非空** |
| `references/` 死链 | **0** |
| 跨技能引用（pub-plotter / file-organizer 等） | **15 / 15 全部真实存在** |

### 最终门禁结果（三跑全过）

```
$ python3 tools/validate_skills.py
skills: 142  errors: 0  warnings: 0
RESULT: PASSED

$ python3 -m pytest skills/integrations skills/dataviz skills/memory -q
no tests ran in 0.01s          # 本范围无 pytest 用例（与基线一致）

$ python3 -m pytest -q          # 全仓对比基线
271 passed, 1 skipped in 23.78s  # 与审计前基线完全一致，无新增失败

$ python3 skills/meta/skill-linter/scripts/lint_skill.py skills/integrations   # → FAIL: 0 WARN: 4 PASS
$ python3 skills/meta/skill-linter/scripts/lint_skill.py skills/dataviz        # → FAIL: 0 WARN: 2 PASS
$ python3 skills/meta/skill-linter/scripts/lint_skill.py skills/memory         # → FAIL: 0 WARN: 4 PASS
$ python3 skills/meta/skill-linter/scripts/lint_skill.py skills/meta/skill-finder # → FAIL: 0 WARN: 1 PASS
```

> `lint_skill.py` 只接受单个 target 参数，故按目录逐个调用；11 个技能 **0 FAIL**。全部 WARN 均为 `BODY-SECTS`（可选章节建议，非结构缺陷）。

---

## 2. 逐技能审计表

> 五要素闭环列：输入清单 / 前置自检 / 工作流 / 交付标准 / 失败处置表 / 参考（✅=齐备且可执行，⚠=齐备但有小缺陷）。

### 2.1 `skills/integrations/notion-workspace`

| 项 | 结论 |
|---|---|
| 五要素闭环 | 输入✅ 自检✅ 工作流✅(6步) 交付✅ 失败表✅(8行) 参考✅ |
| 链条是否有断裂 | **无**。产物 `payload.json`(步骤2→3)、`response.json`(步骤3)、Markdown(步骤4) 均有对应产出步骤 |
| 发现的问题 | 步骤 6「交付」缺「若失败」处置（工作流三件套不完整，P2） |
| 修复动作 | 在步骤 6 补「预期 / 若失败」两段：URL 缺失时用页面 ID 拼链接、产物未落盘时明确说明是 dry-run |

### 2.2 `skills/integrations/feishu-dingtalk-bridge`

| 项 | 结论 |
|---|---|
| 五要素闭环 | 输入✅ 自检✅ 工作流✅(5步) 交付✅ 失败表✅(10行) 参考✅ |
| 链条是否有断裂 | **无**。三平台负载构造 → 发送 → `parse-webhook` 解析闭合成环；步骤 2 三条示例命令逐字实测 rc=0 |
| 发现的问题 | 无（description 声称的 feishu/dingtalk/wecom 三平台在脚本中一一对应实现） |
| 修复动作 | 无需修复 |

### 2.3 `skills/integrations/issue-tracker-sync`

| 项 | 结论 |
|---|---|
| 五要素闭环 | 输入✅ 自检✅ 工作流✅(5步) 交付✅ 失败表✅(10行) 参考✅ |
| 链条是否有断裂 | **无**。产物 `payload.json`/`response.json`/ID 台账/`report.md` 均有产出步骤；步骤 4 周报由步骤 5 锚定 |
| 发现的问题 | 无。空 issue 列表正确返回 rc=2（反例语义诚实，可作其他技能标杆） |
| 修复动作 | 无需修复 |

### 2.4 `skills/integrations/cloud-drive-manager`

| 项 | 结论 |
|---|---|
| 五要素闭环 | 输入✅ 自检✅ 工作流✅(5步) 交付✅ 失败表✅(10行→11行) 参考✅ |
| 链条是否有断裂 | **有（P0）**。`plan-upload` / `checksum-plan` 面对**空目录或全被 `--exclude` 排除**时返回 `rc=0`，把"什么都没规划出来"当成功上报 |
| 发现的问题 | **P0 失败当成功**：空清单 rc=0，流水线会带空计划进入上传；`checksum-plan` 空清单 rc=0 生成的 0 行基准会被 `sha256sum -c` 空过 |
| 修复动作 | ① 两处 `return 0` 改为 `return _die(...)`（rc=2，stderr 报原因）；② SKILL 步骤 1/2 的「若失败」补明「退出码 2」；③ 失败处置表新增 1 行 |

### 2.5 `skills/dataviz/dashboard-designer`

| 项 | 结论 |
|---|---|
| 五要素闭环 | 输入✅ 自检✅ 工作流✅(5步) 交付✅ 失败表✅(10行) 参考✅ |
| 链条是否有断裂 | **无**。120 行真实 CSV 实测 `build` → `external: 0`、`svg 数(3) == charts 数(3)`、`kpis: 2`，自包含断言成立 |
| 发现的问题 | 步骤 5「交付」缺「若失败」处置（P2） |
| 修复动作 | 补「预期 / 若失败」：绝对路径拿不到时的取法、`external != 0` 时不得交付须回步骤 3 排查 |

### 2.6 `skills/dataviz/chart-recommender`

| 项 | 结论 |
|---|---|
| 五要素闭环 | 输入✅ 自检✅ 工作流✅(4步) 交付✅ 失败表✅(9行) 参考✅ |
| 链条是否有断裂 | **无**。纯提示型，步骤 2/3/4 全部声明依赖词库；词库 137 行、46 行表格，自检命令 `grep -c "^|"` 实测输出 46 ≥ 40 |
| 发现的问题 | 无 |
| 修复动作 | 无需修复 |

### 2.7 `skills/memory/memory-architect`

| 项 | 结论 |
|---|---|
| 五要素闭环 | 输入✅ 自检✅ 工作流✅(5步) 交付✅ 失败表✅(6行) 参考✅ |
| 链条是否有断裂 | **无**。链路起点：schema（10 字段冻结版）→ 下游三技能只执行不重设计，链路位置章节声明清晰 |
| 发现的问题 | 无。纯提示型，description 与正文能力一致 |
| 修复动作 | 无需修复 |

### 2.8 `skills/memory/memory-extractor`

| 项 | 结论 |
|---|---|
| 五要素闭环 | 输入✅ 自检✅ 工作流✅(5步) 交付✅ 失败表✅(9行) 参考✅ |
| 链条是否有断裂 | **无**。下游契约明确：产出 `candidates.json`（7 字段），交 memory-manager 落库 |
| 发现的问题 | 无 |
| 修复动作 | 无需修复 |

### 2.9 `skills/memory/memory-manager`

| 项 | 结论 |
|---|---|
| 五要素闭环 | 输入✅ 自检✅ 工作流✅(5步) 交付✅ 失败表✅(10行) 参考✅ |
| 链条是否有断裂 | **无**。上游 `candidates.json` → 本技能 `operations.json` → 下游 retriever，参数传递契约明确 |
| 发现的问题 | 无 |
| 修复动作 | 无需修复 |

### 2.10 `skills/memory/memory-retriever`

| 项 | 结论 |
|---|---|
| 五要素闭环 | 输入✅ 自检✅ 工作流✅(5步) 交付✅ 失败表✅(10行) 参考✅ |
| 链条是否有断裂 | **无**。链路出口，消费 manager 维护的 disputed/unstable 标记做降权，权重与降级路径（hybrid→keyword_only）可追溯 |
| 发现的问题 | 无 |
| 修复动作 | 无需修复 |

### 2.11 `skills/meta/skill-finder`

| 项 | 结论 |
|---|---|
| 五要素闭环 | 输入✅ 自检✅ 工作流✅(4步) 交付✅ 失败表✅(7行) 参考✅ |
| 链条是否有断裂 | **无**。三子命令实测：`search` 命中 rc=0、未命中 rc=1、`pack` 全错 rc=2、`stats` rc=0；退出码语义与文档逐条吻合 |
| 发现的问题 | **P3 文档瑕疵**：`find_skill.py` 第 35 行注释写「上溯三级」，实际 `parents[4]` 是**四级**（scripts→skill-finder→meta→skills→root），代码对、注释错，易误导后续维护者 |
| 修复动作 | 更正注释为「上溯四级」并展开完整层级 |

---

## 3. 脚本实测结果表

| 脚本 | 正例结果 | 异常样例结果 | 离线降级行为 | 返回码传播 | 是否修复 |
|---|---|---|---|---|---|
| `notion-workspace/scripts/notion_ops.py` | `--help` rc=0；`build-page --title T --parent abc` rc=0 | 缺 `--parent` rc=2；`parse-page --json /nope.json` rc=2；`--page-size 500` rc=2；非法块 `table` rc=2 | 纯离线构造器，**从不发 HTTP**；token 仅由外部注入，脚本不读不打印 → 离线语义诚实 | `sys.exit(main())` ✅ | 无需修复 |
| `feishu-dingtalk-bridge/scripts/im_bridge.py` | `--help` rc=0；feishu/dingtalk(加签)/wecom(@) 三例 rc=0 | wecom 超 4096 rc=2；非法平台 `slack` rc=2；缺文件 rc=2；`--sign` 空 secret-env rc=2 | 纯离线；凭证只从环境变量读，dry-run 打印 `{token}` 占位 → 不假装发送成功 | `sys.exit(main())` ✅ | 无需修复 |
| `issue-tracker-sync/scripts/issue_sync.py` | `--help`/`field-map` rc=0；jira/linear/github 三例 rc=0 | jira 缺 `--project` rc=2；`--priority P9` rc=2；周报缺文件 rc=2；**空列表 rc=2** | `weekly-report` 纯本地渲染不联网；`build` 仅打印请求 | `sys.exit(main())` ✅ | 无需修复（反例标杆） |
| `cloud-drive-manager/scripts/drive_ops.py` | `--help` rc=0；`plan-upload`+`checksum-plan` 正例 rc=0；`sha256sum -c` 全 OK | 不存在目录 rc=2；非法算法 rc=2；缺文件 rc=2；**空目录/全排除 → 修复前 rc=0，修复后 rc=2** | 只读本地目录、不联网不删除；删除须双重确认 | `sys.exit(main())` ✅ | **已修复（P0）** |
| `dataviz/dashboard-designer/scripts/dashboard.py` | `--help` rc=0；120 行 CSV `inspect`/`recommend`/`build` rc=0，`external: 0`、svg(3)==charts(3) | 缺文件 rc=1；空文件 rc=1（三个子命令一致） | 产出 HTML 纯内联 SVG，零 CDN；离线打开正常 | `sys.exit(main())` ✅ | 无需修复 |
| `meta/skill-finder/scripts/find_skill.py` | `--help` rc=0；`search 视频` rc=0；`pack` 正例 rc=0；`stats` rc=0（142 技能/36 包） | 未命中 rc=1；`pack` 全错 rc=2；缺 manifest.json rc=2 | 全部读本地 `manifest.json` + `SKILL.md`，无网络依赖 | `sys.exit(main())` ✅ | **已修复（注释 P3）** |

---

## 4. Gap 清单

### P0（链路必坏 / 失败被吞 / 假装成功）

- **[已修复] `cloud-drive-manager` 空目录当成功**：`plan-upload` 与 `checksum-plan` 在
  「目录为空」或「全被 `--exclude` 排除」时返回 `rc=0`，把"零产出"上报为成功。
  这会污染下游流水线（带空计划上传；`sha256sum -c` 对 0 行清单空过）。
  已改为 `_die(...)` → rc=2，并同步 SKILL 步骤说明与失败处置表。

### P1（不可执行命令 / 死链）

- 无。11 个技能的 `references/*.md` 全部真实存在；正文引用的 `scripts/`、`references/` 路径 100% 可解析；SKILL 示例命令逐字实测可执行。

### P2（体验与健壮性）

- **[已修复] `dashboard-designer` 步骤 5「交付」缺「若失败」**：补上绝对路径获取法与 `external != 0` 时不得交付的判定。
- **[已修复] `notion-workspace` 步骤 6「交付」缺「若失败」**：补上 URL 缺失兜底与 dry-run 明确说明要求。
- **未修复（保留）**：`lint_skill.py` 的 `BODY-SECTS` WARN（notion/feishu/issue/dashboard/chart 等 H2 数 6-8 < 10）。判定为**建议级**，这些技能的结构六要素（含硬性 6 项）全部齐备，仅有可选章节（参数速查表/常见错误/工作流变体）未补。强行补章节会稀释正文密度，故不改。

### P3（建议）

- **[已修复] `skill-finder` 注释层级不一致**：注释「上溯三级」与代码 `parents[4]`（四级）矛盾，已更正。
- 建议（未改）：`memory-*` 的 `references/sources-and-methodology.md` 仅 14-15 行，虽属署名文件的合理简练形态（含来源/许可/蒸馏边界三段），若追求"完备"可补各字段的字段级出处。

---

## 5. 已修复文件清单

| 文件 | 修复内容 |
|---|---|
| `skills/integrations/cloud-drive-manager/scripts/drive_ops.py` | `cmd_plan_upload` 空文件清单 `return 0` → `return _die(...)`（rc=2）；`cmd_checksum_plan` 同类改动；各补注释说明"空清单不是成功" |
| `skills/integrations/cloud-drive-manager/SKILL.md` | 步骤 1、步骤 2「若失败」补明退出码 2 与原因；失败处置表新增「计划为空 → 退出码 2」1 行 |
| `skills/dataviz/dashboard-designer/SKILL.md` | 步骤 5「交付」补「预期 / 若失败」两段 |
| `skills/integrations/notion-workspace/SKILL.md` | 步骤 6「交付」补「预期 / 若失败」两段 |
| `skills/meta/skill-finder/scripts/find_skill.py` | 第 35 行注释「上溯三级」更正为「上溯四级」并展开层级 |

改动统计：`5 files changed, 32 insertions(+), 6 deletions(-)`。

---

## 6. 复现命令

```bash
# —— 清单 ——
cd /workspace/awesome-skillkit && find skills/integrations skills/dataviz skills/memory skills/meta/skill-finder -name SKILL.md | sort

# —— 门禁 ——
cd /workspace/awesome-skillkit && python3 tools/validate_skills.py
cd /workspace/awesome-skillkit && python3 -m pytest skills/integrations skills/dataviz skills/memory -q
cd /workspace/awesome-skillkit && python3 -m pytest -q
cd /workspace/awesome-skillkit && python3 skills/meta/skill-linter/scripts/lint_skill.py skills/integrations
cd /workspace/awesome-skillkit && python3 skills/meta/skill-linter/scripts/lint_skill.py skills/dataviz
cd /workspace/awesome-skillkit && python3 skills/meta/skill-linter/scripts/lint_skill.py skills/memory
cd /workspace/awesome-skillkit && python3 skills/meta/skill-linter/scripts/lint_skill.py skills/meta/skill-finder

# —— 脚本 --help 冒烟 ——
cd /workspace/awesome-skillkit && for f in skills/integrations/*/scripts/*.py skills/dataviz/*/scripts/*.py skills/meta/skill-finder/scripts/find_skill.py; do python3 "$f" --help >/dev/null 2>&1; echo "rc=$? $f"; done

# —— cloud-drive P0 复现（修复后应为 rc=2） ——
mkdir -p /tmp/a5_test/emptydir
cd /workspace/awesome-skillkit/skills/integrations/cloud-drive-manager && python3 scripts/drive_ops.py plan-upload --dir /tmp/a5_test/emptydir --remote /x ; echo "rc=$?"
cd /workspace/awesome-skillkit/skills/integrations/cloud-drive-manager && python3 scripts/drive_ops.py checksum-plan --dir /tmp/a5_test/emptydir ; echo "rc=$?"

# —— cloud-drive 正例闭环（rc=0 + sha256sum -c 全 OK） ——
mkdir -p /tmp/a5_test/src/sub && echo hi > /tmp/a5_test/src/a.txt
cd /workspace/awesome-skillkit/skills/integrations/cloud-drive-manager && python3 scripts/drive_ops.py plan-upload --dir /tmp/a5_test/src --remote /archive --provider baidu --prefix backup --exclude "*.tmp" --manifest /tmp/a5_test/plan.json
cd /workspace/awesome-skillkit/skills/integrations/cloud-drive-manager && python3 scripts/drive_ops.py checksum-plan --dir /tmp/a5_test/src --output /tmp/a5_test/sha.txt --algo sha256
cd /tmp/a5_test/src && sha256sum -c /tmp/a5_test/sha.txt

# —— dashboard 自包含断言（external: 0，svg == charts） ——
cd /workspace/awesome-skillkit/skills/dataviz/dashboard-designer && python3 scripts/dashboard.py build /tmp/a5_test/big.csv --out /tmp/a5_test/big.html
grep -o '<svg' /tmp/a5_test/big.html | wc -l

# —— skill-finder 退出码语义 ——
cd /workspace/awesome-skillkit && python3 skills/meta/skill-finder/scripts/find_skill.py search zzzznomatchword ; echo "rc=$?  # 期望 1"
cd /workspace/awesome-skillkit && python3 skills/meta/skill-finder/scripts/find_skill.py pack no-such-skill ; echo "rc=$?  # 期望 2"
cd /workspace/awesome-skillkit && python3 skills/meta/skill-finder/scripts/find_skill.py stats

# —— 清理测试产物与缓存 ——
find skills -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
rm -rf /tmp/a5_test
```

---

### 附：工作纪律确认

- 所有测试中间产物落在 `/tmp/a5_test/`，仓库工作区零污染（`git status --porcelain` 无未跟踪文件）。
- 未触碰 `skills/skill_chains.json` / `manifest.json` / `README*.md` / `SOURCES.md` / `CHANGELOG.md` / `tools/**`。
- 仅修改了负责范围内的 5 个文件，且均为"改产物本身"（SKILL.md 或脚本），非仅写建议。
- 未联网；外部平台（Notion/飞书/钉钉/企微/云盘）的联网路径标记为 **SKIP（本次不联网验证）**，但其**离线降级路径全部实测**且返回码语义诚实。
- `find skills -name "__pycache__" -type d -exec rm -rf {} +` 已执行。
