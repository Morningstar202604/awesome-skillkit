# awesome-skillkit 专家评审与开发路线图

> 评审日期：2026-08-25 ｜ 对象版本：v1.6.2 (commit 4544fa4)
> 评审形式：模拟 67 人联合评审团 —— 由战略产品(10)、工程质量(9)、安全合规(8)、生态分发(9)、内容社区(8)、商业化(7)、数据度量(6)、国际化法务(5) 八个工作组 + 终审委员会(5) 组成。
> 结论基于：仓库全量勘察（407 文件、52 个 SKILL.md、174 个单测逐一核对）+ 2026 年 8 月公开市场情报。

---

## 一、执行摘要

**一句话裁决：这个项目的价值不在"技能多"，而在"有一块别人没有的硬知识"。当前最大的风险是这块硬知识被 33 个大路货淹没，且工程底线（CI、安装器、引用完整性）存在塌方点。**

三个核心判断：

1. **市场已经变了**。Agent Skills 自 2025-10 发布、2025-12 成为跨厂商开放标准（agentskills.io），截至 2026-06 已有约 40 个兼容产品（Claude Code、Codex、Cursor、Gemini CLI、Copilot、OpenCode…）。**分发已不是瓶颈，信任才是**：公开技能平均质量分仅 6.2/12（SkillsBench，47150 样本），36% 的被测技能含提示注入（Snyk ToxicSkills）。行业共识：H2 2026 的战场是"质量策展 + 安全验证"，不是目录规模。
2. **本项目真正的资产只有一块**：18 个中文内容平台发布技能（知乎/微信/CSDN/B站/小红书等）。其中 zhihu-content-manager 的 Draft.js 坑位图、编码陷阱、API-vs-UI 行为差异是一手踩坑知识，全市场无竞品覆盖——包括腾讯 SkillHub（10.7 万技能的横向市场）也不做这个纵深。而占数量 64.7% 的上游搬运技能（alirezarezvani/claude-skills, MIT）在原仓公开可得，对本项目零增值。
3. **工程底线有四个塌方点**（详见 §3.2）：访问令牌明文泄漏（P0）、Windows 安装器路径 bug（直接击穿"30 秒上手"卖点）、多个技能引用不存在的脚本（空壳交付物）、174 个单测零自动执行。

**推荐战略：从"场景包超市"收缩为"中国内容平台自动化技能的权威来源"（垂直第一），以信任基建（验证器 + 校验和 + 门禁）为外壳，以上游技能降级为兼容层为代价。**

---

## 二、市场格局（生态分发组，2026-08 快照）

### 2.1 竞争地图

| 阵营 | 代表 | 规模 | 模式 | 对本项目威胁 |
|---|---|---|---|---|
| 官方策展 | Anthropic 官方目录 | 小 | 人工精选、安全已验证 | 低（不做中国平台） |
| 体量派 | SkillsMP | ~190 万（GitHub 抓取） | 无审核 | 低（噪音市场） |
| 分发管道 | Skills.sh（Vercel） | 数十万 | `npx skills add` npm 式安装 | **高（管道标准制定者）** |
| 中国横向市场 | SkillHub（skillhub.cn，腾讯云系） | 10.7 万 | 三线安全审核流水线、企业专区、按调用结算 | **中高（可能做垂直包）** |
| 企业自建 | 科大讯飞 SkillHub 等 | 私有化 registry | RBAC + 审计 | 低 |
| 质量策展 | Agentman 等 | ~90 个 | 从业者手写、生产级 | 中（模式相同但不懂中文平台） |
| Awesome 列表 | karanb192/awesome-claude-skills（13k★）等 | 50-200 个 | 社区索引 | 中（流量入口） |

### 2.2 关键行业数据（决策依据）

- 精选优质技能可使 agent 任务通过率 **+16.2 分**；但公开技能均值仅 6.2/12 → " reviewed top quartile" 是唯一有价值的位置。
- **聚焦胜过堆料**：一次任务加载 2-3 个针对性技能 +18.6 分；单体大杂烩技能反而 -2.9 分 → 本项目"14 包 51 技能全家桶"的分发形态需要反思。
- 安全成为采购门槛：平均每技能 6.3 个问题；不能证明安全的目录将丢失企业买家。
- 结构化编排 > 平铺调用（AgentSkillOS, arXiv 2603.02176）：本项目自研的 cross-post-orchestrator 恰好踩在学术验证的方向上。

