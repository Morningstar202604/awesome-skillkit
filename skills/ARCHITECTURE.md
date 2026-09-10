# Skill System Architecture — 完整架构图与逻辑链

## 系统总览

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              USER INTENT                                        │
│           "帮我做一个电商网站" / "写篇文章发5个平台" / "做个短视频"              │
└──────────────────────────────────────┬──────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    LAYER 0: UNIVERSAL ROUTER (统一路由)                         │
│                    universal_skill_router.py                                    │
│                                                                                 │
│   Intent Classify → Domain Select → Chain Resolve → Dispatch                    │
│   识别意图类型    选择执行域     解析链路      分发任务                        │
└──────────────────────────────────────┬──────────────────────────────────────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    ▼                  ▼                  ▼
         ┌───────────────┐  ┌────────────────┐  ┌─────────────────┐
         │  PROGRAMMING  │  │    WRITING     │  │   SCENARIOS     │
         │   DOMAIN      │  │    DOMAIN      │  │    DOMAIN       │
         │  (37 skills)  │  │  (18 skills)   │  │   (9 skills)    │
         └───────┬───────┘  └───────┬────────┘  └────────┬────────┘
                 │                  │                     │
                 ▼                  ▼                     ▼
         ┌──────────────────────────────────────────────────────────────────┐
         │              LAYER 3: SKILL EXECUTION (技能执行层)               │
         │                                                                    │
         │  Each skill: SKILL.md + scripts/ + references/ + tests/          │
         │  Input: structured JSON context → Output: structured JSON result │
         └──────────────────────────────────┬───────────────────────────────┘
                                            │
                                            ▼
         ┌──────────────────────────────────────────────────────────────────┐
         │           LAYER 4: VERIFICATION & FEEDBACK (验证反馈层)          │
         │                                                                    │
         │  Result validation → Quality scoring → Retry/Iterate → Audit    │
         │  结果验证            质量打分       重试循环       审计日志       │
         └──────────────────────────────────────────────────────────────────┘
```

---

## 五大场景完整逻辑链

### 场景 1: 完整项目开发 ("帮我做一个用户管理系统")

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Scenario: Full Project Development                                          │
│ Trigger: "帮我做一个XX系统/网站/API"                                         │
└─────────────────────────────────────────────────────────────────────────────┘

    User Input
        │
        ▼
┌─────────────────────────┐
│ code-intent-planner     │  L1: 正则匹配 → L2: Flash LLM → L3: Pro LLM
│ (意图识别 + 任务分解)   │  输出: intent_type, task_decomposition, plan
└────────────┬────────────┘
             │
             ├─── [conditional: if intent needs external knowledge]
             │         │
             │         ▼
             │  ┌─────────────────┐
             │  │ deep-research   │  多轮搜索 + 信息综合
             │  │ (深度调研)      │  输出: structured_report + sources
             │  └────────┬────────┘
             │           │
             │  ┌────────┴──────────┐
             │  │ web-search        │  SearXNG + DuckDuckGo
             │  │ (网络搜索)        │  输出: results[]
             │  └───────────────────┘
             │
             ▼
┌─────────────────────────┐
│ code-generator          │  L1: 模板引擎 → L2: LLM 生成
│ (代码生成)              │  输出: generated_files[]
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ tdd-guide               │  测试生成 + 覆盖率分析
│ (测试驱动)              │  输出: test_files[], coverage_report
└────────────┬────────────┘
             │
             ├─── [if tests FAIL]
             │         │
             │         ▼
             │  ┌──────────────────┐
             │  │ code-generator   │  ← 反馈循环: 根据失败测试修复
             │  │ (regenerate)     │
             │  └────────┬─────────┘
             │           │
             │           ▼ (retry up to 3x)
             │
             ▼
┌─────────────────────────┐
│ code-reviewer           │  静态分析 + 安全检查 + 复杂度评分
│ (代码审查)              │  输出: review_report, issues[]
└────────────┬────────────┘
             │
             ├─── [if critical issues]
             │         │
             │         ▼
             │  ┌──────────────────┐
             │  │ code-generator   │  ← 修复 critical issues
             │  └──────────────────┘
             │
             ▼
┌─────────────────────────┐
│ dependency-auditor      │  依赖安全 + 许可证合规
│ (依赖审计)              │  输出: vulnerability_report
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ ci-cd-pipeline-builder  │  根据技术栈生成 CI/CD 管道
│ (CI/CD 构建)            │  输出: workflow_yaml
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ ship-gate               │  上线前安全/数据库/部署/质量审计
│ (发布门禁)              │  输出: pass/fail + blocking_items[]
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ runbook-generator       │  生成运维 runbook
│ (运维手册)              │  输出: runbook_markdown
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ incident-commander      │  事故响应框架 + 升级路径
│ (事故指挥)              │  输出: incident_playbook
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ observability-designer  │  SLI/SLO + 监控告警设计
│ (可观测性)              │  输出: monitoring_config
└─────────────────────────┘

    Final Output: 完整项目 (代码 + 测试 + CI/CD + 运维 + 监控)
```

