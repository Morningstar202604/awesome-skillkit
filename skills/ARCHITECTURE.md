# Skill System Architecture — Full Architecture Diagram and Logic Chain

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              USER INTENT                                        │
│           "Build me an e-commerce site" / "Write an article for 5 platforms" / "Make a short video"
└──────────────────────────────────────┬──────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    LAYER 0: UNIVERSAL ROUTER                                    │
│                    universal_skill_router.py                                    │
│                                                                                 │
│   Intent Classify → Domain Select → Chain Resolve → Dispatch                    │
│   classify intent    select domain   resolve chain   dispatch task             │
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
         │              LAYER 3: SKILL EXECUTION                            │
         │                                                                    │
         │  Each skill: SKILL.md + scripts/ + references/ + tests/          │
         │  Input: structured JSON context → Output: structured JSON result │
         └──────────────────────────────────┬───────────────────────────────┘
                                            │
                                            ▼
         ┌──────────────────────────────────────────────────────────────────┐
         │           LAYER 4: VERIFICATION & FEEDBACK                       │
         │                                                                    │
         │  Result validation → Quality scoring → Retry/Iterate → Audit    │
         │  validate result      score quality    retry loop     audit log    │
         └──────────────────────────────────────────────────────────────────┘
```

---

## Five Scenarios: Complete Logic Chains

### Scenario 1: Full Project Development ("Build me a user management system")

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Scenario: Full Project Development                                          │
│ Trigger: "Build me a XX system/website/API"                                 │
└─────────────────────────────────────────────────────────────────────────────┘

    User Input
        │
        ▼
┌─────────────────────────┐
│ code-intent-planner     │  L1: regex match → L2: Flash LLM → L3: Pro LLM
│ (intent + decomposition)│  Output: intent_type, task_decomposition, plan
└────────────┬────────────┘
             │
             ├─── [conditional: if intent needs external knowledge]
             │         │
             │         ▼
             │  ┌─────────────────┐
             │  │ deep-research    │  Multi-round search + synthesis
             │  │ (deep research)  │  Output: structured_report + sources
             │  └────────┬────────┘
             │           │
             │  ┌────────┴──────────┐
             │  │ web-search      │  SearXNG + DuckDuckGo
             │  │ (web search)     │  Output: results[]
             │  └───────────────────┘
             │
             ▼
┌─────────────────────────┐
│ code-generator          │  L1: template engine → L2: LLM generation
│ (code generation)       │  Output: generated_files[]
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ tdd-guide               │  Test generation + coverage analysis
│ (test-driven)           │  Output: test_files[], coverage_report
└────────────┬────────────┘
             │
             ├─── [if tests FAIL]
             │         │
             │         ▼
             │  ┌──────────────────┐
             │  │ code-generator    │  ← feedback loop: fix per failing tests
             │  │ (regenerate)     │
             │  └────────┬─────────┘
             │           │
             │           ▼ (retry up to 3x)
             │
             ▼
┌─────────────────────────┐
│ code-reviewer           │  Static analysis + security check + complexity score
│ (code review)            │  Output: review_report, issues[]
└────────────┬────────────┘
             │
             ├─── [if critical issues]
             │         │
             │         ▼
             │  ┌──────────────────┐
             │  │ code-generator    │  ← fix critical issues
             │  └──────────────────┘
             │
             ▼
┌─────────────────────────┐
│ dependency-auditor      │  Dependency security + license compliance
│ (dependency audit)      │  Output: vulnerability_report
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ ci-cd-pipeline-builder  │  Generate CI/CD pipeline per tech stack
│ (CI/CD build)           │  Output: workflow_yaml
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ ship-gate               │  Pre-launch security/db/deploy/quality audit
│ (release gate)          │  Output: pass/fail + blocking_items[]
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ runbook-generator       │  Generate ops runbook
│ (ops manual)            │  Output: runbook_markdown
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ incident-commander      │  Incident response framework + escalation path
│ (incident command)      │  Output: incident_playbook
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ observability-designer  │  SLI/SLO + monitoring alert design
│ (observability)         │  Output: monitoring_config
└─────────────────────────┘

    Final Output: complete project (code + tests + CI/CD + ops + monitoring)
```

### Scenario 2: Multi-Platform Content Publishing ("Write a tech article and post to 5 platforms")

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Scenario: Multi-Platform Content Publishing                                │
│ Trigger: "Write an article" / "Publish to XX platform" / "Multi-platform distribution"
└─────────────────────────────────────────────────────────────────────────────┘

    User Input (topic + style + target platforms)
        │
        ▼
