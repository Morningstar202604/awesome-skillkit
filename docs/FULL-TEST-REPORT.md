# 全量测试报告 / Full-Suite Test Report

> 日期：2026-09-15 ｜ 范围：全部 9 域（时值）27 场景包 100+ 技能
> 方法：三层测试——L1 静态一致性校验、L2 编排器端到端 dry-run、L3 脚本门禁深测（正例+异常双向）
> 纪律：全程零联网、测试产物只写 /tmp；共享文件（chains/manifest/README/SOURCES/CHANGELOG）统一由主控合并
>
> **⚠️ 历史快照**：本报告记录 2026-09-15 时值（9→12 域、21→39 链、28 archives、112 skill、27 包）的测试状态，
> 数字对应该测试版本，非当前 v0.19.0 状态（当前：18 域 / 58 链 / 143 skill / 36 包，见 `site/data/site.json`）。

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

## 6. 残留建议（P3，2026-09-15 已全部清零）

1. ~~tdd-guide 8 个脚本均为无 CLI 库模块~~ **已修**：新增统一入口
   `scripts/tdd_cli.py`（workflow / detect / gen-tests / fixtures / coverage /
   metrics / stub 七个子命令覆盖全部 8 模块，rc: 0/2/1），SKILL.md 同步给出
   CLI 用法并纠正 `tdd_workflow.py --phase` 失效引用；8 正例 + 3 异常路径验证通过。
2. ~~programming full_project 缺失的 5 步 runner~~ **已修**：pipeline_orchestrator.py
   新增 `_run_step_script` 统一封装 + run_code_review / run_dependency_audit /
   run_ci_cd_setup / run_ship_gate / run_runbook_generation 五个 runner，
   `run_full_pipeline` 4 步 → 9 步（与 full_project 链定义对齐）；含失败步骤时
   进程退出码传播 rc!=0（ship-gate 拦截如实记 failed）。
3. ~~lit-review / experiment-runner 的 mock 数据须显式标注~~ **已修**：lit-review
   `--arxiv` 真调 arXiv API（HTTPS + 429 退避重试 + 20s 超时，Atom XML 解析经
   夹具验证），网络失败自动回退 mock 且输出顶层 `data_source` / `warning` 诚实标注；
   experiment-runner 输出顶层带 `mode: "simulated"` + `simulation_notice`。
   注：沙箱共享出口 IP 被 arXiv 限流（429）时按设计降级为带警告的 mock。
4. ~~dep_scanner 对非法清单静默按 0 依赖~~ **已修**：12 个 `_parse_*` 由吞异常
   改为 raise，`scan_project` 统一捕获记入 `parse_errors`（文件/解析器/错误详情），
   summary 计数 + 文本报告 PARSE ERRORS 行 + recommendations WARNING；JSON 报告
   自动携带。坏 package.json 夹具验证：错误上报且其余清单正常扫描。
5. ~~编排器 `--mode research` 会真实联网~~ **已修**：新增 `--offline` 熔断旗标，
   research 模式下不发起任何联网子进程，步骤如实标记 skipped 并输出说明。
6. ~~database-designer 与 sql-database-assistant 各有一份 migration_generator.py~~
   **已划界（不合并）**：二者非重复实现——database-designer 版做 schema JSON 对比
   迁移（ALTER + 回滚 + 零停机 expand-contract），sql-database-assistant 版做
   自然语言 → up/down 迁移模板。双方 SKILL.md 与 docstring 已加 Boundary 互指说明。

## 8. 场景级真实验收（2026-09-21，v0.20.0）

冒烟（121/121）只证明「能跑」；本节记录在此之上补的第二层验收——「在真实场景输入下，
产出过质量门」。工具链 4 件套：`tools/scenario_harness.py`（主驱动）、
`tools/scenario_overrides.py`（逐技能场景覆盖）、`tools/real_scenario_test.py`、
`tools/quality_audit.py`。

**双层设计**：
- 静态模式（无 API key 可跑）：120 个脚本型技能以真实场景输入执行，20 个技能脚本为此
  做了离线化修复（网络调用加 mock/降级，不再假死）；
- LLM 模式：34 个 prompt 型技能以 SKILL.md 为 system、场景为 user 真调模型，过四道
  质量门——长度 / 拒答 / 占位符 / 指定产物名；门禁失败自动重采一次（temperature 0.4
  有方差，门禁标准不变；实测温度 0 会使输出塌短，弃用）。

**终验**：scenario **154/154 pass** | smoke 121/121 | validate 0 错 0 警 | site 构建通过。

**方法论要点**（调通过程沉淀）：
1. 先分清「模型不行」还是「场景输入不行」再动门禁——`assignment-intake` 交付物本就是
   「解析含糊作业 + 列待确认项」，触发拒答门是场景输入不完备；`visual-style-anchor`
   反问项目信息同理。补足输入 + 明示「直接产出」后即过。
2. 占位符门按行豁免白名单（自审声明 / 功能语境如「可用占位符列表」），真 TODO 照拦；
   豁免逐例收敛，不做全开放。
3. 逐技能场景输出入库 `tests/_scenario_artifacts/`（含 LLM 输出与重采产物），合并报告
   `tests/_full_test_artifacts/scenario_report.md`（每技能模式/模型/耗时/门禁明细）。

## 9. 复现

```bash
python3 -m pytest skills -q                        # 全部单测通过
python3 tools/validate_skills.py                   # 154 skills, 0 errors, 0 warnings
python3 tools/run_skill_smoke.py                   # 121/121 pass (offline=0 dep=0)
python3 tools/scenario_harness.py                  # 静态+LLM 双层 154/154（LLM 层需 model_route 可用）
python3 tools/scenario_harness.py --llm-only       # 仅 LLM 层
python3 build.py                                   # 重建 dist，回填 manifest size/sha256
python3 tools/build_site.py                        # 重建 site（154 skills / 36 packs / 18 domains / 62 chains）
```