### 场景 2: 多平台内容发布 ("写一篇技术文章发5个平台")

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Scenario: Multi-Platform Content Publishing                                │
│ Trigger: "写篇文章" / "发布到XX平台" / "多平台分发"                         │
└─────────────────────────────────────────────────────────────────────────────┘

    User Input (topic + style + target platforms)
        │
        ▼
┌─────────────────────────┐
│ deep-research           │  收集素材、数据、引用
│ (深度调研)              │  输出: research_report + sources[]
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ web-search              │  补充搜索具体引用/数据
│ (网络搜索)              │  输出: results[]
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ [Content Generation]    │  LLM 根据研究结果 + 平台风格生成文章
│ (LLM 直接)              │  输出: article_markdown
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ ai-cover-generator      │  生成封面图 (文生图)
│ (封面生成)              │  输出: cover_image_path
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ cross-post-orchestrator │  检查各平台凭据 + 生成执行计划
│ (多平台编排)            │  输出: execution_plan + preconditions
└────────────┬────────────┘
             │
             ├──────────────────────────────────────────┐
             │          │          │          │          │
             ▼          ▼          ▼          ▼          ▼
┌──────────┐┌────────┐┌────────┐┌────────┐┌────────────┐
│wechat-mp ││csdn-   ││juejin- ││baijia- ││  [其他平台] │
│publisher ││pub     ││pub     ││hao-pub ││  publisher │
└────┬─────┘└───┬────┘└───┬────┘└───┬────┘└─────┬──────┘
     │          │          │          │            │
     ▼          ▼          ▼          ▼            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                PUBLISH VERIFICATION                                         │
│  检查每个平台返回 status → 汇总发布结果 → 生成发布台账                     │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
                                   ▼
                     Final Output: 文章已发布到 N 个平台 + 链接清单
```

### 场景 3: 创意视频/内容制作 ("做个AI宝宝播客" / "做个奶龙视频")

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Scenario: Creative Video Content Production                                  │
│ Trigger: "做个视频" / "生成短片" / "AI宝宝播客" / "奶龙视频"                │
└─────────────────────────────────────────────────────────────────────────────┘

    User Input (concept + style + platform)
        │
        ▼
┌─────────────────────────┐
│ [Script Generation]    │  LLM 生成脚本 (对话/旁白/分镜)
│ (脚本生成 - LLM)        │  输出: script_json {scenes[], dialogue[], timing}
└────────────┬────────────┘
             │
             ├─── [if music needed]
             │         │
             │         ▼
             │  ┌─────────────────────┐
             │  │ music-generation    │  文生音乐 (风格/乐器/时长)
             │  │ (音乐生成)          │  输出: music_file_path
             │  └─────────────────────┘
             │
             ▼
┌─────────────────────────┐
│ image-generation        │  文生图/图生图 (角色/背景/场景)
│ (图片生成)              │  输出: images[]
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ video-generation        │  文生视频/图生视频
│ (视频生成)              │  输出: video_file_path
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ [Assembly - LLM]       │  拼接: 视频 + 音乐 + 字幕 + 标题
│ (合成 - LLM)           │  输出: final_video + metadata
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ bilibili-publisher      │  发布到目标平台
│ toutiao-publisher       │
│ [平台选择]              │  输出: publish_url
└─────────────────────────┘

    Final Output: 完整视频 + 已发布链接
```

