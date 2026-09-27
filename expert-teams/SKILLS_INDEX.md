# 技能索引 - SKILLS_INDEX.md

> 本仓库共实装 **100 个 skill**（通用 14 + 团队专用 86）。
> 统一按归属团队登记；调用失败/未安装时自动回退通用经验，不阻塞。

## 目录结构
```
skills/                                 # 通用 skill（14 个，全团队共用）
teams/<team-name>/skills/               # 团队专用 skill（相对本仓库根）
```

> skill 目录即资产：每个 skill 是一个含 `SKILL.md` 的目录，任何 agent 按需读取对应 `SKILL.md` 即可使用，无需安装到任何特定产品的目录。

---

## 🔧 通用 skills/（14 个，全团队共用）

| 名称 | 位置 | 一句话用途 |
|------|------|------------|
| `web-search` | `skills/web-search/` | 免费联网搜索：SearXNG 主 + DuckDuckGo 备、24h 缓存、深度模式（融合版，含 search_client.py 与 4 份 references） |
| `deep-research` | `skills/deep-research/` | 多轮检索深度调研：查询分解、信源可信度评分、去重与结构化报告（含 research_agent.py 可执行流水线，依赖 web-search） |
| `security-scan` | `skills/security-scan/` | 单遍仓库安全审计：依赖 CVE、硬编码密钥、IaC 配置、轻量 SAST 风险清单。 |
| `deep-security-scan` | `skills/deep-security-scan/` | 多遍深度安全扫描：业务逻辑漏洞、越权/注入深挖、攻击面测绘与修复排序。 |
| `performance-profiler` | `skills/performance-profiler/` | Node/Python/Go 性能剖析：CPU/内存/IO 瓶颈、火焰图、k6/Artillery 压测（含剖析与示例代码库） |
| `ci-cd-pipeline-builder` | `skills/ci-cd-pipeline-builder/` | CI/CD 流水线设计：阶段规划、测试门禁、部署策略（融合版，含 pipeline_generator/stack_detector 脚本与平台决策库） |
| `frontend-app-builder` | `skills/frontend-app-builder/` | 前端应用脚手架：Vite/Next.js 目录结构、状态管理选型、路由与 API 层封装。 |
| `frontend-testing-debugging` | `skills/frontend-testing-debugging/` | 前端 E2E/组件测试：Playwright/Vitest 选择器策略、调试与 flaky test 治理。 |
| `api-design-reviewer` | `skills/api-design-reviewer/` | REST/GraphQL 设计评审：命名、状态码、分页版本化、错误格式与安全（融合版，含 api_linter/api_scorecard/breaking_change_detector 脚本） |
| `test-case-generator-v2` | `skills/test-case-generator-v2/` | 企业级测试用例生成：等价类/边界值/决策表设计、标准化模板与回归集分层。 |
| `uml-and-software-architecture-visualization` | `skills/uml-and-software-architecture-visualization/` | 架构/时序/类/流程图：PlantUML 与 Mermaid、C4 模型与图表选型规则。 |
| `accuracy-and-fact-check` | `skills/accuracy-and-fact-check/` | **P0 全团队**：交付前事实准确性核查，断言三级分级+证据强度五级，防幻觉，反例搜索与交叉计算。 |
| `cross-validation-guide` | `skills/cross-validation-guide/` | **P1 数学/学术/工程/数据**：数值结果用 ≥2 种独立方法交叉验证，量纲自检、边界反例、敏感性检验。 |
| `quality-gate-checklist` | `skills/quality-gate-checklist/` | **P0 全团队**：交付前 7 维质检门禁（完整性/一致性/可追溯/可复现/合规/版权/格式），H 级不交付。 |

---

## 📚 学术论文团队 academic-paper-team（7 个）

