# 全量测试报告 / Full-Suite Test Report

> 日期：2026-09-15 ｜ 范围：全部 9 域（时值）27 场景包 100+ 技能
> 方法：三层测试——L1 静态一致性校验、L2 编排器端到端 dry-run、L3 脚本门禁深测（正例+异常双向）
> 纪律：全程零联网、测试产物只写 /tmp；共享文件（chains/manifest/README/SOURCES/CHANGELOG）统一由主控合并

---

## 1. 结论速览

| 指标 | 测试前 | 测试后 |
|------|--------|--------|
| chains 域 / 链条 / 注册技能 | 9 / 21 / 47 | **12 / 39 / 111** |
| 游离技能（在盘上但不在任何链条域） | **53** | **1**（self-eval 元技能，有意留外） |
| 有 SKILL.md 的技能 | 99 | **111**（补齐 paper 12 个） |
| pytest | 257 passed | **257 passed**（无回归） |
| 门禁 validate_skills | 0 err / 0 warn | **0 err / 0 warn** |
| 编排器 dry-run（19 情景） | 全绿 | **全绿**（含新 type 分流与 manual 语义） |
| 已修复缺陷 | — | **27 项**（P0×4 / P1×8 / P2×15） |

---

## 2. L1 静态一致性（chains.json）

- 9→12 域全部 entry 文件存在；21→39 条链无孤儿引用、无重复登记。
- 覆盖缺口扫描发现 **53 个游离技能**（已打包、可运行，但不在任何链条域）：
  编程专家技能 33、发布平台技能 11、video 上游规划 4、chat 1、scenarios 3、paper 1（其余 12 个 paper 技能连 SKILL.md 都没有）。
- 附带发现：12 个 paper 脚本技能**不在任何 pack**——用户下载 zip 根本拿不到。

## 3. L2 编排器端到端（9 编排器 × 19 真实情景）

全部 `--dry-run --json` 通过，但对照 chains 声明发现三处"编排器实现 ≠ 链条声明"：

| 域 | 发现 | 处置 |
|----|------|------|
| video | 编排器硬编码 talking_character 6 步，meme/tutorial 链跑错步骤；真实模式文件交接断裂（tts 写 CWD、lipsync 输出 `lipsync_scene_*.mp4` ≠ editor 期望 `scene_*.mp4`），被 mock 掩盖 | **P0/P1 已修**：按 `--type` 选链分流；`voice_synth` batch 加 `--audio-dir`；`lip_sync` batch 输出对齐 `scene_<id>.mp4` 契约；SKILLKIT_MOCK=1 真跑 6/6 闭环（scene_*.wav 落位 out_dir） |
| writing | news_flash 编排 5 步 vs 链声明 3 步（多 outline+publish）；content-editor 产物只打印 stdout，seo 读编辑前草稿 | **P1 已修**：chains news_flash 补齐 outline+`cross-post-orchestrator?`；editor `--output edited.json` 落盘、seo 读编辑后稿，真跑验证 `edited.json` 产出 |
| ppt | 编排器调用 outline/visual/assets/rehearsal/render 5 个**不存在**的脚本；唯一存在的 make_pptx.py 从未被调 | **P1 已修**：重构为"spec 骨架生成 → LLM 填充提示（manual）→ 真调 make_pptx 渲染"，真跑产出 31 KB final.pptx |
| design | 编排器接受 thumbnail/banner 但无对应链 | chains 补 thumbnail/banner 两链（复用 3 技能，审计脚本支持任意比例） |
| programming | 无 --dry-run、硬编码 `python`、tdd-guide 纯占位且 sys.path 少一层、full_project 9 步仅实现 3 步、CWD 落盘垃圾 | **已修**：sys.executable ×3、--dry-run、rc 传播、去 CWD 落盘、tdd 路径修正；5 步 runner 缺失量化入档（P3 立项建议） |

## 4. L3 脚本门禁深测（139 脚本 / 约 90 用例）

### programming（96 脚本冒烟全过，14 必测脚本深测）