### 场景 4: 线上事故处理 ("线上服务挂了/性能下降")

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Scenario: Production Incident Response                                       │
│ Trigger: "服务挂了" / "性能下降" / "线上事故" / "需要回滚"                 │
└─────────────────────────────────────────────────────────────────────────────┘

    User Input (symptom + service name)
        │
        ▼
┌─────────────────────────┐
│ incident-commander      │  事故分级 + 时间线重建 + 升级路径
│ (事故指挥)              │  输出: incident_record {severity, timeline, actions}
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ runbook-generator       │  加载/生成该服务的 runbook
│ (运维手册)              │  输出: runbook_steps[]
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ code-intent-planner     │  分析症状 → 定位根因
│ (意图分析)              │  输出: root_cause_hypothesis
└────────────┬────────────┘
             │
             ├─── [if need to search for similar issues]
             │         │
             │         ▼
             │  ┌─────────────────────┐
             │  │ deep-research       │  搜索已知 issue/patch
             │  │ (调研类似问题)      │  输出: known_fixes[]
             │  └─────────────────────┘
             │
             ▼
┌─────────────────────────┐
│ code-generator          │  生成修复代码
│ (修复代码)              │  输出: fix_patch
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ tdd-guide               │  回归测试验证
│ (回归测试)              │  输出: test_results
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ migration-architect     │  零停机部署 + 回滚方案
│ (迁移架构)              │  输出: deploy_plan + rollback_plan
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ ship-gate               │  部署前安全验证
│ (发布门禁)              │  输出: go/no-go
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ observability-designer  │  部署后监控验证
│ (可观测性)              │  输出: health_confirmed
└─────────────────────────┘

    Final Output: 事故已解决 + 根因 + 修复 + 监控确认
```

### 场景 5: PPT 制作 + 演讲 ("帮我做一个项目汇报 PPT")

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Scenario: Presentation Production                                            │
│ Trigger: "做个PPT" / "汇报材料" / "演讲稿"                                   │
└─────────────────────────────────────────────────────────────────────────────┘

    User Input (topic + audience + time)
        │
        ▼
┌─────────────────────────┐
│ deep-research           │  收集数据、案例、论据
│ (深度调研)              │  输出: research_brief
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ ppt-builder             │  完整 PPT 流水线:
│ (PPT 构建)              │   outline → visual → assets → render → notes
│                         │  子 skills:
│   ├─ ppt-outline-arch   │  故事线 + 大纲
│   ├─ ppt-visual-design  │  配色 + 版式
│   ├─ ppt-assets-curator │  素材 + 图表
│   ├─ ppt-prompt-formula │  AI 生成提示词
│   ├─ ppt-rehearsal-note │  演讲备注
│   └─ ppt-render-export  │  导出 pptx/pdf
└────────────┬────────────┘
             │
             ├─── [if need images]
             │         │
             │         ▼
             │  ┌─────────────────────┐
             │  │ image-generation    │  生成配图/插图
             │  └─────────────────────┘
             │
             ▼
┌─────────────────────────┐
│ [Delivery - LLM]       │  最终文件 + 演讲要点
│ (交付)                 │  输出: pptx_file + speaker_notes
└─────────────────────────┘

    Final Output: PPT 文件 + 演讲稿 + 素材清单
```

