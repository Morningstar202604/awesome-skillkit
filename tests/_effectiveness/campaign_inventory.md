# 全技能改造战役总账（六要素 × 命令级扫描）

> 生成：2026-09-22T01:49:33.992349+00:00 ｜ 扫描来源：`tests\_effectiveness\real_scenario_fullsweep.json`（2026-09-22T01:19:44.782488+00:00）
> 优先级分布：{'OK': 4, 'P0': 62, 'P1': 16, 'P2': 65, 'P3': 8}
> 六要素分布：{0: 78, 1: 60, 2: 2, 3: 8, 4: 2, 5: 2, 6: 3}

| 优先级 | 含义 | 数量 |
|---|---|---|
| P0 | 命令级扫描 fail/error（可运行性缺陷） | 62 |
| P1 | SKILL.md 无可解析用法示例（文档债） | 16 |
| P2 | 六要素 ≤2 分（配方缺失） | 65 |
| P3 | 六要素 3~5 分（补齐即可） | 8 |
| OK | 已达标（6 分或本战役已完成） | 4 |

## P0 —— 命令级 FAIL（先修可运行性）（62）

| 技能 | 六要素分 | 扫描判定 |
|---|---|---|
| audio/podcast-producer | 0 | fail |
| chat/chat-prompt-engineer | 0 | fail |
| dataviz/dashboard-designer | 0 | fail |
| education/exercise-generator | 0 | fail |
| knowledge/knowledge-graph-builder | 0 | fail |
| knowledge/personal-wiki | 0 | fail |
| marketing/channel-adapter | 0 | fail |
| meta/skill-linter | 0 | fail |
| office/epub-builder | 0 | fail |
| office/pdf-pipeline | 0 | fail |
| programming/ai-engineering/mcp-server-builder | 0 | fail |
| programming/ai-engineering/skill-tester | 0 | fail |
| programming/ai-engineering/skill-tester/assets/sample-skill | 0 | fail |
| programming/api/api-design-reviewer | 0 | fail |
| programming/architecture/migration-architect | 0 | fail |
| programming/architecture/monorepo-navigator | 0 | fail |
| programming/architecture/senior-architect | 0 | fail |
| programming/cicd/ship-gate | 0 | fail |
| programming/code-quality/code-reviewer | 0 | fail |
| programming/code-quality/dependency-auditor | 0 | fail |
| programming/code-quality/tdd-guide | 0 | fail |
| programming/incident/slo-architect | 0 | fail |
| programming/infrastructure/kubernetes-operator | 0 | fail |
| programming/infrastructure/terraform-patterns | 0 | fail |
| programming/performance/performance-profiler | 0 | fail |
| programming/security/env-secrets-manager | 0 | fail |
| programming/workflow/agent-designer | 0 | fail |
| tools/batch-renamer | 0 | fail |
| tools/format-converter | 0 | fail |
| video/video-editor | 0 | fail |
| writing/blog/cnblogs-skill | 0 | fail |
| writing/blog/csdn-publisher | 0 | fail |
| writing/blog/jianshu-publisher | 0 | fail |
| writing/blog/static-blog-deploy | 0 | fail |
| writing/juejin/juejin-publisher | 0 | fail |
| writing/orchestrator/cross-post-orchestrator | 0 | error |
| writing/video/bilibili-publisher | 0 | fail |
| writing/wechat/wechat-mp-publisher | 0 | fail |
| writing/zhihu/zhihu-content-manager | 0 | fail |
| design/layout-spec-auditor | 1 | fail |
| integrations/feishu-dingtalk-bridge | 1 | fail |
| integrations/issue-tracker-sync | 1 | fail |
| integrations/notion-workspace | 1 | fail |
| meta/agent-eval-harness | 1 | error |
| meta/weekly-report-generator | 1 | fail |
| office/docx-template-fill | 1 | fail |
| programming/code-quality/tech-debt-tracker | 1 | fail |
| programming/containers/docker-development | 1 | fail |
| programming/containers/helm-chart-builder | 1 | fail |
| programming/database/database-designer | 1 | fail |
| programming/database/sql-database-assistant | 1 | fail |
| programming/github/changelog-generator | 1 | fail |
| programming/github/git-worktree-manager | 1 | fail |
| programming/incident/incident-commander | 1 | fail |
| programming/testing/webapp-e2e-harness | 1 | error |
| tools/bank-statement-reconcile | 1 | fail |
| tools/file-organizer | 1 | fail |
| tools/invoice-organizer | 1 | fail |
| video/video-thumbnail | 1 | fail |
| writing/ai-trace-auditor | 3 | fail |
| programming/planning/code-generator | 4 | fail |
| video/storyboard-designer | 6 | fail |

## P1 —— 无用法示例（补文档债）（16）

