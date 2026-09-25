# Advanced Agent Skills & Tools Research Report

**Date**: 2026-09-25
**Scope**: Evaluate whether skillkit (153 skills / 36 packs) has additional gaps beyond the already-identified web-data-extractor and image-batch-processor.
**Method**: Strict three-filter test — (a) agents use it frequently, (b) not LLM-native reasoning, (c) not platform-covered, (d) not already in skillkit.

---

## 1. Research Summary

### Sources Consulted

| Source | What we took from it |
|---|---|
| **Anthropic Agent Skills Docs** (platform.claude.com) | Skills architecture: progressive disclosure (3 levels), YAML frontmatter contract, VM-based execution model, pre-built skills for docx/xlsx/pptx/pdf |
| **Anthropic Skill Authoring Best Practices** (docs.anthropic.com) | Concise-is-key principle, degrees-of-freedom calibration (high/medium/low), naming conventions, description as discovery slot, progressive disclosure patterns, domain-specific organization |
| **Anthropic Engineering Blog** ("Equipping agents for the real world") | Start-from-evaluation methodology, split SKILL.md when unwieldy, self-correcting loop pattern, context economy |
| **Anthropic Long-Running Agents Blog** | Feature-list file scaffolding, init.sh pattern, self-verification gates |
| **aihero.dev (Matt Pocock, 25 skills, 268K GitHub stars)** | Workflow chain methodology: grill-with-docs → to-spec → to-tickets → implement → code-review; upkeep skills (triage, diagnosing-bugs, resolving-merge-conflicts); productivity skills (handoff, teach, wait-what, writing-for-agents) |
| **skillmd.ai** | Skill authoring validation checklist, multi-domain skill structure, sequential workflow patterns, skill composition guidance |
| **agnt.gg "100 Best AI Agent Skills 2026"** | 12-category taxonomy: Development (15), Design (8), Data (8), Document Processing (7), Content (9), Security (8), Business/Marketing (9), Productivity (9), Communication (8), DevOps (8), Creative/Media (8), Enterprise (13) |
| **MCP Ecosystem Research** | Playwright MCP (Microsoft, accessibility-tree based, 22+ tools), Chrome DevTools MCP, GitHub MCP, Context7, Sentry MCP; MCP is the dominant tool-protocol standard |
| **Multi-Agent Orchestration Patterns** (2026) | Supervisor/manager pattern, peer-to-peer handoff, fan-out/fan-in scatter-gather, pipeline chaining; handoff protocol = target + context + instructions + metadata + auth + model_hint |
| **GitHub Agentic Workflows** (GitHub Blog, Feb 2026) | Continuous issue triage, PR triage with CODEOWNERS, Dependabot PR grouping, failure analysis from Actions logs, nightly test fixes |
| **Webhook Design Patterns** (agentndx.ai, 2026) | Webhook Designer skill: HMAC signature verification, idempotency keys, replay protection, dead-letter queue specs, retry semantics |
| **Intelligent Document Processing** (2026 landscape) | Document classification → OCR → NER extraction → validation → routing; invoice 3-way matching, contract clause extraction; multimodal vision LLMs replacing template-based extraction |
| **Code Execution Sandboxes** (2026) | E2B (Firecracker microVMs), Modal (gVisor), Cloudflare sandbox-sdk, OpenAI Codex Windows sandbox; this is platform infrastructure, not a skill |

### Key Trends Found

1. **Skills are workflow contracts, not tool wrappers.** The best skills encode *procedural knowledge* (when to do what, in what order, with what guardrails) rather than just listing APIs. The LLM already knows how to call an HTTP endpoint; the skill teaches it the domain-specific sequence and failure modes.

2. **Browser automation has matured.** Playwright MCP (Microsoft) is the default — accessibility-tree snapshots instead of screenshots, 22+ tools, cross-browser. But this is a *tool layer*, and workflow guidance (anti-bot, session management, form-filling reliability) is the skill-level opportunity.