| 名称 | 位置 | 一句话用途 |
|------|------|------------|
| `paper-topic-selector` | `teams/academic-paper-team/skills/paper-topic-selector/` | 研究选题评分排序：novelty/feasibility/impact/buildability 四因子（融合版，含打分脚本与 lit-review 联动） |
| `journal-adapt` | `teams/academic-paper-team/skills/journal-adapt/` | 期刊投稿格式适配：venue 规则、页数估算、禁词与双盲检查（融合版，含 journal_adapt.py 校验脚本） |
| `lit-review` | `teams/academic-paper-team/skills/lit-review/` | PRISMA 文献综述与真实引文图：S2/arXiv 检索、趋势缺口综合（融合版，含 lit_review.py 与离线 mock 回退） |
| `figure-maker` | `teams/academic-paper-team/skills/figure-maker/` | 论文级图表闸门：矢量导出、色盲友好配色、字号坐标轴规范与 Matplotlib 模板。 |
| `model-formulator` | `teams/academic-paper-team/skills/model-formulator/` | 自然语言问题→数学模型规格：变量/约束/目标形式化（融合版，含规格化脚本，衔接 model-solver） |
| `model-solver` | `teams/academic-paper-team/skills/model-solver/` | LP/MIP/ODE/蒙特卡洛数值求解与收敛报告（融合版，含求解脚本，消费 model-formulator 规格） |
| `pdf-pipeline` | `teams/academic-paper-team/skills/pdf-pipeline/` | PDF 页级处理：合并/拆分/文本提取/元数据/AcroForm 探测（融合版，含 pdf_ops.py 操作脚本） |

---

## 🌐 全栈 Web 团队 fullstack-web-team（11 个）

| 名称 | 位置 | 一句话用途 |
|------|------|------------|
| `docker-development` | `teams/fullstack-web-team/skills/docker-development/` | Dockerfile 优化、compose 编排、多阶段构建与容器安全加固（含 compose_validator 等校验脚本与规则库） |
| `helm-chart-builder` | `teams/fullstack-web-team/skills/helm-chart-builder/` | Helm chart 脚手架、values 设计、模板模式与安全加固（含 chart_analyzer 脚本与 references） |
| `terraform-patterns` | `teams/fullstack-web-team/skills/terraform-patterns/` | Terraform 模块设计、state 管理、安全加固与 CI plan/apply（含 tf_module_analyzer 与规则库） |
| `github-actions-advanced` | `teams/fullstack-web-team/skills/github-actions-advanced/` | 高级 Workflow：矩阵构建、缓存、environment 保护、OIDC 免密与并发控制。 |
| `supabase-postgres-best-practices` | `teams/fullstack-web-team/skills/supabase-postgres-best-practices/` | Postgres 实战：索引选型、EXPLAIN 慢查询、RLS 策略、分区与 vacuum。 |
| `react-best-practices` | `teams/fullstack-web-team/skills/react-best-practices/` | React/Next.js 性能优化规则库（Vercel 工程规则 + references 全集，组件/数据获取/打包纪律） |
| `shadcn` | `teams/fullstack-web-team/skills/shadcn/` | shadcn/ui 规范：初始化、组件引入、主题暗色、react-hook-form+zod 表单与 a11y。 |
| `stripe-best-practices` | `teams/fullstack-web-team/skills/stripe-best-practices/` | Stripe 接入：Payment Intent、Webhook 签名校验、订阅生命周期与 Connect 分账。 |
| `observability-designer` | `teams/fullstack-web-team/skills/observability-designer/` | 可观测性三支柱、黄金信号与告警降噪（融合版，含 dashboard_generator/alert_optimizer 脚本与 Grafana 模板） |
| `slo-architect` | `teams/fullstack-web-team/skills/slo-architect/` | SLO/SLI/错误预算设计与评审（含 SLO designer、error-budget 计算器、multi-window burn-rate 脚本） |
| `kubernetes-operator` | `teams/fullstack-web-team/skills/kubernetes-operator/` | K8s Operator/自定义控制器与 CRD 设计（含 CRD validator、reconcile linter、capability auditor 脚本） |

---

## 📐 数学建模团队 math-modeling-team（2 个，已有勿动）