### 2.3 空白点（本项目的立足之地）

没有任何一个主流目录/市场拥有"微信公众号、知乎、CSDN、掘金、B站、小红书、头条、百家号、微博、豆瓣、简书、V2EX、SegmentFault、OSChina"发布的**可执行**自动化知识。西方竞品不碰（不了解平台），中国横向市场不做纵深（SkillHub 是货架不是知识库）。这是结构性机会。

---

## 三、项目体检报告

### 3.1 优势（终审委员会确认）

| # | 优势 | 证据 |
|---|---|---|
| S1 | 中文平台暗知识壁垒 | zhihu-content-manager 14KB：Draft.js 空段剥离、Latin-1 乱码对策、回答必须走 PUT API 而 UI 不保存、删除必须 UI（API 403）、90s 缓存、反爬 40362 处置、A-D 质量评级、自带 lint 脚本 + 单测 |
| S2 | 诚实的安全范式 | 全线默认 dry-run、凭据只走环境变量、端点标 VERIFY BEFORE USE、`*.local.json` 构建层强制排除、v1.3.0 曾彻底清除个人账号数据 |
| S3 | 元数据三方零偏差 | manifest.json ↔ 14 pack.json ↔ 51 磁盘技能完全一致，无孤儿、无死链；52/52 frontmatter 合规 |
| S4 | 内嵌测试文化 | 21 个测试文件、174 个用例随技能分发；`_common` 共享库消除发布脚本重复轮子 |
| S5 | 免依赖构建体系 | build.py 纯 stdlib、自动感知 `_common` 依赖打包、build.sh 语义镜像 |

### 3.2 问题清单（按严重度）

#### P0 — 必须立即处理
- **[SEC-01] 访问令牌明文泄漏**：`.git/config` origin URL 内嵌推送令牌（`https://badhope:<token>@gitcode.com/...`）。任何拿到工作目录（打包/截图/备份）的人即获推送权限。**处置：立即在 GitCode 吊销轮换该令牌；改用 credential manager；对历史无影响但令牌已在本对话中出现过，视为已暴露。**