3. **MCP is the standard protocol** for tool integration. The ecosystem has 1000+ MCP servers. But building MCP servers is a developer task (covered by mcp-server-builder); consuming them is a runtime concern.

4. **Multi-agent orchestration is architectural, not a skill.** Supervisor/handoff/fan-out patterns are system-design decisions, not reusable workflows that belong in a SKILL.md.

5. **Document intelligence is converging on multimodal LLMs.** Contract analysis, invoice extraction, receipt processing are increasingly done by vision-capable models reading documents directly — reducing the need for template/OCR-heavy skills.

6. **The skill ecosystem is dominated by integration skills.** Composio, Google Workspace CLI, and similar platforms sell "X-automation" skills (Slack, Gmail, HubSpot, Salesforce, Shopify, Stripe). These are API-integration wrappers, not workflow-methodology skills.

---

## 2. Advanced Patterns Catalog

| # | Pattern | What It Is | Industry Examples | Skillkit Coverage |
|---|---|---|---|---|
| 1 | **Browser automation / form filling** | Agent controls headless browser: navigate, click, type, screenshot, extract from JS-rendered pages | Playwright MCP (Microsoft), browser-use, Browserbase | ⚠️ Partial — platform has computer_use_tool + browser-use-automation; web-data-extractor (in progress) covers extraction. Interactive form workflows are tool-layer, not skill-layer |
| 2 | **MCP server creation** | Scaffold MCP servers from OpenAPI/API contracts | Anthropic official mcp-builder, FastMCP | ✅ Covered — `mcp-server-builder` (OpenAPI → Python/TS scaffold + validation) |
| 3 | **MCP client / consumption** | Discover, configure, and call MCP servers as a client | Any MCP host (Claude Desktop, Cursor, etc.) | ❌ Not a skill — this is runtime/platform infrastructure |
| 4 | **Sub-agent orchestration** | Task decomposition, parallel workers, handoff protocols, fan-out/fan-in | OpenAI Codex subagents, Microsoft Agent Framework, Loki Mode (37 agents) | ⚠️ Partial — `session-handoff`, `skill_chains.json`, `agent-designer`. Remaining patterns are architectural decisions, not reusable skills |
| 5 | **Code execution sandbox** | Isolated runtime for untrusted/generated code: microVMs, containers, WASM | E2B, Modal, Cloudflare sandbox-sdk, OpenAI Codex sandbox | ❌ Platform-provided — Doubao harness provides Bash/Python execution environment |
| 6 | **Git worktree / branch management** | Isolated worktrees for parallel feature work | obra/superpowers, Composio Skills | ✅ Covered — `git-worktree-manager` |
| 7 | **Changelog / release notes generation** | Convert commits to user-facing changelogs, categorize by type | Composio Awesome Skills | ✅ Covered — `changelog-generator` |
| 8 | **GitHub release management** | Semver bump determination, version coordination across packages, tag creation, GitHub Release publishing, breaking-change detection | lobehub github-release-management, lightspeedwp release.agent.md | ⚠️ Partial — `changelog-generator` covers notes; no full release workflow skill. But semver reasoning is LLM-native; git tag/push is CLI |
| 9 | **Issue triage automation** | Auto-label, route, prioritize incoming issues; group Dependabot PRs by risk | GitHub Agentic Workflows, aihero /triage, jstark518 issue-pipeline | ⚠️ Partial — `issue-tracker-sync` creates issues and generates reports; triage (reading incoming issues and categorizing) is LLM reasoning + API calls |
| 10 | **Systematic debugging** | Reproduce → isolate → hypothesize → test → fix; root-cause tracing | obra/superpowers /diagnosing-bugs, aihero /diagnosing-bugs | ✅ Covered — `debug-diagnoser` |
| 11 | **TDD enforcement** | Red-green-refactor loop before implementation | obra/superpowers, aihero /tdd | ✅ Covered — `tdd-guide`, plus `webapp-flow-tester`, `webapp-e2e-harness` |
| 12 | **Frontend design / UI aesthetics** | Break "AI slop" UI distributional convergence; design system philosophy before code | Anthropic official frontend-design skill (277K installs) | ✅ Covered — `frontend-design-director`, `layout-spec-auditor`, `frontend-component-lab` |
| 13 | **Natural-language-to-SQL** | Convert questions to parameterized SQL with safety guards | Agent-SQL-Pro, PostgreSQL connector | ✅ Covered — `sql-database-assistant`, `database-designer` |
| 14 | **Deep research** | Multi-source research: broad survey → deep dive → synthesis → citations | sanjay3290/ai-skills, agnt.gg #26 | ✅ Covered — `deep-research`, `web-search`, `lit-review` |
| 15 | **PDF document processing** | Extract text/tables, merge/split, fill forms, OCR scanned docs | Anthropic official pdf skill (32K+ downloads) | ✅ Covered — `pdf-pipeline` (merge/split/extract/meta/rotate + AcroForm probe + scanned detection). Form filling is NOT covered but is a minor extension |
| 16 | **DOCX / PPTX / XLSX generation** | Full Office document lifecycle with formatting preservation | Anthropic official skills (28K/22K/35K downloads) | ✅ Covered — `docx-writer`, `docx-template-fill`, `ppt-builder`, `excel-assistant` |
| 17 | **Invoice / receipt organization** | Extract vendor/amount/date, rename consistently, tax-ready summaries | Composio Awesome Skills | ✅ Covered — `invoice-organizer` |
| 18 | **Bank statement reconciliation** | Match transactions, flag discrepancies | (skillkit-native) | ✅ Covered — `bank-statement-reconcile` |
| 19 | **File organization / batch rename** | Intelligently organize files, find duplicates, consistent naming | Composio Awesome Skills | ✅ Covered — `file-organizer`, `batch-renamer` |
| 20 | **Webhook receiver design** | Inbound webhook handlers with HMAC verification, idempotency, replay protection, DLQ | agentndx.ai Webhook Designer | ❌ Not covered — but this is backend programming work; LLM can write Stripe/GitHub/Slack webhook handlers. Weak candidate |
| 21 | **CRM automation** (HubSpot/Salesforce) | Contacts, deals, pipeline, SOQL queries | Composio Awesome Skills | ❌ Not covered — requires specific CRM API integration; niche enterprise; not a workflow-methodology skill |
| 22 | **Payment automation** (Stripe) | Charges, subscriptions, refunds, invoices | Composio Awesome Skills | ❌ Not covered — requires Stripe API integration; niche |
| 23 | **E-commerce automation** (Shopify) | Products, orders, inventory, GraphQL | Composio Awesome Skills | ❌ Not covered — previously evaluated and rejected. Existing skills cover product-copywriter + image generation + SEO |
| 24 | **Email automation** (Gmail) | Send/reply, search, labels, threads, attachments | Composio Awesome Skills | ❌ Not covered — email writing is LLM-native; inbox management requires IMAP/SMTP platform integration |
| 25 | **Slack / Discord / Teams automation** | Messages, channels, reactions, workflow triggers | Composio Awesome Skills | ⚠️ Partial — `feishu-dingtalk-bridge` covers outbound notifications to Feishu/DingTalk/WeCom. Slack incoming webhooks are simple POSTs (LLM-native) |
| 26 | **Competitive ads extraction** | Extract competitor ads from ad libraries for intelligence | Composio Awesome Skills | ❌ Not covered — overlaps with web-data-extractor (in progress) |
| 27 | **Meeting behavioral analysis** | Speaking ratios, filler words, conflict patterns, action items beyond summary | Composio Awesome Skills | ⚠️ Partial — `meeting-notes` covers summaries/action items; behavioral analysis is LLM-native text analysis |
| 28 | **Autonomous security testing** | Penetration testing, web fuzzing, vulnerability exploitation | Shannon (XBOW), ffuf skill, Trail of Bits | ❌ Not covered — `security` pack covers secrets/PII/prompt-injection (defensive). Offensive security is highly specialized niche |
| 29 | **Threat hunting / Sigma rules** | Translate Sigma rules to SIEM queries, hunt for threats | jthack/threat-hunting-sigma | ❌ Not covered — very niche security operations |
| 30 | **Remotion programmatic video** | Natural-language → React-based video components | remotion/agent-skills | ❌ Not covered — `ai-video-pipeline` covers video creation via platform tools. Remotion is a specific framework for developers |
| 31 | **3D model generation** | Text/image → 3D models for games/AR/VR | OpenClaw Skills | ❌ Not covered — emerging but niche |
| 32 | **Scientific research databases** | ArXiv, PubMed, ChEMBL, clinical trials access | K-Dense scientific skills | ⚠️ Partial — `deep-research`, `lit-review` cover research methodology; specific database APIs are integration concerns |
| 33 | **n8n workflow automation** | Create/modify/debug n8n automations | haunchen/n8n-skills | ❌ Not covered — n8n is a specific platform; niche |
| 34 | **Calendly / scheduling automation** | Event types, bookings, availability sync | Composio Awesome Skills | ❌ Not covered — platform has lark-calendar for Feishu; external scheduling requires API integration |
| 35 | **Notion automation** | Pages, databases, blocks, comments | Composio Awesome Skills | ✅ Covered — `notion-workspace` |
| 36 | **Jira automation** | Issues, projects, sprints, JQL, workflow transitions | Composio Awesome Skills | ✅ Covered — `issue-tracker-sync` (Jira/Linear/GitHub) |
| 37 | **Sentry / Datadog monitoring** | Error monitoring, alert management, incident triage | Composio Awesome Skills | ⚠️ Partial — `incident-commander`, `runbook-generator`, `slo-architect`, `observability-designer` cover the methodology. Specific Sentry/Datadog API calls are integration concerns |
| 38 | **Vercel / deployment automation** | Deployments, domains, env vars, preview deployments | Composio Awesome Skills | ⚠️ Partial — `ci-cd-pipeline-builder`, `ship-gate` cover CI/CD methodology. Vercel-specific API is integration concern |
| 39 | **YouTube transcript extraction** | Fetch transcripts for summarization/analysis | tapestry-skills YouTube Transcript | ✅ Platform-covered — `doubao-video-extract` supports YouTube extraction |
| 40 | **Image batch processing / OCR** | Batch compress/resize/watermark/OCR from images | Composio Awesome Skills, image-enhancer | ⚠️ In progress — `image-batch-processor` being created |
| 41 | **Article / full-text extraction** | Clean article text from web pages, strip navigation/ads | tapestry-skills Article Extractor | ⚠️ In progress — `web-data-extractor` (being created) covers this |
| 42 | **Theme factory / brand consistency** | Apply consistent fonts/colors across artifacts | Composio Awesome Skills | ⚠️ Partial — `layout-spec-auditor`, `visual-style-anchor` cover design audits. Cross-artifact theme application is not explicitly a skill |
| 43 | **Kaizen / continuous improvement** | Identify waste, optimize processes, track metrics | NeoLabHQ context-engineering-kit | ❌ Not covered — this is management consulting methodology; LLM-native reasoning |
| 44 | **Ship-learn-next feedback loop** | Iterate based on outcomes, identify next steps | tapestry-skills | ❌ Not covered — LLM-native reasoning about priorities |
| 45 | **ADHD founder planner** | Neurodivergent-friendly productivity system | OpenClaw Skills | ❌ Not covered — niche personal productivity; LLM-native planning |