| 名称 | 位置 | 一句话用途 |
|------|------|------------|
| `math-modeling-guosai` | `teams/math-modeling-team/skills/math-modeling-guosai/` | 国赛（CUMCM）资料库：题型映射、模型速查、LaTeX 骨架与评审自查表。 |
| `math-modeling-selfcheck` | `teams/math-modeling-team/skills/math-modeling-selfcheck/` | 国赛自检闸门：思想纪律 + 思维强化，开工前/产出后强制逐项过单。 |

---

## 🧩 软件开发交付团队 software-dev-team（无独立 skill）

引用通用 skills/：`api-design-reviewer`、`test-case-generator-v2`、`uml-and-software-architecture-visualization`
（位置：`skills/api-design-reviewer/`、`skills/test-case-generator-v2/`、`skills/uml-and-software-architecture-visualization/`）

> 团队成员遵循「开工前 Glob 扫 `skills/` 目录」协议，命中即用、失败退回通用经验。

---

## 🎨 视觉设计团队 visual-design-team（6 个）

| 名称 | 位置 | 一句话用途 | 适配 Agent |
|------|------|------------|------------|
| `design-brief-writer` | `teams/visual-design-team/skills/design-brief-writer/` | 设计需求简报模板与拆解：目标/受众/风格/尺寸/交付物逐项对齐。 | visual-team-lead、visual-brand-identity-designer |
| `color-and-typography-guide` | `teams/visual-design-team/skills/color-and-typography-guide/` | 色彩与字体体系速查：配色策略、字体层级、版式网格与对比度规范。 | visual-color-theory-expert、visual-typography-expert |
| `poster-and-key-visual-templates` | `teams/visual-design-team/skills/poster-and-key-visual-templates/` | 海报与主视觉 KV 版式模板库：横/竖/方版构图、信息层级、留白与安全区。 | visual-poster-designer、visual-social-media-designer |
| `ecommerce-visual-checklist` | `teams/visual-design-team/skills/ecommerce-visual-checklist/` | 电商视觉自查清单：主图/详情页/长图的卖点层级、合规与转化率要点。 | visual-ecommerce-designer |
| `image-generation-prompt-guide` | `teams/visual-design-team/skills/image-generation-prompt-guide/` | AI 生图提示词工程：构图/光影/风格/负面词结构化写法与迭代策略。 | visual-illustrator、visual-poster-designer、visual-brand-identity-designer |
| `design-review-checklist` | `teams/visual-design-team/skills/design-review-checklist/` | 设计评审清单：视觉一致性、可读性、品牌契合、合规与交付规范逐项检查。 | visual-design-reviewer、visual-team-lead |

---

## ✍️ 内容写作团队 content-writing-team（6 个）

| 名称 | 位置 | 一句话用途 | 适配 Agent |
|------|------|------------|------------|
| `content-strategy-canvas` | `teams/content-writing-team/skills/content-strategy-canvas/` | 选题与策略画布：受众画像/内容定位/选题矩阵/差异化价值四象限。 | content-strategist、content-planner |
| `title-crafting-guide` | `teams/content-writing-team/skills/title-crafting-guide/` | 标题工程：钩子类型、数字/疑问/对比/痛点公式、A/B 测试与合规边界。 | content-title-expert、content-social-media-writer |
| `multi-platform-adaptation-guide` | `teams/content-writing-team/skills/multi-platform-adaptation-guide/` | 多平台改写适配：公众号/小红书/知乎/微博的字数、语气、标签与格式差异。 | content-multiplatform-adaptor、content-social-media-writer |
| `copywriting-framework` | `teams/content-writing-team/skills/copywriting-framework/` | 文案框架：AIDA/SCQA/PAS/FAB 等经典模型的适用场景与模板。 | content-copywriter、content-article-writer |
| `seo-writing-guide` | `teams/content-writing-team/skills/seo-writing-guide/` | SEO 写作：关键词布局、搜索意图匹配、内链结构、元描述与可读性优化。 | content-seo-writer、content-editor |
| `content-quality-checklist` | `teams/content-writing-team/skills/content-quality-checklist/` | 内容质检清单：事实核查/原创度/结构逻辑/合规敏感词/排版规范逐项过单。 | content-reviewer、content-editor |

---