┌─────────────────────────┐
│ deep-research           │  Gather material, data, citations
│ (deep research)         │  Output: research_report + sources[]
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ web-search              │  Supplementary search for specific citations/data
│ (web search)            │  Output: results[]
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ [Content Generation]    │  LLM generates article from research + platform style
│ (LLM direct)           │  Output: article_markdown
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ ai-cover-generator      │  Generate cover image (text-to-image)
│ (cover generation)      │  Output: cover_image_path
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ cross-post-orchestrator │  Check platform credentials + generate execution plan
│ (multi-platform orchestration) │  Output: execution_plan + preconditions
└────────────┬────────────┘
             │
             ├──────────────────────────────────────────┐
             │          │          │          │          │
             ▼          ▼          ▼          ▼          ▼
┌──────────┐┌────────┐┌────────┐┌────────┐┌────────────┐
│wechat-mp ││csdn-   ││juejin- ││baijia- ││ [other     ]│
│publisher ││pub     ││pub     ││hao-pub ││ publisher  │
└────┬─────┘└───┬────┘└───┬────┘└───┬────┘└─────┬──────┘
     │          │          │          │            │
     ▼          ▼          ▼          ▼            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                PUBLISH VERIFICATION                                         │
│  Check each platform's returned status → summarize results → generate publish ledger
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
                                   ▼
                     Final Output: article published to N platforms + link list
```

### Scenario 3: Creative Video/Content Production ("Make an AI baby podcast" / "Make a Nailong video")

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Scenario: Creative Video Content Production                                  │
│ Trigger: "Make a video" / "Generate a short film" / "AI baby podcast" / "Nailong video"
└─────────────────────────────────────────────────────────────────────────────┘

    User Input (concept + style + platform)
        │
        ▼
┌─────────────────────────┐
│ [Script Generation]    │  LLM generates script (dialogue/voiceover/storyboard)
│ (script - LLM)         │  Output: script_json {scenes[], dialogue[], timing}
└────────────┬────────────┘
             │
             ├─── [if music needed]
             │         │
             │         ▼
             │  ┌─────────────────────┐
             │  │ music-generation    │  Text-to-music (style/instruments/duration)
             │  │ (music generation)  │  Output: music_file_path
             │  └─────────────────────┘
             │
             ▼
┌─────────────────────────┐
│ image-generation        │  Text-to-image / image-to-image (characters/backgrounds/scenes)
│ (image generation)      │  Output: images[]
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ video-generation        │  Text-to-video / image-to-video
│ (video generation)       │  Output: video_file_path
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ [Assembly - LLM]       │  Combine: video + music + subtitles + title
│ (assembly - LLM)       │  Output: final_video + metadata
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ bilibili-publisher      │  Publish to target platform
│ toutiao-publisher       │
│ [platform selection]    │  Output: publish_url
└─────────────────────────┘

    Final Output: complete video + published link
```

### Scenario 4: Production Incident Response ("Production service is down/performance degraded")

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Scenario: Production Incident Response                                       │
│ Trigger: "Service is down" / "Performance degraded" / "Production incident" / "Need to roll back"
└─────────────────────────────────────────────────────────────────────────────┘

    User Input (symptom + service name)
        │
        ▼
┌─────────────────────────┐
│ incident-commander      │  Incident grading + timeline reconstruction + escalation path
│ (incident command)      │  Output: incident_record {severity, timeline, actions}
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ runbook-generator       │  Load/generate the service's runbook
│ (ops manual)            │  Output: runbook_steps[]
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ code-intent-planner     │  Analyze symptoms → locate root cause
│ (intent analysis)       │  Output: root_cause_hypothesis
└────────────┬────────────┘
             │
             ├─── [if need to search for similar issues]
             │         │
             │         ▼
             │  ┌─────────────────────┐
             │  │ deep-research       │  Search known issues/patches
             │  │ (research similar)  │  Output: known_fixes[]
             │  └─────────────────────┘
             │
             ▼
┌─────────────────────────┐
│ code-generator          │  Generate fix code
│ (fix code)              │  Output: fix_patch
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ tdd-guide               │  Regression test verification
│ (regression tests)      │  Output: test_results
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ migration-architect     │  Zero-downtime deploy + rollback plan
│ (migration architecture)│  Output: deploy_plan + rollback_plan
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ ship-gate               │  Pre-deploy security verification
│ (release gate)          │  Output: go/no-go
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ observability-designer  │  Post-deploy monitoring verification
│ (observability)         │  Output: health_confirmed
└─────────────────────────┘

    Final Output: incident resolved + root cause + fix + monitoring confirmed
