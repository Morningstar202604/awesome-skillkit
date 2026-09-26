
---

## 七、逻辑漂移 / 思维漂移 / 步骤漂移 / 内容漂移（深度层）

> 用户追加要求：不止数据漂移，还要检查"人顺着使用情景往下推"时，文件内/文件间是否
> 逻辑连贯、步骤完整、内容完整。本节为深度层审查结果。

### 七.1 通过项（深度层无缺陷）

| 检查维度 | 方法 | 结果 |
|---|---|---|
| 链路位置段引用完整性 | 23 个含"链路位置"段的 skill，提取全部引用的 skill 名 | ✅ 全部真实存在，无死链 |
| 链路方向一致性 | A 说"下游=B"则 B 应回指"上游=A"（或至少不矛盾） | ✅ 0 处矛盾 |
| 23 条链路语义连贯性 | 逐条精读 education/memory/paper/writing 域的链路段 | ✅ 上游/下游/平行叙述自洽，符合"人怎么用"的推演 |
| 工作流步骤 vs 失败处置表覆盖 | 有"若失败"分支的 skill 是否都有"失败处置表"章节 | ✅ 0 缺失 |
| SKILL.md 引用的 scripts/*.py 存在性 | 提取全部 scripts/ 引用，逐文件验证 | ✅ 唯一命中是 humanize-rewriter 引用 ai-trace-auditor 的 trace_scanner.py（跨 skill 共享，脚本在 ai-trace-auditor/scripts/ 下真实存在，非断链） |
| chains.json 的 `?` 标记 | 18 处可选步骤带 `?` | ✅ 设计如此（可选路径），非缺陷 |

### 七.2 发现的真实漂移（域归属层）

**核心发现：物理目录域、frontmatter `category`、`skill_chains.json` 的域名 三方不一致。**

这不是"数据漂移"（数字过期），而是**逻辑漂移**（分类体系本身不统一），会影响使用
情景下"人往哪走"的判断：

| skill | 物理目录 | frontmatter category | chains.json 归入域 | site.json 呈现域 | 漂移 |
|---|---|---|---|---|---|
| `music-generation` | `skills/scenarios/` | `media-generation` | **`music` 域**（独立域，仅 1 链 bgm） | `scenarios` | ⚠️ 物理在 scenarios，chains 说 music |
| `excel-assistant` | `skills/scenarios/` | `office-productivity` | **`office` 域** | `scenarios` | ⚠️ 物理在 scenarios，chains 说 office |
| `meeting-notes` | `skills/scenarios/` | `office-productivity` | **`office` 域** | `scenarios` | ⚠️ 同上 |
| `resume-tailor` | `skills/scenarios/` | `office-productivity` | **`office` 域** | `scenarios` | ⚠️ 同上 |
| `internal-comms-writer` | `skills/writing/` | `office-productivity` | **`office` 域** | `writing` | ⚠️ 物理在 writing，chains 说 office |
| `image-generation` | `skills/video/` | `media-generation` | `video` 域 | `video` | 一致 |
| `ai-baby-podcast` | `skills/video/` | `viral-entertainment` | `video` 域 | `video` | 一致 |

**根因分析**：
- `build_site.py:106` 用 `rel.split("/")[0]`（物理路径第一层）做 `domain` → site.json 呈现 `scenarios`/`writing`
- `skill_chains.json` 的域名用**功能语义**（`music`、`office`、`media-generation`）→ 把 4 个 scenarios 的 skill 归到 `music`/`office` 域
- 于是"人在网站上按域筛选时看到 scenarios 域有 music-generation，但技能链（chains.json）说它属于 music 域"——**两处入口给出不同答案**，这就是逻辑漂移。

**影响**：
- 用户按"域"筛选时，site 的 `scenarios` 域会出现 4 个本该属于 office/music 的技能
- 反之，`music` 域（chains.json 声明的独立域）在 site 上**没有独立的域卡片**（因为 build_site 按物理路径建域，物理上没有 `skills/music/` 目录）
- 这是"文件间不连贯"：site 的域划分 vs chains.json 的域划分 vs 物理目录 三方不一致

**修正建议（三选一）**：
1. **统一按物理目录**：把 `skill_chains.json` 的 `music` 域改为 `scenarios` 下的子域，`office` 域去掉对 scenarios 下 4 个 skill 的声明（或把 4 个 skill 物理移到 `skills/office/`）
2. **统一按 category**：改 `build_site.py` 用 frontmatter `category` 做 domain 而非物理路径第一层
3. **最简**：接受"scenarios 是物理容器域，office/music 是功能语义域"的双层设计，但**在 docs/SKILL-STANDARD-v2.md 明确写清这个双层规则**，消除歧义

### 七.3 `scenarios` 物理域是"幽灵域"（不在 chains.json 18 域中）

- `scenarios` 作为物理目录存在于磁盘（含 4 个 skill），但 `skill_chains.json` 的 18 域里没有 `scenarios`
- 这意味着"人在 chains.json 里找不到 scenarios 域"——它是一个**没有链路归属的物理容器**
- 与七.2 是同一个根因：物理域 vs 功能域的双层不一致

### 七.4 文件内部完整性（逐文件）

已读代表文件（article-drafter / article-outliner / content-editor / ai-trace-auditor / 
humanize-rewriter / internal-comms-writer / personal-voice-profile / seo-optimizer / 
cnblogs-skill / zhihu-content-manager / batch-renamer / file-organizer / format-converter / 
task-scheduler / memory-manager / skill-linter / skill-finder / knowledge-graph-builder /
storyboard-designer / video-script-writer / campaign-designer）全部通过：
- 六要素（输入→自检→工作流→I/O→交付→失败处置→参考）闭合
- 工作流每步有"预期 + 若失败"分支
- 失败处置表覆盖所有"若失败"场景
- 无内容截断、无未闭合代码块、无字段臆造、无前后矛盾

**结论：文件内部无内容漂移。漂移全部在"文件间/域层"——即三方分类体系（物理/category/chains）不一致。**

---

## 八、综合修复优先级（更新）

| 优先级 | 问题 | 类型 | 位置 |
|---|---|---|---|
| P1-新 | 域归属三方不一致（物理/category/chains） | 逻辑漂移 | `build_site.py:106` + `skill_chains.json` + 4 个 scenarios skill |
| P2-1 | DEPLOY-SITE.md 数字过期 | 数据漂移 | 112/27/12/39 → 143/36/18/58 |
| P2-2 | site/index.html 静态数字过期 | 数据漂移 | 113/112 → 143/36/18 |
| P2-3 | FULL-TEST-REPORT.md 历史快照未标注 | 数据漂移 | 顶部加"快照"说明 |
| P3-1 | CHANGELOG cnblogs 死链描述与现状不一致 | 记录勘误 | 补"已修复"口径 |
| P3-2 | 跨 skill 引用约定未文档化 | 文档补充 | SKILL-STANDARD-v2.md 加一条 |

**P1-新（域归属不一致）是本次深度审查的核心发现，比数据漂移更严重——它会在"人使用情景"中造成"按域筛选找错地方"的真实困惑。**

## 八、GAP-PLAN 补齐:2 个安全自扫描器(2026-09-19)

`docs/SKILL-GAP-PLAN.md` 计划中 19 个新增技能(17 已落地)+ 2 个安全附加项,
本轮把最后 2 个缺失项补齐,均为 self-authored、纯 Python、无网络依赖:

| 技能 | 位置 | 能力 | 实测 |
|------|------|------|------|
| `pii-redactor` | `skills/programming/security/` | 检测 8 类 PII(身份证/银行卡/手机号/邮箱/社会信用代码/IP 等),默认 `--dry-run` 只报告,`--redact -o` 输出脱敏版(源文件不改) | 身份证 `110101199003078518` 命中 id_card 而非 credit_code;坏校验位身份证漏过;源文件永不改动 ✓ |
| `prompt-injection-guard` | `skills/programming/security/` | 7 类注入模式,加权 0-100,输出 clean/low/medium/high/critical 五档 JSON;间接注入(`<tool_result>` 包装)额外加权 | benign→clean(0);注入样例→critical(90, 3 hits);indirect→low(40) ✓ |

**登记位置(四处同步)**
- `packs/security/pack.json`:skills[] 新增 2 条(source: self-authored),description/description_zh 更新
- `skills/skill_chains.json`:programming domain skills[] 在 `secrets-vault-manager` 后插入 2 个
- `manifest.json`:security pack 4 skills(size_kb 52→68,sha256 由 build.py 回写)
- `CHANGELOG.md`:[Unreleased] 段记录 2 技能落地

**重建 + 门禁**
- `python3 tools/build_site.py` → 145 skills / 36 packs / 18 domains / 58 chains(v0.19.0)
- `python3 tools/validate_skills.py` → 145 skills,0 errors,0 warnings,PASSED
- `python3 build.py` → `dist/security.zip`(4 skills,~68 KB)

至此 GAP-PLAN 全部 19+2 项清零。

## 九、基础/前端/办公缺口补齐：5 个新技能（2026-09-20）

头脑风暴结论（对照 2026 头部开源技能生态 mattpocock/skills、ECC、anthropics/skills、
santifer/career-ops、awesome 目录）：仓库强在"能力"（145 个），缺的是
**基础办公（Word/求职）、前端工程、网页 e2e** 三块；按"模型原生能做的不配
skill、需要领域知识/平台规则/离线可复现的才配"筛完，落地 5 个（均改造自明星
开源项目、离线可测、dry-run 默认、凭证走 env、零拷贝）：

| 技能 | 落域 | 改造来源 | 落 pack |
|------|------|----------|---------|
| `docx-template-fill` | office | docx-writer 补强方向（独立成技能，避免重复） | office-productivity |
| `frontend-component-lab` | design | mattpocock frontend-design + ECC frontend-patterns | visual-design-studio |
| `webapp-e2e-harness` | programming/testing | anthropics webapp-testing | tdd |
| `career-ops-lite` | office | santifer/career-ops（MIT，裁剪无网络版） | office-productivity |
| `session-handoff` | meta | mattpocock handoff | skill-forge |

**判定原则记录**：用户提出"基本 Word / 各种网站 / 前端设计"缺。筛选后：
- Word"排版"模型能做→不配；"模板填写/批注修订"模型裸做易翻车→配（docx-template-fill）
- "各种网站逐个"无底洞且多数搜索+模型即可→不配；通用 e2e 方法论→配（webapp-e2e-harness）
- 前端"审美"模型够用→不配；"工程规范/设计 token/选择器纪律"→配（frontend-component-lab）
- career-ops 原要 Playwright 登录态→裁剪为纯文本评分（合规 + 离线）

**重建 + 门禁**：build_site.py → 150 skills / 36 packs / 18 domains / 58 chains；
validate_skills.py → 150 skills 0 err 0 warn PASSED；build.py 回写 manifest（5 pack size_kb/sha256 对齐）。
5 个脚本全部独立干跑通过（fill/scaffold/e2e/score/handoff）。

至此仓库 150 技能；缺口补齐策略：只补"真能用 skill、且模型原生做不到"的地方。

## 十、死流程补齐：3 个"固定步骤"技能（2026-09-20）

skill 本质校准：skill 应封装**人的固定/死步骤、易漏、且模型不会主动做**的重复劳动
（报销归档、银行对账、周报等），而非审美/判断/自由创作（那些要放大 AI，不配 skill）。
据此落地 3 个"死流程"技能（全离线可测、dry-run 默认、凭证走 env、零拷贝、移动不删除可回滚）：

| 技能 | 落域 | 能力 | 实测 |
|------|------|------|------|
| `weekly-report-generator` | meta（skill-forge pack） | `git log --since=N天` + `git diff --stat` 自动填"做了什么"段，留卡点/下周占位；`--input report.json` 结构化输入 | 拉真实 git 提交渲染三段周报 ✓ |
| `invoice-organizer` | tools（toolsmith pack） | 散乱发票按 `<YYYY-MM>/<类别>/` 归档 + 台账 CSV；DEFAULT_RULES 正则（餐饮/交通/住宿/办公/通讯/发票/未分类）；`shutil.move` 不删除可回滚；`--apply`/`--map-json` | 测试文件正确分到 2026-08/办公、2026-09/交通、2026-09/餐饮、2026-09/发票 ✓ |
| `bank-statement-reconcile` | tools（toolsmith pack） | 银行流水 CSV vs 账单 CSV 按金额±0.01+同月+可选对手方匹配，出 matched/unmatched_stmt/unmatched_bill + 匹配率；自动识别列；无网络无凭证 | 流水3/账单3 匹配2、各 unmatched1、匹配率 66.7% ✓ |

**登记位置（四处同步）**
- `packs/skill-forge/pack.json`：skills[] +`weekly-report-generator`
- `packs/toolsmith/pack.json`：skills[] +`invoice-organizer` +`bank-statement-reconcile`
- `skills/skill_chains.json`：meta 域 +`weekly-report-generator`、tools 域 +2；新增链 `expense_filing [invoice-organizer, bank-statement-reconcile?]`、`weekly_status [weekly-report-generator]`
- `manifest.json`（skill-forge / toolsmith pack，size_kb/sha256 由 build.py 回写）、`CHANGELOG.md`[Unreleased]

**重建 + 门禁**
- `python3 tools/build_site.py` → 153 skills / 36 packs / 18 domains / 60 chains（v0.19.0）
- `python3 tools/validate_skills.py` → 153 skills, 0 errors, 0 warnings, PASSED
- `python3 build.py` → `dist/skill-forge.zip`（5 skills, ~52 KB, sha256:535b6ce44b98）、`dist/toolsmith.zip`（6 skills, ~61 KB, sha256:ab1e0143b796）

至此仓库 153 技能。补齐策略一贯：只封装"固定步骤、易漏、模型裸做易翻车"的死流程，
不约束 AI 自由发挥。

## 十一、验证型补齐：agent-eval-harness（2026-09-20）

纪律层"放大 AI 价值而非限制"的唯一保留候选落地：`agent-eval-harness`。
它不做约束类（grill/triage/强制 TDD 均判为 2026 模型原生能力，不配），
只做**验证型**——把"agent 行为对不对"量化成 0-100 分，让"改 prompt 后悄悄退化"可回归、可 CI 门禁。
本质仍是固定可规定流程（验证/回归），与 e2e（测"能不能跑通"）互补（测"对不对"）。

| 技能 | 落域 | 能力 | 实测 |
|------|------|------|------|
| `agent-eval-harness` | meta（tdd pack） | 5 维度（format/grounding/no_hallu/consistency/safety）加权 0-100 + pass/fail/warn 判定 + 失败维度明细；默认离线规则评分，`expects.evidence` 防幻觉、`forbidden` 让危险操作扣分；模式 B 生成 LLM-as-judge 评审 prompt（只产文本、不替调模型、凭证走 env） | case0→pass(100)、case1→warn(75,grounding 降)、case2→warn(67.5,safety 命中 `rm -rf /`+`删除生产库`) 三档判定全正确 ✓ |

**判定原则记录**：用户明确"不要来一堆没用的东西限制 AI 发挥，要尽最大可能发挥 AI 价值"。
据此纪律层只留验证型。本技能把验证标准写死成脚本（确定性、可对 CI 出退码），
正是 skill 该干的固定步骤活，而非让模型自由发挥。

**登记位置（四处同步）**
- `packs/tdd/pack.json`：skills[] +`agent-eval-harness`
- `skills/skill_chains.json`：meta 域 +`agent-eval-harness`；新增链 `agent_eval [agent-eval-harness]`、`agent_eval_gate [webapp-e2e-harness?, agent-eval-harness, ci-cd-pipeline-builder?]`
- `manifest.json`（tdd pack，size_kb/sha256 由 build.py 回写）、`CHANGELOG.md`[Unreleased]

**重建 + 门禁**
- `python3 tools/build_site.py` → 154 skills / 36 packs / 18 domains / 62 chains（v0.19.0）
- `python3 tools/validate_skills.py` → 154 skills, 0 errors, 0 warnings, PASSED
- `python3 build.py` → `dist/tdd.zip`（4 skills, ~76 KB, sha256:a80be214e00a）

至此仓库 154 技能；纪律层候选清零（仅保留"放大价值"的验证型）。