## 🎬 视频制作团队 video-production-team（6 个）

| 名称 | 位置 | 一句话用途 | 适配 Agent |
|------|------|------------|------------|
| `video-script-template` | `teams/video-production-team/skills/video-script-template/` | 脚本结构模板：钩子/展开/行动号召三段式，含分栏表与时长配比。 | video-scriptwriter-director、video-short-form-expert |
| `storyboard-guide` | `teams/video-production-team/skills/storyboard-guide/` | 分镜指南：镜号/景别/运镜/画面/对白/时长/转场字段规范与构图要点。 | video-storyboard-artist、video-scriptwriter-director |
| `short-video-structure-guide` | `teams/video-production-team/skills/short-video-structure-guide/` | 短视频结构方法论：3 秒钩子/信息密度/完播曲线/互动引导与平台差异。 | video-short-form-expert、video-editor |
| `video-editing-guide` | `teams/video-production-team/skills/video-editing-guide/` | 剪辑方法论：节奏曲线/转场选择/音画同步/J-cut L-cut 与叙事剪辑。 | video-editor、video-animation-motion-designer |
| `caption-and-subtitle-guide` | `teams/video-production-team/skills/caption-and-subtitle-guide/` | 字幕规范：断句/字号/安全区/双语对照/敏感词合规与读屏速度。 | video-caption-subtitle-expert |
| `video-quality-checklist` | `teams/video-production-team/skills/video-quality-checklist/` | 成片质检清单：画面/音频/字幕/色彩/合规/导出参数逐项终检。 | video-quality-reviewer、video-team-lead |

---

## 📊 数据分析团队 data-analysis-team（5 个）

| 名称 | 位置 | 一句话用途 | 适配 Agent |
|------|------|------------|------------|
| `data-cleaning-guide` | `teams/data-analysis-team/skills/data-cleaning-guide/` | 数据清洗手册：缺失值/异常值/重复/格式统一/编码修复的标准流程与阈值。 | data-cleaning-engineer、data-python-engineer |
| `funnel-and-retention-analysis` | `teams/data-analysis-team/skills/funnel-and-retention-analysis/` | 漏斗与留存分析：转化漏斗拆解、同期群 Cohort、留存曲线与归因方法。 | data-analyst-funnel、data-bi-analyst |
| `ab-testing-guide` | `teams/data-analysis-team/skills/ab-testing-guide/` | A/B 实验设计：假设检验、样本量计算、显著性判定、SRM 检查与陷阱规避。 | data-experiment-designer、data-statistician |
| `metric-tree-and-indicator-guide` | `teams/data-analysis-team/skills/metric-tree-and-indicator-guide/` | 指标体系搭建：OSM 模型、北极星指标、一级/二级指标拆解与口径定义。 | data-bi-analyst、data-governance |
| `report-and-dashboard-template` | `teams/data-analysis-team/skills/report-and-dashboard-template/` | 报表与看板模板：日报/周报/月报结构、KPI 卡片、维度下钻与自动化规范。 | data-report-engineer、data-visualization |

---

## 📣 市场营销团队 marketing-team（5 个）

| 名称 | 位置 | 一句话用途 | 适配 Agent |
|------|------|------------|------------|
| `marketing-plan-framework` | `teams/marketing-team/skills/marketing-plan-framework/` | 营销计划框架：STP 定位、4P 组合、预算分配、KPI 设定与节奏排期。 | marketing-strategist、marketing-team-lead |
| `campaign-brief-template` | `teams/marketing-team/skills/campaign-brief-template/` | 活动简报模板：目标/受众/创意/渠道/预算/排期/风险逐项对齐。 | marketing-campaign-planner、marketing-campaign-executor |
| `brand-positioning-canvas` | `teams/marketing-team/skills/brand-positioning-canvas/` | 品牌定位画布：品类/差异点/信任状/品牌人格/口号的系统化推导。 | marketing-brand-pr、marketing-strategist |
| `growth-experiment-guide` | `teams/marketing-team/skills/growth-experiment-guide/` | 增长实验方法论：AARRR 漏斗、ICE 打分、实验闭环与增长黑客战术库。 | marketing-growth-hacker、marketing-data-analyst |
| `marketing-channel-matrix` | `teams/marketing-team/skills/marketing-channel-matrix/` | 营销渠道矩阵：各平台特性/受众/成本/转化路径对比与渠道组合策略。 | marketing-social-media、marketing-seo-sem、marketing-koc-manager |