| 缺陷 | 级别 | 修复 |
|------|------|------|
| math `model_solver` LP 路径 `result.iter`（scipy 无此属性）→ **100% 必崩** | **P0** | → `result.nit` + 异常分支 rc=1 |
| `data_ml_pipeline` SCRIPTS 指向 `ml/pipeline/`（实为 `ml/ml-pipeline/`）→ **ml 链第 3 步必断** | **P0** | 路径修正，fake.csv 三步 complete |
| code-intent-planner L2 失败仍 rc=0（失败当成功） | P1 | `sys.exit(1)` |
| visualizer 数据缺失 skipped 却 rc=0 | P1 | rc=1 |
| math 四件套 `__main__` 裸 main() 不传播 | P1 | `sys.exit(main())` ×4 |
| dep_scanner CVE 重复计数（name 大小写双扫） | P2 | 去重 6→3 |
| ship_gate 未知 `--category` 静默 rc=0 | P2 | rc=2 + 合法列表 |
| tdd test_generator 字符串 criteria 崩溃 | P2 | 兼容 |

### video / writing / chat / scenarios（30 脚本：13 双向深测 + 17 publisher offline 扫描）

全部通过或按设计语义放行；scene_lint / prompt_audit / script_lint 类严格门禁对缺字段、
超长行、舞台提示等异常输入全部正确拦截。真实联网/ffmpeg 路径 SKIP 未触发。

### design / audio / marketing / education / ppt / paper（13 启发式脚本）

12 个完全通过；1 个弱门禁（topic_selector 空主题不拦，P2 已加非法 JSON 拦截）。

| 缺陷 | 级别 | 修复 |
|------|------|------|
| **paper 13 脚本 `main()` 返回码被 `__main__` 丢弃 → 进程恒 rc=0，编排器把失败当成功，门禁在编排层被静默绕过** | **P0** | 13 处 `sys.exit(main())` |
| latex-formatter / self-reviewer / tex-cleaner 缺文件 rc=0 | P2 | rc=1 |
| figure_maker `--type heatmap` 未实现却强制标 success | P2 | 诚实返回 unsupported |
| exercise_lint 无题块输入 TypeError 崩溃 | P2 | 返回 dict，rc=2 |

### 链条"一个动作立刻展开"核查

design / audio / marketing / education 四域 SKILL.md 的移交话术核查通过；为 26 个
游离/上游技能 SKILL.md 补齐"继续调用 X——链条自动展开"话术（validate 0 警）。

## 5. 链条大扩展（查缺补漏的落地）

```
9 域 21 链 47 注册  ──►  12 域 39 链 111 注册
```

- **新增 chat 域**（prompt_audit 链）、**office 域**（document_pipeline 链）、
  **paper 域**（full_paper / quick_draft / polish_only / submit_ready 四链）
- programming 补登 32 技能 + 9 条专家链：security_fix / debug_hotfix / data_ml /
  math_modeling / api_design / infra_delivery / db_change / sre_readiness / release_audit
- video 补 pre_production 上游规划链（visual-style-anchor → storyboard → shot-recipe? → prompt-engineer → script-writer）
- writing 登记全部 11 个发布平台技能；news_flash 补齐
- design 补 thumbnail / banner 链
- 12 个 paper 技能补齐合规 SKILL.md，收编进 `ai-research-writing` 包（7→19 技能）

## 6. 残留建议（P3，未动）

1. tdd-guide 8 个脚本均为无 CLI 库模块——建议补统一入口或 SKILL.md 明示"仅库引用"。
2. programming full_project 缺失的 5 步 runner（reviewer/dep-audit/ci-cd/ship-gate/runbook）——仿 run_code_generator 模式单独立项。
3. lit-review / experiment-runner 的 mock 数据须显式标注（SKILL.md 已写诚实声明，接入真实 API 是后续项）。
4. dep_scanner 对非法清单静默按 0 依赖——建议 parse_errors 进报告。
5. 编排器 `--mode research` 会真实联网——建议 `--offline` 熔断。
6. database-designer 与 sql-database-assistant 各有一份 migration_generator.py，建议比对合并或划清边界。

## 7. 复现

```bash
python3 -m pytest skills -q              # 257 passed, 1 skipped
python3 tools/validate_skills.py         # 111 skills, 0 errors, 0 warnings
python3 build.py                         # 28 archives, _all bundle 112 skills
# 编排器抽样（SKILLKIT_MOCK=1 真跑 / --dry-run 规划）见 docs 各域 SKILL.md
```