---

## 3. Gap Candidates (Passing the Filter)

After applying the strict four-filter test across all 45 patterns catalogued above, **no strong additional gaps emerge beyond the two already identified** (web-data-extractor, image-batch-processor).

Below are the only candidates that partially pass the filter, with honest assessment:

### Candidate A: Inbound Webhook Receiver Patterns

| Dimension | Assessment |
|---|---|
| **Scenario** | User needs to build an HTTP endpoint that receives webhooks from Stripe, GitHub, or Slack events. Must verify HMAC signatures, handle idempotency, respond with correct status codes, and route events to handlers. |
| **Why agent needs it** | Webhook signature verification is security-sensitive: getting HMAC comparison wrong (non-timing-safe, wrong header parsing, wrong secret handling) creates vulnerabilities. Each platform has a different header format: Stripe uses `Stripe-Signature: t=timestamp,v1=signature`, GitHub uses `X-Hub-Signature-256: sha256=hash`, Slack uses `X-Slack-Signature: v0:timestamp:signature`. The LLM may not get all three right from memory. |
| **What tools/operations** | HMAC verification code templates per platform, idempotency key extraction, replay protection timestamps, dead-letter queue pattern, retry/backoff specs. |
| **Suggested name** | `webhook-receiver-builder` |
| **Suggested pack** | `api-development` (currently 2 skills) |
| **Estimated complexity** | Low — 3 platform templates (Stripe/GitHub/Slack), each ~50 lines of reference code. |
| **Filter result** | ⚠️ **Weak pass.** Fails filter (a) on frequency: building inbound webhook receivers is a developer task, not a high-frequency user request. Fails filter (b) partially: the LLM knows HMAC generally, but per-platform header format differences are non-obvious. Fails filter (d) marginally: this is backend programming, and the 49-skill programming pack already covers API design/testing. **Recommendation: Low priority. Only add if webhook integration requests become frequent.** |