---

## Gap 分析（当前系统不足之处）

| # | Gap | 影响 | 解决方案 |
|---|-----|------|---------|
| 1 | **无统一入口** | 用户不知道从哪个 skill 开始，需要手动选 | `universal_skill_router.py` 统一路由 |
| 2 | **无共享上下文协议** | skill 之间数据格式不统一，无法自动串联 | 定义 `SkillContext` JSON schema |
| 3 | **无反馈循环** | 测试失败不回溯、审查不通过不修复 | pipeline 加 retry + feedback 机制 |
| 4 | **无跨域编排** | "做个博客"需要 programming + writing + scenarios | `cross_domain_orchestrator.py` |
| 5 | **scenarios/ 无编排器** | 视频/PPT 子 skill 之间无协调 | `creative_pipeline.py` |
| 6 | **无 skill 健康检查** | SearXNG 挂了、API 不通时无感知 | `skill_health_check.py` |
| 7 | **无审计日志** | 不知道哪些 skill 执行了、耗时多少 | `execution_audit_log.jsonl` |
| 8 | **writing 各平台 skill 无统一验证** | 发布成功与否无汇总 | cross-post-orchestrator 扩展 |
| 9 | **无降级策略** | 某 skill 失败整个链路中断 | fallback chain + partial success |
| 10 | **无 skill 组合模板** | 每个场景的 skill 组合靠人记忆 | `skill_chains.json` 预定义 |

---

## 分层架构 (详细)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 0: ROUTING (路由层)                                                   │
│                                                                             │
│  universal_skill_router.py                                                  │
│  ├─ intent_classifier:  意图识别 (复用 code-intent-planner L1)            │
│  ├─ domain_selector:    域选择 (programming/writing/scenarios/cross)      │
│  ├─ chain_resolver:     链路解析 (skill_chains.json 查表)                │
│  └─ dispatch:           分发执行 (subprocess / import)                    │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│ LAYER 1: ORCHESTRATION (编排层)                                             │
│                                                                             │
│  ├─ programming_orchestrator.py (enhanced pipeline_orchestrator.py)        │
│  │    intent → research → generate → test → review → ci → deploy           │
│  │    with feedback loops (test fail → regenerate, review fail → fix)      │
│  │                                                                         │
│  ├─ writing_orchestrator.py (enhanced cross-post-orchestrator)             │
│  │    research → draft → cover → [platform×N] → verify                    │
│  │                                                                         │
│  ├─ creative_orchestrator.py (NEW)                                          │
│  │    script → [image/music/video] → assembly → publish                    │
│  │                                                                         │
│  ├─ incident_orchestrator.py (NEW)                                          │
│  │    assess → runbook → diagnose → fix → test → deploy → verify           │
│  │                                                                         │
│  └─ cross_domain_orchestrator.py (NEW)                                      │
│       decompose → [domain1 + domain2 + ...] → merge → verify               │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│ LAYER 2: EXECUTION (执行层)                                                 │
│                                                                             │
│  64 individual skills, each with:                                            │
│  ├─ SKILL.md (knowledge + instructions)                                     │
│  ├─ scripts/ (executable logic)                                             │
│  ├─ references/ (domain knowledge)                                           │
│  └─ tests/ (verification)                                                   │
│                                                                             │
│  数据协议 (SkillContext):                                                    │
│  {                                                                           │
│    "task_id": "uuid",                                                       │
│    "intent": {"type": "implement", "raw": "...", "confidence": 0.95},      │
│    "domain": "programming",                                                  │
│    "inputs": {...},          ← upstream skill output                         │
│    "outputs": {...},         ← this skill's output                           │
│    "context": {...},         ← shared state across chain                     │
│    "feedback": null,        ← retry info if in feedback loop                │
│    "trace": [           ← audit trail                                        │
│      {"skill": "code-intent-planner", "ts": "...", "ms": 45, "ok": true},  │
│      {"skill": "code-generator", "ts": "...", "ms": 1200, "ok": true}       │
│    ]                                                                         │
│  }                                                                           │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│ LAYER 3: VERIFICATION & FEEDBACK (验证反馈层)                                │
│                                                                             │
│  ├─ result_validator.py:    每步输出 schema 校验                           │
│  ├─ quality_scorer.py:      质量打分 (confidence, completeness, risk)       │
│  ├─ feedback_loop.py:       失败 → 诊断 → 重试 (max 3) → 降级             │
│  ├─ skill_health_check.py:  依赖可用性检查 (网络、API、文件)              │
│  └─ execution_audit_log:     全链路日志 (jsonl)                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Skill 协调矩阵 (谁调用谁)