#### P1 — 两周内修复
- **[ENG-01] Windows 安装器路径 bug（已复核）**：install.ps1:19-25 把每个 zip 解压到 `$Target\<zip名>\` 子目录，产生 `~/.claude/skills/code-review/code-reviewer/SKILL.md` 双层嵌套；Claude Code 约定是单层 `~/.claude/skills/<skill>/SKILL.md`（install.sh 是平铺的，两者不一致）。Windows 用户一键安装后技能不可被发现。
- **[ENG-02] 技能引用完整性破损（已复核抽样）**：
  - performance-profiler：Quick Start 引用 `scripts/performance_profiler.py`，scripts/ 目录不存在；
  - runbook-generator：同病，整包仅 2 文件；
  - ship-gate：三处引用 `references/checks.md` 不存在；
  - sql-database-assistant 缺 schema_explorer.py；skill-tester 引用根目录 `audit_skills.py` 不存在；observability-designer 残留已迁移的 slo_designer.py 引用。
- **[ENG-03] 零 CI/零 lint/零 runner**：174 个单测无任何自动执行机制。v1.3.0 曾有 skill-quality.yml，随后"drop GitHub remnants"时连根删除且未在任何镜像侧补替代。质量回归纯靠人肉。
- **[PROD-01] 定位稀释**：64.7% 的技能是上游原样拷贝（零增值），README 头图式的"14 场景包"叙事把唯一的差异化资产（content-publishing）埋在第 15 个位置。

#### P2 — 一个版本内解决
- **[SUP-01]** dist 不入库导致 manifest 的 `file:` 全部指向不存在路径、`size_kb` 不可核验；无 sha256/签名。
- **[GOV-01]** 版本号只活在 manifest.json；中间 6 个版本无 git tag；CHANGELOG 承诺 SemVer 但未执行。
- **[GOV-02]** 上游 MIT 合规依赖 README/manifest 集中署名，33 个技能目录内基本未保留版权头。
- **[DOC-01]** manifest 中文描述"豆瓣"重复出现两次；frontmatter 风格三种并存（引号/metadata 字段不一）。
- **[BUS-01]** 单人维护、8 天冲刺提交（v1.2→v1.6.2 一天跳 4 版），bus factor = 1。

---

## 四、战略裁决（终审委员会）

> **[2026-08-25 更新]** 本节"路线 C 中国内容平台垂直"结论已被创始人裁定扩展为**通用场景工作流库**战略，现行版本见 `docs/DIRECTION-V2.md`；编写规范见 `docs/SKILL-STANDARD-v2.md`。本节的 v1.6.3/v1.7 工程修复路线继续有效。

三条候选路线：

| 路线 | 描述 | 判决 |
|---|---|---|
| A. 大而全技能超市 | 与 SkillsMP/SkillHub 拼广度 | **否决**。无基础设施、无网络效应、单人维护拼不过平台方；SkillsBench 证明堆料负收益（-2.9 分） |
| B. 通用质量策展层 | 学 Agentman 做"reviewed top quartile" | **否决**。赛道拥挤（Anthropic 官方、Vercel、腾讯都在做），且本项目对英文编程技能没有策展优势 |
| **C. 垂直纵深：中国内容平台自动化权威** | 收缩到 content-publishing，做成"发布到中文互联网"的事实标准 | **通过（4:1）**。独占资产已在手、竞品结构性缺位、知识难复制（每条都是踩坑换来的）、天然匹配 GitCode/Gitee 分发渠道 |

**配套动作：上游 33 技能降级为"basics 兼容包"，保留但不作为门面**——它们负责引流和完整性，content-publishing 负责定位和口碑。

### 北极星指标
> **"一个自媒体运营者从安装到成功发布第一篇内容的时间"< 10 分钟**，以及 **月度成功发布次数**（遥测自愿上报或用户反馈计数）。

---

## 五、开发路线图

### v1.6.3 热修复（本周，目标：止血）
| # | 动作 | 验收标准 |
|---|---|---|
| 1 | 轮换泄漏令牌，remote 改 credential manager | `.git/config` 无明文令牌；旧令牌在 GitCode 后台吊销 |
| 2 | 修 install.ps1：平铺解压（与 install.sh 同语义），加安装后自检（列出发现的 SKILL.md 数） | Windows 全新环境安装任一包后，Claude Code 能发现全部技能 |
| 3 | 清理 ENG-02 空壳引用：要么补齐脚本，要么删除死引用并在 description 如实降级 | 新增 `tools/check_integrity.py`：扫描全部 SKILL.md 中引用的相对路径，0 断链 |
| 4 | manifest 加 sha256 字段；build.py 打包后写入校验和并回填 size_kb | 任一 zip 可用 sha256 验证 |

### v1.7 信任基建（2-3 周，目标：把"诚实"变成"可证明"）
| # | 动作 | 说明 |
|---|---|---|
| 1 | **skill-validator 门禁脚本**（复用 verify 思路）：frontmatter 规范、引用完整性、dry-run 守卫存在性、密钥模式扫描、publish_common 单测强制运行 | 输出每技能质量分卡（对齐 SkillsBench 12 分制），manifest 中记录 score |
| 2 | 恢复自动执行：GitCode/Gitee 流水线若不可用则提供 `make check`（pytest + validator + build 冒烟）+ pre-commit hook；CONTRIBUTING 改为"PR 必须附 check 输出" | 174 用例每次变更全部执行 |
| 3 | 每个 patch 版本打 git tag；CHANGELOG 与 tag 一一对应 | v1.7.0 起 tag 全覆盖 |
| 4 | 上游 33 技能目录内补 MIT 版权头（来源、commit hash、许可证） | 法务合规闭环 |

### v2.0 重定位 + 多渠道分发（1-2 月，目标：占领心智）
| # | 动作 | 说明 |
|---|---|---|
| 1 | **仓库叙事重构**：首页主打 content-publishing（"让 AI 替你运营 18 个中文平台"）；programming 重组为单数个 "basics" 包，移到二级位置 | README 首屏 = 北极星场景演示 GIF |
| 2 | **接入注册处管道**：向 SkillHub（skillhub.cn）、skills.sh、ClawHub 提交 18 个自研技能；保留 zip 直装作为兜底 | 支持 `npx skills add` 式一键安装；每个技能独立可装（拆掉"必须整包"） |
| 3 | **聚焦原则落地**：pack 按 SkillsBench 结论瘦身——每个使用场景默认推荐 2-3 个技能组合（如"知乎深度文"= zhihu-content-manager + ai-cover-generator + cross-post-orchestrator），在 README 给出"组合配方"表 | 反"大杂烩"，正中 +18.6 分数据 |
| 4 | 18 个自研技能双语化（SKILL.md 正文中文保留、frontmatter/description 英文化），面向海外想触达中文平台的用户 | 全球无竞品 |
| 5 | orchestrator 升级为旗舰：plan(离线)→逐平台 confirm→执行的编排模式写成公开方法论文章，蹭 AgentSkillOS 学术热点建立"我们早就这么做"的心智 | 内容营销素材 |

### v2.x 扩展（Q4 起，视 v2.0 数据决定优先级）
- **平台适配器 SDK**：把 `_common` + publisher 模板抽象成"新平台接入指南"，社区可提 PR 增加新平台（知乎盐选、即刻、酷安…），配 validator 门禁保证质量 → 解决 bus factor 和规模天花板。
- **企业/团队形态**：MCN 机构、品牌新媒体团队的私有包 + 团队凭据管理（对接 SkillHub 企业结算或独立提供）——商业化组评估这是本项目唯一自然的付费场景。
- **效果度量**：发布成功率、阅读量回收（各平台 stats API）反哺技能迭代，形成数据飞轮。

---

## 六、KPI 仪表盘（数据度量组）

| 维度 | 指标 | 当前基线 | v2.0 目标 |
|---|---|---|---|
| 质量 | 技能均分（validator 12 分制） | 未测（估 7-8，含 2 个空壳） | ≥9（top quartile） |
| 质量 | 引用断链数 | ≥7 处 | 0 |
| 可靠 | 测试自动执行率 | 0%（174 用例人肉） | 100%（每次变更） |
| 体验 | Windows 安装成功率 | 存疑（路径 bug） | 安装后自检 100% 发现 |
| 增长 | 一键安装渠道数 | 0（仅 zip 手动） | ≥3（SkillHub/skills.sh/ClawHub） |
| 增长 | 北极星：首篇发布耗时 | 未测 | < 10 分钟 |
| 治理 | tag 覆盖率 | 2/8 版本 | 100% |

---

## 七、风险登记册

| 风险 | 概率 | 影响 | 缓解 |
|---|---|---|---|
| 平台改版使 publisher 失效（最大业务风险） | 高 | 高 | VERIFY BEFORE USE 范式 + 每技能 lint 脚本 + 版本化端点常量 + 社区 issue 快速响应 SLA |
| SkillHub 等平台自己做垂直发布包 | 中 | 高 | 加速积累平台暗知识（先发 + 深）；知识壁垒比代码壁垒难抄 |
| 令牌/凭据事故 | 已发生 | 高 | P0 处置；凭据只走 env 的既有纪律保持 |
| 单人维护中断 | 中 | 中 | v2.x 平台适配器 SDK 引入外部贡献者；文档化 SOP |
| 上游许可证纠纷 | 低 | 中 | v1.7 补齐目录内版权头 |
| 中文平台 ToS 灰色地带（自动化发布） | 中 | 中 | 各技能明确标注平台政策边界；默认人工确认步骤保留（orchestrator 的 confirm 设计已是正确答案） |

---

## 附录 A：竞品速查（生态组供后续跟踪）

- agentskills.io — 开放规范本体
- skills.sh（Vercel）/ SkillsMP / SkillHub(skillhub.cn) / ClawHub.ai — 分发渠道四强
- anthropics/skills、obra/superpowers、vercel-labs/agent-skills — 标杆仓库
- karanb192/awesome-claude-skills（13k★）— 提交收录的流量入口
- SkillsBench / AgentSkillOS（arXiv 2603.02176）— 质量基准与编排方法论，路线图的理论依据

## 附录 B：本评审的证据基础

- 全量勘察：407 文件 / 189 md / 120 py / 64 json；52 SKILL.md frontmatter 逐个核验；manifest↔pack↔磁盘三方比对零偏差
- 抽样深读 9 个技能（api-design-reviewer、helm-chart-builder、tdd-guide、performance-profiler、runbook-generator、zhihu-content-manager、csdn-publisher、v2ex-publisher、wechat-mp-publisher）
- install.ps1/install.sh/build.py/build.sh/sync-mirrors.ps1 源码级审查；P0/P1 关键项由主会话二次复核
- 市场数据：Agentman Ecosystem Report 2026-06、Snyk ToxicSkills、SkillsBench、arXiv 2602.08004 / 2603.02176、腾讯云开发者社区 2026-05 平台评测

*—— 评审团联席签署（模拟）：战略产品组长 · 工程质量组长 · 安全合规组长 · 生态分发组长 · 终审委员会主席*