### Candidate B: PDF Form Filling

| Dimension | Assessment |
|---|---|
| **Scenario** | User has a PDF form (AcroForm) and needs to fill in fields with data, then flatten/save. |
| **Why agent needs it** | `pdf-pipeline` currently *probes* AcroForm fields but does not *fill* them. Field naming in PDFs is inconsistent (long internal names vs. readable labels), and flattening requires pypdf/pdfrw-specific patterns. |
| **What tools/operations** | Field listing script, field-mapping from user data to internal field names, fill-and-flatten workflow, save-as-new-PDF. |
| **Suggested name** | `pdf-form-filler` (or extend existing `pdf-pipeline`) |
| **Suggested pack** | `office-productivity` |
| **Estimated complexity** | Low — extension of existing pdf-pipeline skill. |
| **Filter result** | ⚠️ **Very weak pass.** This is a natural extension of an existing skill, not a new gap. The existing `pdf-pipeline` already probes fields; adding fill capability is incremental. **Recommendation: Extend pdf-pipeline when needed, do not create a standalone skill.** |

---

## 4. Rejected Candidates

Patterns that looked interesting but fail at least one filter:

| Pattern | Reason for Rejection |
|---|---|
| **Playwright/browser automation workflows** | **Platform-covered.** Doubao harness provides `computer_use_tool` + `browser-use-automation` skill. Web-data-extractor (in progress) covers data extraction. Interactive browser workflows are tool-layer operations, not workflow-methodology skills. |
| **MCP client / consumption patterns** | **Platform-native.** MCP clients are runtime infrastructure (Claude Desktop, Cursor, agent host), not skills. Building MCP servers IS covered by `mcp-server-builder`. |
| **Sub-agent orchestration / handoff protocols** | **LLM-native + existing coverage.** `session-handoff` covers session transfer. Fan-out/fan-in, supervisor patterns are architectural decisions, not reusable SKILL.md workflows. The LLM reasons about task decomposition naturally. |
| **Code execution sandbox** | **Platform-native.** Doubao harness provides Bash/Python execution in a VM sandbox. Sandbox implementation (Firecracker, gVisor) is infrastructure, not a user-facing skill. |
| **GitHub release management** | **LLM-native + partial existing coverage.** Semver determination from commits is reasoning. `changelog-generator` already covers release notes. Git tag/push is CLI. The full release workflow is a composition of existing skills + LLM reasoning. |
| **Issue triage / auto-labeling** | **LLM-native.** Reading an issue and categorizing/labeling it is reasoning. `issue-tracker-sync` already handles issue creation and reporting. Triage logic is not non-obvious domain knowledge. |
| **Dependency update / Dependabot management** | **Existing coverage + LLM-native.** `dependency-auditor` audits dependencies. Managing Dependabot PRs is CI/CD reasoning (group patches, test updates) that the LLM handles. |
| **ETL / webhook data ingestion** | **LLM-native.** Writing API ingestion code, webhook receivers, and data pipelines is programming work. `etl-builder` covers local batch ETL generation. The LLM writes requests/webhook code naturally. |
| **Contract analysis / clause extraction** | **LLM-native.** Reading a contract and identifying parties, dates, termination clauses is text comprehension — exactly what LLMs do. No deterministic tool workflow needed beyond document reading. |
| **Receipt processing beyond invoices** | **Existing coverage.** `invoice-organizer` already handles invoice/receipt extraction and organization. |
| **Email writing / inbox management** | **LLM-native + platform integration.** Email drafting is writing (covered by `internal-comms-writer` + content skills). Inbox management requires IMAP/SMTP integration — platform tool concern, not a skill. |
| **CRM automation (HubSpot/Salesforce)** | **Platform integration concern.** Requires specific CRM API OAuth and data models. Not a workflow-methodology skill; it's an API wrapper. Niche enterprise use case. |
| **Payment automation (Stripe)** | **Platform integration concern.** Requires Stripe API keys and billing domain. Niche. |
| **E-commerce platform operations (Shopify/淘宝)** | **Previously rejected.** `product-copywriter` + image generation + SEO skills cover content-side operations. Platform backend operations require API integration. |
| **Autonomous pentesting / offensive security** | **Too niche + high-risk.** The security pack covers defensive concerns (secrets, PII, prompt injection). Offensive security (50+ exploit types) is a specialized professional domain, not a general agent skill. |
| **Threat hunting / Sigma rules** | **Too niche.** SIEM/SOC operations. Not a general-purpose skill. |
| **Remotion programmatic video** | **Too niche + platform-covered.** `ai-video-pipeline` covers video creation. Remotion is a specific React framework for developers. |
| **3D model generation** | **Too niche.** Emerging but low-frequency. Not a common user request. |
| **Scientific research database connectors** | **Existing coverage + integration concern.** `deep-research` and `lit-review` cover research methodology. Specific database APIs (PubMed, ChEMBL) are integrations. |
| **n8n workflow automation** | **Too niche.** Specific platform. |
| **Calendly / scheduling** | **Platform-covered for Feishu (lark-calendar).** External scheduling requires API integration. |
| **Sentry / Datadog monitoring** | **Existing coverage + integration concern.** `incident-commander`, `runbook-generator`, `observability-designer` cover methodology. Specific API calls are integration. |
| **Meeting behavioral analysis** | **LLM-native.** Analyzing transcripts for speaking ratios/patterns is text analysis. `meeting-notes` covers summaries/action items. |
| **Competitive ads extraction** | **Overlaps with web-data-extractor (in progress).** |
| **Theme factory / cross-artifact branding** | **Existing coverage.** `layout-spec-auditor` and `visual-style-anchor` cover design consistency. Applying a theme is design work the LLM reasons about. |
| **Kaizen / continuous improvement methodology** | **LLM-native.** Management consulting reasoning, not a deterministic tool workflow. |
| **Travel planning / itinerary** | **Previously rejected.** LLM-native reasoning + deep-research covers it. |
| **Financial investment / stock analysis** | **Previously rejected + platform-covered.** High-risk regulated domain. Platform has doubao-stock-screening, doubao-daily-stock, doubao-earnings-analysis, etc. |
| **Health management** | **Previously rejected + platform-covered.** Medical safety concerns. Platform has doubao-medical-* skills. |
| **Slack/Discord/Teams messaging** | **LLM-native for simple messages.** `feishu-dingtalk-bridge` covers complex multi-protocol notifications. Slack incoming webhook is a simple POST — LLM handles it. |
| **Google Workspace automation** | **Platform integration concern.** Requires Google OAuth. Not a skill; it's an MCP server / API integration. |
| **CSV data summarization** | **LLM-native + existing coverage.** `excel-assistant` and data-ml-science pack cover data analysis. Dropping a CSV and getting stats is LLM reasoning over data. |
| **Natural language to SQL** | **Existing coverage.** `sql-database-assistant` covers this. |
| **D3.js / custom data visualization** | **Existing coverage.** `dataviz-studio` (dashboard-designer, chart-recommender) + `result-visualizer` cover visualization. |
| **Excalidraw / architecture diagrams** | **Existing coverage.** `arch-diagram` and `neural-net-draw` in ai-research-writing pack cover diagram generation. |
| **Accessibility auditing (axe-core)** | **LLM-native.** Writing axe commands and interpreting results is reasoning over tool output. Niche web dev task. |
| **SEO technical audit** | **LLM-native + existing coverage.** `seo-optimizer` covers content SEO. Technical SEO (sitemaps, structured data) is reasoning. |