```
                    ┌──────────────────────────────────────────────────────────┐
                    │            CALLS / USES                                  │
                    │                                                          │
  code-intent-      │  → deep-research (need external knowledge)             │
  planner ──────────┼  → web-search (quick lookup)                            │
                    │  → code-generator (hand off plan)                       │
                    │                                                          │
  deep-research ────┼  → web-search (underlying search engine)                │
                    │  → image-generation (if visual research needed)         │
                    │                                                          │
  code-generator ───┼  → tdd-guide (generate tests alongside code)           │
                    │  → code-reviewer (self-review before delivery)          │
                    │                                                          │
  tdd-guide ────────┼  → code-generator (feedback: failed test → fix)        │
                    │  → performance-profiler (if perf test fails)            │
                    │                                                          │
  code-reviewer ────┼  → security-blindspot-scan (security check)            │
                    │  → code-generator (feedback: fix critical issues)       │
                    │                                                          │
  ci-cd-pipeline ───┼  → ship-gate (pre-deploy gate)                         │
                    │  → observability-designer (add monitoring)              │
                    │                                                          │
  ship-gate ────────┼  → dependency-auditor (security scan)                  │
                    │  → code-reviewer (code quality check)                   │
                    │                                                          │
  incident-cmd ─────┼  → runbook-generator (load runbook)                    │
                    │  → code-intent-planner (diagnose)                      │
                    │  → deep-research (find known fixes)                     │
                    │                                                          │
  cross-post-orch ──┼  → wechat-mp-publisher                                 │
                    │  → csdn-publisher                                      │
                    │  → juejin-publisher                                    │
                    │  → baijiahao-publisher                                 │
                    │  → [other platform publishers]                         │
                    │  → ai-cover-generator (generate cover)                 │
                    │                                                          │
  ppt-builder ──────┼  → image-generation (slide images)                     │
                    │  → deep-research (content research)                    │
                    │  → ppt-outline-arch (story structure)                  │
                    │  → ppt-visual-designer (style)                         │
                    │  → ppt-assets-curator (images/icons/charts)            │
                    │  → ppt-render-exporter (final file)                    │
                    │                                                          │
  creative-pipeline │  → image-generation (frames)                           │
  ─────────────────┼  → music-generation (BGM)                              │
                    │  → video-generation (clips)                            │
                    │  → [platform publishers]                               │
                    │                                                          │
  universal-router │  → code-intent-planner (intent recognition)            │
  ────────────────┼  → [domain orchestrators]                                │
                    └──────────────────────────────────────────────────────────┘
```

---

## 降级策略 (Graceful Degradation)

```
Normal:   A → B → C → D → E (full chain)
D1 fail:  A → B → C → [D1 FAIL] → D2 (fallback) → E
All fail: A → B → C → [D FAIL] → SKIP D, mark incomplete, deliver partial
Timeout:  A → B → [C TIMEOUT] → use cached result from C's previous run
```

每个 skill 定义:
- `primary`: 主路径
- `fallback`: 降级路径 (至少 1 个替代方案)
- `skip_if_fail`: 该 skill 失败是否阻塞后续 (false = 跳过继续)