---

## 🛒 电商运营团队 ecommerce-ops-team（5 个）

| 名称 | 位置 | 一句话用途 | 适配 Agent |
|------|------|------------|------------|
| `product-selection-guide` | `teams/ecommerce-ops-team/skills/product-selection-guide/` | 选品方法论：市场容量/竞争度/利润率/供应链/差异化五维评分模型。 | ecommerce-product-selector、ecommerce-market-research |
| `listing-optimization-guide` | `teams/ecommerce-ops-team/skills/listing-optimization-guide/` | Listing 优化：标题/关键词/五点描述/A+页面/主图视频的转化率优化规范。 | ecommerce-listing-optimizer、ecommerce-store-operator |
| `customer-service-sop` | `teams/ecommerce-ops-team/skills/customer-service-sop/` | 客服 SOP：售前咨询/售中跟进/售后退换/差评处理的标准话术与升级流程。 | ecommerce-cs-lead、ecommerce-review-manager |
| `pricing-strategy-guide` | `teams/ecommerce-ops-team/skills/pricing-strategy-guide/` | 定价策略：成本加成/竞品对标/心理定价/促销节奏/利润测算模型。 | ecommerce-pricing-strategist、ecommerce-data-analyst |
| `store-operations-checklist` | `teams/ecommerce-ops-team/skills/store-operations-checklist/` | 店铺运营清单：日常巡检/活动报名/库存预警/广告投放/数据复盘逐项过单。 | ecommerce-store-operator、ecommerce-supply-planner |

---

## 📦 产品管理团队 product-team（5 个）

| 名称 | 位置 | 一句话用途 | 适配 Agent |
|------|------|------------|------------|
| `prd-writing-guide` | `teams/product-team/skills/prd-writing-guide/` | PRD 撰写规范：背景/目标/用户故事/功能需求/交互逻辑/验收标准模板。 | product-prd-writer、product-manager |
| `user-research-guide` | `teams/product-team/skills/user-research-guide/` | 用户研究方法：访谈/问卷/可用性测试/用户画像/旅程图的执行与分析。 | product-user-researcher、product-experience-reviewer |
| `roadmap-and-prioritization` | `teams/product-team/skills/roadmap-and-prioritization/` | 路线图与优先级：RICE/MoSCoW/Kano 模型、版本规划与需求排序方法。 | product-roadmap-planner、product-team-lead |
| `product-metrics-guide` | `teams/product-team/skills/product-metrics-guide/` | 产品指标体系：DAU/留存/转化/LTV/NPS 等核心指标定义与分析框架。 | product-data-analyst、product-operations |
| `competitor-analysis-framework` | `teams/product-team/skills/competitor-analysis-framework/` | 竞品分析框架：功能矩阵/用户体验对比/商业模式/差异化机会识别。 | product-competitor-analyst、product-manager |

---

## 💰 财务会计团队 finance-team（4 个）

| 名称 | 位置 | 一句话用途 | 适配 Agent |
|------|------|------------|------------|
| `financial-reporting-guide` | `teams/finance-team/skills/financial-reporting-guide/` | 财务报告指南：三大报表勾稽关系、附注披露、会计准则适用与分析框架。 | finance-report-analyst、finance-accountant |
| `budget-and-forecast-template` | `teams/finance-team/skills/budget-and-forecast-template/` | 预算与预测模板：零基预算/滚动预测/差异分析/预算调整流程。 | finance-budget-planner、finance-team-lead |
| `tax-compliance-checklist` | `teams/finance-team/skills/tax-compliance-checklist/` | 税务合规清单：增值税/企业所得税/个税申报要点、优惠政策与风险点。 | finance-tax-advisor、finance-qa-reviewer |
| `cost-analysis-guide` | `teams/finance-team/skills/cost-analysis-guide/` | 成本分析手册：本量利分析/作业成本法/标准成本差异/降本路径。 | finance-cost-controller、finance-report-analyst |