```

### Scenario 5: Presentation Production + Speech ("Help me make a project report PPT")

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Scenario: Presentation Production                                            │
│ Trigger: "Make a PPT" / "Report materials" / "Speech script"                │
└─────────────────────────────────────────────────────────────────────────────┘

    User Input (topic + audience + time)
        │
        ▼
┌─────────────────────────┐
│ deep-research           │  Gather data, cases, arguments
│ (deep research)         │  Output: research_brief
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ ppt-builder             │  Full PPT pipeline:
│ (PPT build)             │   outline → visual → assets → render → notes
│                         │  Sub-skills:
│   ├─ ppt-outline-arch   │  Storyline + outline
│   ├─ ppt-visual-design  │  Color scheme + layout
│   ├─ ppt-assets-curator │  Assets + charts
│   ├─ ppt-prompt-formula │  AI generation prompts
│   ├─ ppt-rehearsal-note │  Speaker notes
│   └─ ppt-render-export  │  Export pptx/pdf
└────────────┬────────────┘
             │
             ├─── [if need images]
             │         │
             │         ▼
             │  ┌─────────────────────┐
             │  │ image-generation     │  Generate illustrations
             │  └─────────────────────┘
             │
             ▼
┌─────────────────────────┐
│ [Delivery - LLM]       │  Final file + speaking points
│ (delivery)              │  Output: pptx_file + speaker_notes
└─────────────────────────┘

    Final Output: PPT file + speech script + asset list
```

---

## Gap Analysis (current system shortcomings)

| # | Gap | Impact | Solution |
|---|-----|------|---------|
| 1 | **No unified entry** | Users don't know which skill to start with; manual selection needed | `universal_skill_router.py` unified routing |
| 2 | **No shared context protocol** | Data formats inconsistent across skills; cannot auto-chain | Define `SkillContext` JSON schema |
| 3 | **No feedback loop** | Test failures don't trace back; review failures don't get fixed | Add retry + feedback mechanism to pipeline |
| 4 | **No cross-domain orchestration** | "Make a blog" needs programming + writing + scenarios | `cross_domain_orchestrator.py` |
| 5 | **No orchestrator under scenarios/** | Video/PPT sub-skills have no coordination | `creative_pipeline.py` |
| 6 | **No skill health check** | No awareness when SearXNG is down or APIs unreachable | `skill_health_check.py` |
| 7 | **No audit log** | Don't know which skills ran or how long they took | `execution_audit_log.jsonl` |
| 8 | **writing platform skills have no unified verification** | No summary of publish success/failure | Extend cross-post-orchestrator |
| 9 | **No degradation strategy** | One skill failing breaks the whole chain | Fallback chain + partial success |
| 10 | **No skill combination templates** | Per-scenario skill combos rely on human memory | `skill_chains.json` predefined |

---

## Layered Architecture (detailed)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 0: ROUTING                                                           │
│                                                                             │
│  universal_skill_router.py                                                  │
│  ├─ intent_classifier:  intent recognition (reuse code-intent-planner L1) │
│  ├─ domain_selector:    domain selection (programming/writing/scenarios/cross)
│  ├─ chain_resolver:     chain resolution (skill_chains.json lookup)       │
│  └─ dispatch:           dispatch execution (subprocess / import)           │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│ LAYER 1: ORCHESTRATION                                                     │
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
│ LAYER 2: EXECUTION                                                         │
│                                                                             │
│  64 individual skills, each with:                                            │
│  ├─ SKILL.md (knowledge + instructions)                                     │
│  ├─ scripts/ (executable logic)                                             │
│  ├─ references/ (domain knowledge)                                           │
│  └─ tests/ (verification)                                                   │
│                                                                             │
│  Data protocol (SkillContext):                                              │
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
│ LAYER 3: VERIFICATION & FEEDBACK                                           │
│                                                                             │
│  ├─ result_validator.py:    per-step output schema validation              │
│  ├─ quality_scorer.py:      quality scoring (confidence, completeness, risk)
│  ├─ feedback_loop.py:       fail → diagnose → retry (max 3) → degrade      │
│  ├─ skill_health_check.py:  dependency availability check (network, API, files)
│  └─ execution_audit_log:    full-chain log (jsonl)                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Skill Coordination Matrix (who calls whom)

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
                    │  → code-intent-planner (diagnose)                       │
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
                    │  → video-generation (clips)                              │
                    │  → [platform publishers]                               │
                    │                                                          │
  universal-router │  → code-intent-planner (intent recognition)              │
  ────────────────┼  → [domain orchestrators]                                │
                    └──────────────────────────────────────────────────────────┘
```

---

## Degradation Strategy (Graceful Degradation)

```
Normal:   A → B → C → D → E (full chain)
D1 fail:  A → B → C → [D1 FAIL] → D2 (fallback) → E
All fail: A → B → C → [D FAIL] → SKIP D, mark incomplete, deliver partial
Timeout:  A → B → [C TIMEOUT] → use cached result from C's previous run
```

Each skill defines:
- `primary`: primary path
- `fallback`: degradation path (at least 1 alternative)
- `skip_if_fail`: whether this skill's failure blocks downstream (false = skip and continue)