---

## 5. Top Recommendations

### Honest conclusion: No strong additional gaps found beyond the two already identified.

The skillkit's 153 skills across 36 packs are remarkably comprehensive when combined with the Doubao Harness platform's native capabilities (lark-* suite, image/video/audio generation, web.fetch, computer_use_tool, browser automation, file operations, plus 60+ additional platform skills for finance, medical, ecommerce, marketing, academic research).

### Already identified and in progress:

| Priority | Skill | Status |
|---|---|---|
| P0 | `web-data-extractor` | Being created — structured web data extraction, anti-bot handling, pagination/login |
| P1 | `image-batch-processor` | Being created — batch compress/resize/watermark/OCR via Pillow |

### Weak candidates (monitor, do not build now):

1. **`webhook-receiver-builder`** — Low priority. Only if users frequently ask to build inbound webhook endpoints. Would be a small addition to the api-development pack (which currently has 2 skills). The core value is per-platform HMAC signature verification templates (Stripe/GitHub/Slack).

2. **PDF form filling (extend pdf-pipeline)** — Incremental enhancement. The existing `pdf-pipeline` skill already probes AcroForm fields; adding fill-and-flatten capability is a natural extension when a user asks for it, not a standalone skill.

### Why no other gaps:

The 49-skill programming pack covers the full software development lifecycle (planning → coding → debugging → testing → review → CI/CD → containers → infrastructure → security). The 18-skill content/writing pack covers the full content pipeline (research → outline → draft → edit → SEO → de-AI → platform publishing). The 10-skill office pack covers document creation (PPT/Excel/Word/PDF/EPUB). The 7-skill data/ML pack covers ETL → features → modeling → visualization. The 4 integration skills cover Notion, Feishu/DingTalk, Jira/Linear/GitHub, and cloud drives.

The remaining "skills" in the industry lists (agnt.gg Top 100, Composio, etc.) are predominantly:
- **API integration wrappers** (Slack, Gmail, HubSpot, Stripe, Shopify, Sentry, Datadog) — these are platform/MCP integration concerns, not workflow-methodology skills
- **LLM-native reasoning tasks** (debugging, architecture, code review, writing, summarization) — already covered or inherently LLM capability
- **Niche vertical tools** (pentesting, 3D generation, scientific databases, n8n) — low-frequency, not general-purpose

The skillkit has correctly focused on **workflow methodology** — the non-obvious, domain-specific sequences and guardrails that make agents reliable — rather than on **API wrappers** that are better handled by the platform's integration layer.