---

## 👥 人力资源团队 hr-team（4 个）

| 名称 | 位置 | 一句话用途 | 适配 Agent |
|------|------|------------|------------|
| `jd-writing-guide` | `teams/hr-team/skills/jd-writing-guide/` | JD 撰写指南：职责描述/任职要求/薪酬区间/雇主品牌的结构化写法。 | hr-jd-writer、hr-recruiter |
| `interview-guide` | `teams/hr-team/skills/interview-guide/` | 面试评估指南：结构化面试/STAR 法则/胜任力模型/评分卡与偏见规避。 | hr-interviewer、hr-recruiter |
| `performance-review-framework` | `teams/hr-team/skills/performance-review-framework/` | 绩效管理框架：OKR/KPI 设定、360 评估、校准会议、绩效面谈与改进计划。 | hr-performance-manager、hr-team-lead |
| `onboarding-checklist` | `teams/hr-team/skills/onboarding-checklist/` | 入职清单：设备/账号/文档/导师/30-60-90 天计划与文化融入。 | hr-onboarding-designer、hr-employee-relations |

---

## ⚖️ 法律合规团队 legal-compliance-team（4 个）

| 名称 | 位置 | 一句话用途 | 适配 Agent |
|------|------|------------|------------|
| `contract-review-checklist` | `teams/legal-compliance-team/skills/contract-review-checklist/` | 合同审查清单：主体资质/权利义务/违约条款/争议解决/风险分级逐项核查。 | legal-contract-reviewer、legal-document-drafter |
| `privacy-compliance-guide` | `teams/legal-compliance-team/skills/privacy-compliance-guide/` | 数据隐私合规：个保法/GDPR 要点、数据分类分级、同意机制与跨境传输。 | legal-privacy-officer、legal-compliance-officer |
| `ip-protection-guide` | `teams/legal-compliance-team/skills/ip-protection-guide/` | 知识产权保护：商标/专利/著作权/商业秘密的申请策略与侵权应对。 | legal-ip-specialist、legal-document-drafter |
| `regulatory-watch-guide` | `teams/legal-compliance-team/skills/regulatory-watch-guide/` | 监管跟踪方法：法规监测/影响评估/合规整改/培训宣贯的闭环流程。 | legal-regulatory-watcher、legal-compliance-officer |

---

## 🌐 翻译本地化团队 translation-team（4 个）

| 名称 | 位置 | 一句话用途 | 适配 Agent |
|------|------|------------|------------|
| `translation-style-guide` | `teams/translation-team/skills/translation-style-guide/` | 翻译风格指南：信达雅标准、术语一致性、句式转换、标点与格式规范。 | translation-zh-to-en、translation-en-to-zh、translation-proofreader |
| `terminology-base-guide` | `teams/translation-team/skills/terminology-base-guide/` | 术语库管理：术语提取/审定/维护/复用流程与 CAT 工具集成。 | translation-terminologist、translation-localization-manager |
| `localization-checklist` | `teams/translation-team/skills/localization-checklist/` | 本地化清单：日期/货币/度量衡/文化禁忌/UI 适配/法律差异逐项检查。 | translation-localization-manager、translation-cultural-adaptor |
| `translation-qa-checklist` | `teams/translation-team/skills/translation-qa-checklist/` | 翻译质检清单：漏译/错译/术语不一致/格式错误/可读性逐项评分。 | translation-qa-reviewer、translation-proofreader |

---

## 🎓 教育培训团队 education-training-team（4 个）