| 技能 | 六要素分 | 扫描判定 |
|---|---|---|
| meta/skill-finder | 0 | no-example |
| programming/math/model-formulator | 0 | no-example |
| programming/security/secrets-vault-manager | 0 | no-example |
| programming/testing/webapp-flow-tester | 0 | no-example |
| video/video-prompt-engineer | 0 | no-example |
| programming/planning/code-intent-planner | 1 | no-example |
| programming/security/prompt-injection-guard | 1 | no-example |
| writing/community/douban-publisher | 1 | no-example |
| writing/community/oschina-publisher | 1 | no-example |
| writing/community/segmentfault-publisher | 1 | no-example |
| writing/community/v2ex-publisher | 1 | no-example |
| writing/news/baijiahao-publisher | 1 | no-example |
| writing/news/toutiao-publisher | 1 | no-example |
| writing/social/weibo-publisher | 1 | no-example |
| writing/social/xiaohongshu-publisher | 1 | no-example |
| programming/security/pii-redactor | 2 | no-example |

## P2 —— 配方缺失（≤2 分）（65）

| 技能 | 六要素分 | 扫描判定 |
|---|---|---|
| audio/episode-publisher | 0 | n/a |
| audio/tts-voice-director | 0 | n/a |
| dataviz/chart-recommender | 0 | n/a |
| design/frontend-design-director | 0 | n/a |
| education/course-designer | 0 | n/a |
| education/feynman-explainer | 0 | n/a |
| marketing/campaign-designer | 0 | n/a |
| music/music-generation | 0 | n/a |
| office/docx-writer | 0 | pass |
| office/excel-assistant | 0 | n/a |
| office/meeting-notes | 0 | n/a |
| paper/arch-diagram | 0 | pass |
| paper/figure-maker | 0 | pass |
| ppt/ppt-builder | 0 | pass |
| programming/ai-engineering/feature-flags-architect | 0 | pass |
| programming/ai-engineering/self-eval | 0 | n/a |
| programming/api/api-test-suite-builder | 0 | n/a |
| programming/cicd/ci-cd-pipeline-builder | 0 | pass |
| programming/cicd/spec-driven-workflow | 0 | pass |
| programming/infrastructure/observability-designer | 0 | pass |
| programming/math/result-visualizer | 0 | pass |
| programming/math/simulation-runner | 0 | pass |
| programming/ml/ml-pipeline | 0 | pass |
| programming/planning/deep-research | 0 | pass |
| programming/planning/web-search | 0 | pass |
| tools/task-scheduler | 0 | pass |
| video/image-generation | 0 | n/a |
| video/nailong-laugh-shorts | 0 | n/a |
| video/shot-recipe-designer | 0 | n/a |
| video/video-generation | 0 | n/a |
| video/video-lip-sync | 0 | pass |
| video/video-subtitles | 0 | pass |
| video/video-voice-synth | 0 | pass |
| writing/assets/ai-cover-generator | 0 | pass |
| design/frontend-component-lab | 1 | pass |
| education/assignment-intake | 1 | n/a |
| education/solution-drafter | 1 | n/a |
| integrations/cloud-drive-manager | 1 | pass |
| memory/memory-architect | 1 | n/a |
| memory/memory-extractor | 1 | n/a |
| memory/memory-manager | 1 | n/a |
| memory/memory-retriever | 1 | n/a |
| meta/session-handoff | 1 | pass |
| meta/skill-author | 1 | n/a |
| office/career-ops-lite | 1 | pass |
| office/internal-comms-writer | 1 | n/a |
| office/resume-tailor | 1 | n/a |
| paper/ai-humanizer | 1 | pass |
| paper/anti-defensive | 1 | pass |
| paper/experiment-runner | 1 | pass |
| paper/latex-formatter | 1 | pass |
| paper/lit-review | 1 | pass |
| paper/neural-net-draw | 1 | pass |
| paper/paper-topic-selector | 1 | pass |
| paper/pub-plotter | 1 | pass |
| paper/self-reviewer | 1 | pass |
| paper/tex-cleaner | 1 | pass |
| programming/data/etl-builder | 1 | pass |
| programming/data/feature-engineer | 1 | pass |
| programming/debug/debug-diagnoser | 1 | pass |
| programming/github/pr-review-expert | 1 | n/a |
| programming/incident/runbook-generator | 1 | pass |
| video/ai-baby-podcast | 1 | n/a |
| writing/personal-voice-profile | 1 | n/a |
| paper/journal-adapt | 2 | pass |

## P3 —— 3~5 分（补齐要素）（8）

| 技能 | 六要素分 | 扫描判定 |
|---|---|---|
| design/design-brief-interpreter | 3 | n/a |
| marketing/product-copywriter | 3 | n/a |
| programming/math/model-solver | 3 | pass |
| video/visual-style-anchor | 3 | n/a |
| writing/content-editor | 3 | pass |
| writing/humanize-rewriter | 3 | n/a |
| writing/seo-optimizer | 3 | pass |
| writing/article-drafter | 4 | pass |

## 本战役已完成（5）

- design/image-prompt-engineer（六要素 5 分，批次 4）
- education/own-voice-rewrite（六要素 5 分，批次 4）
- video/storyboard-designer（六要素 6 分，批次 4）
- video/video-script-writer（六要素 6 分，批次 4）
- writing/article-outliner（六要素 6 分，批次 4）