| 名称 | 位置 | 一句话用途 | 适配 Agent |
|------|------|------------|------------|
| `curriculum-design-guide` | `teams/education-training-team/skills/curriculum-design-guide/` | 课程设计指南：教学目标/布鲁姆分类/内容模块化/教学法选择与评估对齐。 | education-curriculum-designer、education-team-lead |
| `quiz-and-exercise-generator` | `teams/education-training-team/skills/quiz-and-exercise-generator/` | 出题手册：填空/选择题型设计、大白话比喻解析、举一反三变式题生成。 | education-quiz-designer、education-tutor |
| `course-outline-template` | `teams/education-training-team/skills/course-outline-template/` | 课程大纲模板：章节结构/知识点拆解/课时分配/课件要点与作业设计。 | education-courseware-writer、education-lecturer |
| `learning-path-planner` | `teams/education-training-team/skills/learning-path-planner/` | 学习路径规划：能力模型/前置依赖/阶段目标/资源推荐与进度追踪。 | education-learning-path-planner、education-assessment-designer |

---

## 🎙️ 音频播客团队 audio-podcast-team（4 个）

| 名称 | 位置 | 一句话用途 | 适配 Agent |
|------|------|------------|------------|
| `podcast-script-template` | `teams/audio-podcast-team/skills/podcast-script-template/` | 播客脚本模板：冷开场/主题引入/分段讨论/金句设计/结尾 CTA 的结构。 | audio-scriptwriter、audio-host |
| `audio-editing-guide` | `teams/audio-podcast-team/skills/audio-editing-guide/` | 音频剪辑指南：降噪/均衡/压缩/响度标准化/剪辑节奏与播客导出参数。 | audio-editor、audio-sound-director |
| `voice-and-mic-guide` | `teams/audio-podcast-team/skills/voice-and-mic-guide/` | 配音与麦克风指南：发声技巧/录音环境/设备选型/电平控制与防喷。 | audio-host、audio-sound-director |
| `podcast-quality-checklist` | `teams/audio-podcast-team/skills/podcast-quality-checklist/` | 播客质检清单：响度/底噪/剪辑痕迹/内容完整性/平台规格逐项终检。 | audio-qa-reviewer、audio-reviewer |

---

## 🎮 游戏设计团队 game-design-team（4 个）

| 名称 | 位置 | 一句话用途 | 适配 Agent |
|------|------|------------|------------|
| `game-design-document-template` | `teams/game-design-team/skills/game-design-document-template/` | GDD 模板：核心循环/玩法机制/关卡结构/数值框架/美术风格的完整文档。 | game-gameplay-designer、game-team-lead |
| `game-balance-guide` | `teams/game-design-team/skills/game-balance-guide/` | 数值平衡指南：伤害公式/经济曲线/难度曲线/玩家体验与调参方法。 | game-balance-designer、game-economy-designer |
| `game-economy-guide` | `teams/game-design-team/skills/game-economy-guide/` | 游戏经济设计：货币体系/产出消耗/付费点/通胀控制与经济闭环。 | game-economy-designer、game-balance-designer |
| `game-qa-checklist` | `teams/game-design-team/skills/game-qa-checklist/` | 游戏 QA 清单：功能/Bug/性能/兼容性/体验/平衡性逐项测试与回归。 | game-qa、game-reviewer |

---

## 调用约定

```python
# 伪代码：skill 调用标准模式
def use_skill(skill_id: str, team_context: str = None, fallback: bool = True):
    try:
        # 1. 优先加载团队专用 skill
        if team_context:
            load_team_skill(team_context, skill_id)
        # 2. 回退用户级/全局 skill
        load_skill(skill_id)
        return execute_skill(skill_id)
    except SkillNotFound:
        if fallback:
            log(f"[Skill Fallback] {skill_id} 未安装，退回通用经验")
            return generic_experience()
        raise
```

### 调用优先级
1. **Team-lead 指定** → 成员必须按指定 skill 执行
2. **成员自查** → Phase 开工前扫描本列表，关键词匹配（含 `team_context`）
3. **无匹配** → 退回通用经验，不阻塞

---

## 维护规则
- 新增 skill → 必须在此表登记（名称/位置/一句话用途）
- 废弃 skill → 标记 `DEPRECATED`，保留 90 天
- 团队专用 skill → 仅在对应团队目录，不污染全局 `skills/`
- 总数口径：本仓库统一为 **100 个 skill**，新增/删除时同步更新顶部数字
