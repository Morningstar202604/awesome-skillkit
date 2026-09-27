# SOURCES — 技能来源与更新指引 / Skill Sources & Updates

> 本仓库维护六条线（截至 0.23.2，共 **418 个技能 / 57 个场景包** = 官方收录 28 + 上游精选 32 +
> 上游改造 5 + 自建 126 + 新收录 I 148 + 新收录 II 64 + 查漏补缺 15）：
> 0. **官方收录**（28 个，2026-09-27 起，`skills/integrations/lark/`）——飞书官方仓库 `larksuite/cli` 的
>    Agent Skills，整包收录为 `feishu-suite`，见「官方收录」一节；
> 1. **上游精选**（`skills/programming/` 下 13 个分类目录，32 个）——全部来自下方上游项目；
> 2. **上游改造**（5 个：`docx-template-fill`、`frontend-component-lab`、`career-ops-lite`、
>    `session-handoff`、`webapp-e2e-harness`，改造自其他开源项目，见「上游改造」一节）；
> 3. **自建场景技能**（126 个）——分布在 `skills/writing/`、`skills/video/`、`skills/office/`、`skills/music/`、
>    `skills/paper/`、`skills/ppt/`、`skills/tools/`、`skills/integrations/`、`skills/memory/`、`skills/knowledge/`、
>    `skills/education/`、`skills/meta/`、`skills/dataviz/`、`skills/design/`、`skills/life/`、
>    `skills/communication/` 等，及 `skills/programming/` 下的 6 个自建子目录（`data/`、`debug/`、
>    `math/`、`ml/`、`planning/`、`web-data-extractor/`）与 3 个编在上游目录里的自建技能
>    （`security/pii-redactor`、`security/prompt-injection-guard`、`testing/webapp-flow-tester`），
>    本仓库原创维护。
> 4. **新收录 I**（148 个，2026-09-27，12 个新场景包 × 21 个上游仓库，见「本批新收录」一节）——
>    按路线图「开户」清单批量迁入：知识工作 / 工程方法论 / 云平台 / CMO / 产品管理 / 微信长文 /
>    代码化视频 / Google Workspace / Hugging Face / 科研计算 / 代码质量 / 创作增强单品。
> 5. **新收录 II**（64 个，2026-09-27，5 个新场景包 × 5 个上游仓库，见「本批新收录 II」一节）——
>    路线图 P1 收尾（caveman 省 token 工具包）+ P2 许可核验后的四源精选：网络安全实战（cybersecurity-pro，
>    Apache-2.0 社区大包精选）、GTM 增长（goose-skills）、语言工程规范（mindrally/skills）、
>    公司运营手册（headcount）；同批裁决三项**不迁**（Lawvable CC BY-NC-ND、OpenClaw Medical 无 LICENSE、
>    buildwithclaude 聚合平台）。

> 6. **并入资产·专家团**（2026-09-27 起，`expert-teams/`）——原独立仓库 `ai-expert-teams`（MIT）
>    整体迁入：18 支团队 / 219 位专家 agent / 100 个技能，自带索引与门禁；**不计入**上文
>    339 技能 / 52 场景包的计数口径。

## 上游仓库 / Upstream（skills/programming/ 的 13 个分类目录）

| 项目 | 地址 | 协议 |
|------|------|------|
| alirezarezvani/claude-skills | <https://github.com/alirezarezvani/claude-skills> | MIT |

- 收录数量：**32 个 skill**（全部来自上述上游；原收录的 `pr-review-expert` 已移除）。
- 与上游的差异：上游两个近似重复项 `database-schema-designer`、`agent-workflow-designer`
  已合并进同源兄弟 skill，其独有内容以参考文档形式保留在对应 skill 内。
- ⚠️ 注意：`skills/programming/` 下的 `data/`、`debug/`、`math/`、`ml/`、`planning/`、
  `web-data-extractor/` 六个目录是**自建**技能（共 13 个），不属于上游——更新上游时请勿覆盖。
  另有 3 个自建技能编在上游目录里（`security/pii-redactor`、`security/prompt-injection-guard`、
  `testing/webapp-flow-tester`），同步上游时同样勿覆盖。

## 更新方法 / How to update

```bash
# 1. 拉取上游最新版
git clone https://github.com/alirezarezvani/claude-skills.git D:\_upstream\claude-skills
#    （已克隆过则：git -C D:\_upstream\claude-skills pull）

# 2. 把需要更新的 skill 文件夹覆盖到本仓库对应位置
#    skills/programming/<分类>/<skill-name>/...
#    （仅限上游 13 个分类目录，勿碰 data/debug/math/ml/planning/web-data-extractor）

# 3. 校验 manifest.json 中该 skill 的条目仍一致（名称、分类）

# 4. 重新打包发布
python3 build.py         # 唯一构建入口
```

## 上游改造 / Upstream-adapted（5 个）

改造自其他开源项目（非 `alirezarezvani/claude-skills` 上游主线），核心工作流保留、按本仓库
工程规范重写（离线可测 / dry-run 默认 / 自带冒烟测试）。来源项目：mattpocock、ECC、
anthropics、santifer-career-ops——逐技能对应关系以各技能 `references/` 与 commit `3a39242`
登记为准。

| Skill | 目录 |
|-------|------|
| docx-template-fill | `skills/office/docx-template-fill` |
| frontend-component-lab | `skills/design/frontend-component-lab` |
| career-ops-lite | `skills/office/career-ops-lite` |
| session-handoff | `skills/meta/session-handoff` |
| webapp-e2e-harness | `skills/programming/testing/webapp-e2e-harness` |

## 官方收录 / Official upstream —— 飞书套件 `feishu-suite`（28 个）

| 项目 | 地址 | 协议 |
|------|------|------|
| larksuite/cli（飞书官方 CLI） | <https://github.com/larksuite/cli> | MIT（Copyright (c) 2026 Lark Technologies Pte. Ltd.） |

- 收录数量：**28 个 skill**（`skills/integrations/lark/<skill-name>/`，整包 = `packs/feishu-suite`）：
  `lark-shared`（认证/权限底座）、`lark-im`、`lark-doc`、`lark-wiki`、`lark-base`、`lark-sheets`、`lark-slides`、
  `lark-calendar`、`lark-mail`、`lark-task`、`lark-meeting`、`lark-drive`、`lark-approval`、`lark-okr`、
  `lark-contact`、`lark-event`、`lark-markdown`、`lark-whiteboard`、`lark-apps`、`lark-attendance`、
  `lark-openapi-explorer`、`lark-skill-maker`，以及 4 个兼容重定向项（`lark-minutes` / `lark-note` / `lark-vc` /
  `lark-vc-agent`）与 2 个流程配方（`lark-workflow-meeting-summary` / `lark-workflow-standup-report`）。
- **与上游的差异**（同步上游时注意，勿覆盖）：
  1. frontmatter 规范化为本仓库 schema（`license: MIT` + `compatibility` + `metadata.{author,version,category,pattern,tier,verified-date,source}`）；
  2. 每个技能正文尾附「来源与署名」段；
  3. 长参考文档（>100 行且无目录）增补 `## 目录`；
  4. 相对链接归一化为「技能目录相对」口径（本仓库 `validate_skills.py` 的解析约定）；
  5. 少量文案修正（去盘符示例、去掉会误判为路径的写法）；`lark-slides/scripts/conftest.py` 为 pytest 收集补的 sys.path 垫片。
- 更新方法：上游更新后，用 `skills/integrations/lark/<name>/` 覆盖同名目录（`references/` / `scripts/` 一并覆盖），
  再按上述 1–4 重新规范化，最后跑门禁（`python3 tools/validate_skills.py` / `pytest skills -q` / `build.py` / `tools/build_site.py`）。

## 本批新收录 / New batch — 12 个新场景包（148 个，2026-09-27）

按 [`docs/TAXONOMY-V2.md`](docs/TAXONOMY-V2.md) §3 开户清单批量迁入；许可一律以仓库内 **LICENSE 文件实测**为准（README 口述不采信），无许可不入仓（不迁裁决见 TAXONOMY-V2 §3）。

| 场景包 | 上游仓库 | 许可 | 技能 | 目录 |
|--------|----------|------|-----:|------|
| knowledge-work | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) | Apache-2.0 | 21 | `skills/hr`(6) / `legal`(4) / `finance`(2) / `ops`(3) / `customer`(3) / `design`(3) |
| engineering-playbook | [obra/superpowers](https://github.com/obra/superpowers)（12）+ [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)（6）+ [mattpocock/skills](https://github.com/mattpocock/skills)（3） | MIT ×3 | 21 | `skills/programming/methodology`(12) / `engineering`(9) |
| cloud-platforms | [microsoft/azure-skills](https://github.com/microsoft/azure-skills)（5）+ [cloudflare/skills](https://github.com/cloudflare/skills)（3）+ [supabase/agent-skills](https://github.com/supabase/agent-skills)（2）+ [firebase/agent-skills](https://github.com/firebase/agent-skills)（2） | MIT / Apache-2.0 | 12 | `skills/programming/cloud` |
| cmo-suite | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills)（增量：LinkedIn 6 + C-level 6） | MIT | 12 | `skills/marketing/cmo`(6) / `skills/leadership`(6) |
| product-management | [phuryn/pm-skills](https://github.com/phuryn/pm-skills)（12）+ [mattpocock/skills](https://github.com/mattpocock/skills)（2：`to-spec` / `triage`） | MIT ×2 | 14 | `skills/product` |
| wechat-longform | [JimLiu/baoyu-skills](https://github.com/JimLiu/baoyu-skills) | MIT | 10 | `skills/writing` |
| video-code | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | Apache-2.0 | 5 | `skills/video` |
| google-workspace | [googleworkspace/cli](https://github.com/googleworkspace/cli) | Apache-2.0 | 12 → **27**（2026-09-27 查漏补缺：补齐被引用的 15 个兄弟技能） | `skills/integrations/gws` |
| hf-ml-hub | [huggingface/skills](https://github.com/huggingface/skills) | Apache-2.0 | 11 | `skills/programming/ml` |
| scientific-agent-skills | [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills)（自 166 精选 12） | MIT | 12 | `skills/programming/science` |
| code-quality-pro | [wshobson/agents](https://github.com/wshobson/agents)（12）+ [alibaba/open-code-review](https://github.com/alibaba/open-code-review)（1） | MIT / Apache-2.0 | 13 | `skills/programming/quality` |
| creator-boosters | [blader/humanizer](https://github.com/blader/humanizer)（1）+ [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design)（1）+ [tt-a1i/archify](https://github.com/tt-a1i/archify)（2）+ [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft)（1） | MIT ×3 + Apache-2.0 | 5 | `skills/design`(3) / `writing`(1) / `video`(1) |

**统一的迁移规范化**（同步上游时注意，勿覆盖）：

1. frontmatter 规范化为本仓库 schema（`license` + `compatibility` + `metadata.{author,version,category,pattern,tier,verified-date,source}`），`name` 与目录名对齐；
2. 每个技能正文尾附「来源与署名」段；
3. 长参考文档（>100 行且无目录）增补 `## 目录`；超长正文（≥500 行）拆到 `references/` 并在正文留链接；
4. 相对链接归一化为「技能目录相对」口径；盘符/绝对路径改 `<project-dir>` 占位或注释化；
5. 移除上游的嵌套 / 重复 `SKILL.md` 与杂散目录；过短 description 补写至可路由粒度；
6. 中文使用说明按需补 `compatibility`（如"部分技能假设已连接企业系统，未连接时按文内提示降级"）。

**更新方法**：clone 上游 → 覆盖对应目录（`references/` / `scripts/` 一并覆盖）→ 按上述 1–6 重新规范化 → 跑门禁四连（`tools/validate_skills.py` / `pytest skills -q` / `build.py` / `tools/build_site.py`）。

## 本批新收录 II / New batch II — 5 个新场景包（64 个，2026-09-27）

> 分类 v2 路线图 P1 收尾（caveman）+ P2 许可核验后的四源精选；许可一律 raw LICENSE 文件级实测。

| 场景包 | 上游仓库 | 许可 | 技能 | 目录 |
|--------|----------|------|-----:|------|
| caveman-toolkit | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman)（仅取 `skills/` 技能面 7 个） | MIT（引擎目录 `engine/` `proxy/` 等为 BSL-1.1，**未收录**） | 7 | `skills/meta` |
| cybersecurity-pro | [mukul975/Anthropic-Cybersecurity-Skills](https://github.com/mukul975/Anthropic-Cybersecurity-Skills)（818 精选 14；社区项目，非 Anthropic 官方） | Apache-2.0 | 14 | `skills/programming/security` |
| gtm-growth | [gooseworks-ai/goose-skills](https://github.com/gooseworks-ai/goose-skills)（281 精选 16） | MIT | 16 | `skills/marketing/gtm` |
| language-standards | [mindrally/skills](https://github.com/mindrally/skills)（Cursor Rules 转换，240+ 精选 14） | Apache-2.0 | 14 | `skills/programming/standards` |
| company-playbooks | [cbrock84/headcount](https://github.com/cbrock84/headcount)（172 精选 13） | MIT | 13 | `skills/ops`(8) / `skills/leadership`(3) / `skills/finance`(1) / `skills/product`(1) |

**P2 许可核验裁决（核验未通过，不迁）**：

| 来源 | 实测 | 裁决 |
|---|---|---|
| [lawvable/awesome-legal-skills](https://github.com/lawvable/awesome-legal-skills)（272） | 根 LICENSE = **CC BY-NC-ND 4.0**（禁商用 + 禁衍生物）；部分条目另有 AGPL-3.0 标注 | 不迁（ND 禁止改写与再分发） |
| [FreedomIntelligence/OpenClaw-Medical-Skills](https://github.com/FreedomIntelligence/OpenClaw-Medical-Skills)（~870） | **无 LICENSE 文件**（README 徽章口述 MIT，不采信） | 不迁（沿用 vercel-labs 先例）；医疗内容另需合规审查与人审 |
| [davepoon/buildwithclaude](https://github.com/davepoon/buildwithclaude)（373） | MIT（但本体是发现/市场平台，条目来自不同作者，授权链路混杂） | 不迁（聚合平台非作者本体） |

**迁移规范化**：与「本批新收录」一节 1–6 条同口径（frontmatter 归一、来源署名段、长参考文档补目录、
绝对路径占位化、name 与目录名对齐、补 `description_zh`）；cyber 技能的 5 个超 100 行参考文档已补
`## 目录 / Contents`，headcount 的 `sources.md` 生成脚注改写为未随包的说明。

**更新方法**：clone 上述上游 → 覆盖对应 `skills/` 目录（`references/` / `scripts/` 一并覆盖）→
按 1–6 重新规范化 → 跑门禁四连（`tools/validate_skills.py` / `pytest skills -q` / `build.py` / `tools/build_site.py`）。

## 并入资产 / Merged-in assets

### 专家团 `expert-teams/`（原 `ai-expert-teams` 仓库，MIT）

2026-09-27 自独立仓库整体迁入；原仓库已在 GitHub（X33834 / Morningstar202604）、GitCode、
Gitee 四个平台下线。资产构成：

- `teams/<team>/agents/*.md`——18 支团队共 219 位专家定义；根级 `project-director.md` 为跨团队路由入口（agent 合计 220 个）；
- `teams/<team>/skills/`（团队专属 86 个）+ `skills/`（通用 14 个）——共 100 个技能，索引见 `expert-teams/SKILLS_INDEX.md`；
- `orchestration-protocol.md`——共享编排协议（门禁 / 回炉 / 断路 / 交接四块模板）；
- 工程层——`verify.py`、`effectiveness.py`、`export-agents.py`、`export-platforms.py`、`build-site.py`、`tests/`（pyyaml 依赖）；
- 官网——源模板 `expert-teams/site/template.html`，生成页 `expert-teams/site/index.html`，构建时同步为站点子页 `site/expert-teams.html`；
- 安装包——`expert-teams/export-platforms.py` 生成四平台包与全量源包（可复现 zip），提交在 `site/downloads/expert-teams-*.zip` 供站点/镜像直接下载，发版时同步挂 Release 附件；
- 与主仓库技能重叠的 26 个同名技能在迁入前已完成融合裁定（8 取仓库版、10 融合含 Apache 署名、3 保留原版、5 无许可不入仓），同名以子目录内版本为准。

## 自建场景技能 / Self-authored scenarios（126 个）

### 内容发布与写作（skills/writing/，21 个）

| Skill | 场景包 | 说明 |
|-------|--------|------|
| zhihu-content-manager | content-publishing | 知乎发布/编辑/删除/乱码修复 + HTML lint 门禁 |
| cnblogs-skill | content-publishing | 博客园 API 发文全流程 + 预发布格式检查 |
| wechat-mp-publisher | content-publishing | 公众号官方草稿箱/发布 API，默认 dry-run |
| juejin-publisher | content-publishing | 掘金 Web 接口发布（端点需按文档核对） |
| cross-post-orchestrator | content-publishing | 多平台编排：计划→调度→台账 |
| csdn-publisher | content-publishing | CSDN 博客发布/管理，Web 内部 API，7 子命令 |
| jianshu-publisher | content-publishing | 简书发布/管理，Web 内部 API，4 子命令 |
| bilibili-publisher | content-publishing | B 站视频/专栏/动态发布，官方 API + Web API，5 子命令 |
| toutiao-publisher | content-publishing | 今日头条/抖音文章/微头条，官方 API + Web API，2 子命令 |
| baijiahao-publisher | content-publishing | 百家号文章/视频/草稿发布，官方 API，3 子命令 |
| xiaohongshu-publisher | content-publishing | 小红书笔记草稿/发布/编辑/删除，Web 内部 API，4 子命令 |
| weibo-publisher | content-publishing | 微博发布/转发/评论/删除/图片上传，官方 API + Web API，3 子命令 |
| douban-publisher | content-publishing | 豆瓣日记/广播/小组话题发布，Web 内部 API，3 子命令 |
| v2ex-publisher | content-publishing | V2EX 发帖/回复/节点列表，Web 内部 API，3 子命令 |
| segmentfault-publisher | content-publishing | SegmentFault 文章/提问发布，Web 内部 API，3 子命令 |
| oschina-publisher | content-publishing | 开源中国博客/问答/动态，官方 API + Web API，3 子命令 |
| static-blog-deploy | content-publishing | Hexo/Hugo/GitHub Pages/GitLab Pages/Vercel/Netlify 部署，6 子命令 |
| article-outliner | ai-research-writing | 文章大纲生成 |
| article-drafter | ai-research-writing | 初稿撰写 |
| content-editor | ai-research-writing | 内容编辑润色 |
| seo-optimizer | ai-research-writing | SEO 优化 |

### AI 视频（skills/video/，15 个）

| Skill | 场景包 | 说明 |
|-------|--------|------|
| video-script-writer | ai-video-pipeline | 视频脚本撰写 |
| video-voice-synth | ai-video-pipeline | 语音合成 |
| video-lip-sync | ai-video-pipeline | 口型同步 |
| video-editor | ai-video-pipeline | 视频剪辑编排 |
| video-subtitles | ai-video-pipeline | 字幕生成/烧录 |
| video-thumbnail | ai-video-pipeline | 封面/缩略图 |
| video-generation | ai-media-toolkit | 文生视频 |
| image-generation | ai-media-toolkit | 文生图 |
| ai-baby-podcast | viral-entertainment | AI 宝宝播客短视频 |
| nailong-laugh-shorts | viral-entertainment | 奶龙搞笑短片 |
| storyboard-designer | video-design-studio | 分镜设计：节拍表 + 逐场景 prompt 对 + 连续性约束表 |
| shot-designer | video-design-studio | 镜头清单设计（目的/能量/运镜/出场转场） |
| motion-effects-designer | video-design-studio | 动态图形与特效设计（动态排版/角标/动态图表/粒子） |
| transition-designer | video-design-studio | 场景转场设计（转场选型/时长/踩点/交接清单） |
| visual-style-anchor | video-design-studio | 风格锚 + 角色一致性卡 |

### 编程自建（skills/programming/ 下 6 个目录，13 个）

| Skill | 场景包 | 说明 |
|-------|--------|------|
| etl-builder | data-ml-science | ETL 流水线搭建 |
| feature-engineer | data-ml-science | 特征工程 |
| model-formulator | data-ml-science | 数学建模（问题→公式） |
| model-solver | data-ml-science | 求解器调度（scipy/pulp 等） |
| simulation-runner | data-ml-science | 蒙特卡洛/离散事件仿真 |
| result-visualizer | data-ml-science | 结果可视化 |
| ml-pipeline | data-ml-science | 机器学习全流程（sklearn/XGBoost） |
| debug-diagnoser | code-planning | 系统化调试诊断 |
| code-intent-planner | code-planning | 意图→计划→代码流水线（含会话持久化） |
| code-generator | code-planning | 按计划生成代码骨架 |
| deep-research | ai-research-writing | 深度研究流水线 |
| web-search | ai-research-writing | 网络检索聚合 |
| web-data-extractor | web-ops | 网页数据提取（结构化抽取/批量抓取） |

### 办公/研究/娱乐（skills/office/ + skills/music/ + skills/paper/ + skills/ppt/，6 个）

| Skill | 场景包 | 说明 |
|-------|--------|------|
| paper-topic-selector | ai-research-writing | 论文选题评估 |
| ppt-builder | office-productivity | PPT 生成（python-pptx） |
| excel-assistant | office-productivity | Excel 处理（openpyxl/pandas） |
| meeting-notes | office-productivity | 会议纪要 |
| resume-tailor | office-productivity | 简历定制 |
| music-generation | ai-media-toolkit | 音乐生成 |

### AI 对话/设计/营销/教育（skills/chat/ + skills/design/ + skills/audio/ + skills/marketing/ + skills/education/，17 个）

| Skill | 场景包 | 说明 |
|-------|--------|------|
| chat-prompt-engineer | chat-prompt-craft | 对话助手提示词工程（豆包/ChatGPT/Kimi 等：五要素公式 + 智能体五段骨架 + 结构审计） |
| design-brief-interpreter | visual-design-studio | 模糊需求 → 7 字段设计规格单（链条入口） |
| image-prompt-engineer | visual-design-studio | 五段式文生图 prompt（含文字渲染铁律与模型方言） |
| layout-spec-auditor | visual-design-studio | 平台版面规格审计脚本（比例/分辨率/安全区/文字预算） |
| design-system-foundations | visual-design-studio | 设计系统基础：令牌/组件/间距体系搭建 |
| ui-ux-accessibility | visual-design-studio | UI/UX 无障碍审计（对比度/键盘/读屏） |
| image-batch-processor | image-studio | 图片批量处理（压缩/转格式/批量改尺寸） |
| podcast-producer | audio-studio | 播客分段脚本（纯口播词纪律 + TTS 安全 lint） |
| tts-voice-director | audio-studio | 跨引擎声音目录选角 + ffmpeg 拼接计划 |
| sound-designer | audio-studio | 音频床设计与混音（SFX/BGM 选型、音量/响度规范） |
| episode-publisher | audio-studio | shownotes + 时间戳章节 + 平台元数据 + AI 披露 |
| product-copywriter | growth-marketing | 转化框架商品文案（FAB/PAS/AIDA + 异议处理 + 广告法卫生） |
| campaign-designer | growth-marketing | 营销日历 + 渠道矩阵 + 单变量 A/B 变体对 |
| channel-adapter | growth-marketing | 渠道适配（内置约束表 + channel_fit_check.py 校验） |
| course-designer | edu-craft | 学习契约 + checkpoint 依赖排序课程设计 |
| exercise-generator | edu-craft | 开放题严格题库（禁选择题，附评分标准与 lint） |
| feynman-explainer | edu-craft | 费曼六拍补救伴学（诊断→修复→回讲→迁移） |

### 学术论文工具（skills/paper/，11 个）

| Skill | 场景包 | 说明 |
|-------|--------|------|
| lit-review | ai-research-writing | 文献检索+关系图谱+总结（--arxiv 为离线 mock，输出须标注模拟数据） |
| experiment-runner | ai-research-writing | 实验多轮运行+统计检验（实验体为 mock 逻辑，同上） |
| arch-diagram | ai-research-writing | 架构/框架图 TikZ+SVG（学习自 torchdiagram / archscope / PlotNeuralNet） |
| neural-net-draw | ai-research-writing | 神经网络结构图 TikZ（学习自 PlotNeuralNet） |
| latex-formatter | ai-research-writing | LaTeX 格式化+编译前检查（缺文件 rc=1 门禁语义） |
| self-reviewer | ai-research-writing | 模拟审稿 ready/needs_work 结构判定 |
| journal-adapt | ai-research-writing | IEEE/ACM/NeurIPS/ACL/Nature/Cell 适配+禁用语筛查（学习自 Awesome-Journal-Skills） |
| anti-defensive | ai-research-writing | 防御性学术写作检测修复（学习自 anti-defensive-writing） |
| ai-humanizer | ai-research-writing | 去 AI 痕迹保学术声音（学习自 academic-humanizer） |
| tex-cleaner | ai-research-writing | arXiv 提交前清理五类检查（学习自 arxiv-latex-cleaner） |
| pub-plotter | ai-research-writing | SciencePlots 风格学术图（学习自 garrettj403/SciencePlots） |

### 外部集成（skills/integrations/，4 个）

| Skill | 场景包 | 说明 |
|-------|--------|------|
| notion-workspace | workspace-integrations | Notion API 请求构造与响应解析（版本头/游标分页/3 req/s 限速/块类型白名单），脚本离线不发请求 |
| feishu-dingtalk-bridge | workspace-integrations | 飞书/钉钉/企业微信三家消息负载构造与回调解析，含协议差异对照表与钉钉加签算法 |
| issue-tracker-sync | workspace-integrations | Jira/Linear/GitHub Issues 建单请求构造 + 跨平台状态语义映射 + 离线周报生成 |
| cloud-drive-manager | workspace-integrations | 云盘归档：上传计划（分片策略）、sha256/md5 校验清单、三家列表响应解析；不提供删除命令 |

### 生活与沟通（skills/life/ + skills/communication/，6 个）

| Skill | 场景包 | 说明 |
|-------|--------|------|
| car-purchase-maintenance | life-essentials | 买车与保养决策（比价/合同/维保避坑） |
| home-renovation-avoidance | life-essentials | 家装避坑（报价审核/增项/验收） |
| medical-visit-guide | life-essentials | 就诊准备与沟通（症状梳理/问诊清单/报告解读） |
| rental-contract-guide | life-essentials | 租房合同审查（条款风险/押金/退租） |
| decision-debiasing | communication-essentials | 决策去偏（识别常见偏差并给出纠偏流程） |
| tactful-communication | communication-essentials | 得体沟通（措辞策略/难对话脚本/分寸检查） |

### v0.16–v0.20 新增自研（33 个）

v0.18 发版后新增、未及登记进上文分域表格的技能，此处补齐：

| Skill | 场景包 | 目录 |
|-------|--------|------|
| agent-eval-harness | Test-Driven Development | `meta/agent-eval-harness` |
| ai-trace-auditor | De-AI Writing | `writing/ai-trace-auditor` |
| assignment-intake | Homework Autopilot | `education/assignment-intake` |
| bank-statement-reconcile | Toolsmith | `tools/bank-statement-reconcile` |
| batch-renamer | Toolsmith | `tools/batch-renamer` |
| chart-recommender | Data Viz Studio | `dataviz/chart-recommender` |
| dashboard-designer | Data Viz Studio | `dataviz/dashboard-designer` |
| docx-writer | Office Productivity | `office/docx-writer` |
| epub-builder | Office Productivity | `office/epub-builder` |
| file-organizer | Toolsmith | `tools/file-organizer` |
| format-converter | Toolsmith | `tools/format-converter` |
| frontend-design-director | Visual Design Studio | `design/frontend-design-director` |
| humanize-rewriter | De-AI Writing | `writing/humanize-rewriter` |
| internal-comms-writer | Office Productivity | `office/internal-comms-writer` |
| invoice-organizer | Toolsmith | `tools/invoice-organizer` |
| knowledge-graph-builder | Knowledge Base | `knowledge/knowledge-graph-builder` |
| memory-architect | Memory Systems | `memory/memory-architect` |
| memory-extractor | Memory Systems | `memory/memory-extractor` |
| memory-manager | Memory Systems | `memory/memory-manager` |
| memory-retriever | Memory Systems | `memory/memory-retriever` |
| own-voice-rewrite | Homework Autopilot | `education/own-voice-rewrite` |
| pdf-pipeline | Office Productivity | `office/pdf-pipeline` |
| personal-voice-profile | De-AI Writing | `writing/personal-voice-profile` |
| personal-wiki | Knowledge Base | `knowledge/personal-wiki` |
| pii-redactor | Security & Secrets | `programming/security/pii-redactor` |
| prompt-injection-guard | Security & Secrets | `programming/security/prompt-injection-guard` |
| skill-author | Skill Forge | `meta/skill-author` |
| skill-finder | Skill Forge | `meta/skill-finder` |
| skill-linter | Skill Forge | `meta/skill-linter` |
| solution-drafter | Homework Autopilot | `education/solution-drafter` |
| task-scheduler | Toolsmith | `tools/task-scheduler` |
| webapp-flow-tester | Test-Driven Development | `programming/testing/webapp-flow-tester` |
| weekly-report-generator | Skill Forge | `meta/weekly-report-generator` |

以上 126 个自建技能不来自上游（另 5 个上游改造见上文），由本仓库原创维护，更新即改本仓库。

## 全部技能清单（418 = 官方收录 28 + 上游精选 32 + 上游改造 5 + 自建 126 + 新收录 I 148 + 新收录 II 64 + 查漏补缺 15）

### 上游精选（32）

| # | Skill | 所在 pack | 上游路径参考 |
|---|-------|-----------|--------------|
| 1 | agent-designer | ai-agent-development | skills/ 下同名目录 |
| 2 | mcp-server-builder | ai-agent-development | 同上 |
| 3 | feature-flags-architect | ai-agent-development | 同上 |
| 4 | self-eval | ai-agent-development | 同上 |
| 5 | skill-tester | ai-agent-development | 同上 |
| 6 | api-design-reviewer | api-development, code-review | 同上 |
| 7 | api-test-suite-builder | api-development | 同上 |
| 8 | senior-architect | architecture | 同上 |
| 9 | migration-architect | architecture | 同上 |
| 10 | monorepo-navigator | architecture | 同上 |
| 11 | ci-cd-pipeline-builder | ci-cd | 同上 |
| 12 | ship-gate | ci-cd | 同上 |
| 13 | spec-driven-workflow | ci-cd | 同上 |
| 14 | code-reviewer | code-review | 同上 |
| 15 | tech-debt-tracker | code-review | 同上 |
| 16 | dependency-auditor | code-review | 同上 |
| 17 | docker-development | containers | 同上 |
| 18 | helm-chart-builder | containers | 同上 |
| 19 | kubernetes-operator | containers, infrastructure | 同上 |
| 20 | database-designer | database | 同上 |
| 21 | sql-database-assistant | database | 同上 |
| 22 | git-worktree-manager | github-workflow | 同上 |
| 23 | changelog-generator | github-workflow | 同上 |
| 24 | incident-commander | incident-response | 同上 |
| 25 | runbook-generator | incident-response | 同上 |
| 26 | slo-architect | incident-response | 同上 |
| 27 | terraform-patterns | infrastructure | 同上 |
| 28 | observability-designer | infrastructure | 同上 |
| 29 | performance-profiler | performance | 同上 |
| 30 | secrets-vault-manager | security | 同上 |
| 31 | env-secrets-manager | security | 同上 |
| 32 | tdd-guide | tdd | 同上 |

> 注：`skill-tester/assets/sample-skill/` 是 skill-tester 自带的示例资产，不算独立 skill。

### 自建（126）

按上文"自建场景技能"各小节的表格为准，此处不重复罗列。
单一事实来源是 `manifest.json`（由 `build.py` 从 `packs/*/pack.json` 自动同步）。

### 官方收录（28）与本批新收录（I 148 + II 64）

- 官方收录（feishu-suite 28）：见上文「官方收录」一节清单；
- 新收录 I（12 包 148 个）、新收录 II（5 包 64 个）与查漏补缺（15 个 gws 兄弟技能）：逐技能以
  `packs/<id>/pack.json` 的 `skills[].name/source` 为准，由 `build.py` 同步进 `manifest.json`，此处不重复罗列。

## 共享工具 / Shared helpers

| 模块 | 说明 |
|------|------|
| `skills/writing/writing_pipeline.py` | 写作域编排器：选题→大纲→初稿→编辑→SEO→发布 |
| `skills/video/video_pipeline.py` | 视频域编排器：脚本→配音→口型→剪辑→字幕→封面 |
| `skills/paper/paper_pipeline.py` | 论文域编排器 |
| `skills/ppt/ppt_pipeline.py` | PPT 域编排器 |
| `skills/programming/math/math_pipeline.py` | 数学建模域编排器：建模→求解→仿真→可视化 |
| `skills/programming/planning/pipeline_orchestrator.py` | 代码计划域编排器：意图→计划→生成 |

## 历史 / History

- 2026-09-27（v0.23.2）：**二轮逐文件复查定版**——5814 个跟踪文件全覆盖：video-shotcraft
  `workbench/GUIDE.md` 9 处插图断链补齐（上游 `workbench/docs/` 全 9 图随包分发）、26 个 lark
  官方技能补 `description_zh`（418/418 真实全仓覆盖）、运行残留清理；分发侧落地 skills.sh
  徽章 + `npx skills add` 安装路线（CLI 实测发现全部 418 技能），站点每包 `release_*` 钉链
  随定版对齐（上一版钉在无 Release 的 v0.23.1）。账目不变 418 = 28+32+5+126+148+64+15。

- 2026-09-27（v0.23.1）：**全仓查漏补缺**——逐文件审计（5721 个跟踪文件）后：修复 293 处相对引用
  （含 lark / diagram-design / baoyu 等上游路径口径不一）、补齐被引用的上游资产（knowledge-work 5 份
  CONNECTORS.md → 13 个技能 `references/`；HyperFrames frame-presets 48 文件 + design-picker 模板；
  video-shotcraft workbench/GUIDE.md）、gws 包 12 → 27（补齐 15 个被引用的兄弟技能）、`pack.json` 字段
  归一（desc→description，与 build_site 读取口径一致），`references/iconpark-index.json` 假扩展名改名。
  账目 418 = 28+32+5+126+148+64+15；技能链 108→112；门禁 0 错 0 警、pytest 284 过。

- 2026-09-27（0.23 候选，续）：**新收录 II 5 包 / 64 技能（P1 收尾 + P2 四源精选）**——
  caveman-toolkit（caveman 技能面 7，MIT）、cybersecurity-pro（818 精选 14，Apache-2.0）、
  gtm-growth（goose-skills 精选 16，MIT）、language-standards（mindrally 精选 14，Apache-2.0）、
  company-playbooks（headcount 精选 13，MIT）；同批裁决不迁三项（Lawvable CC BY-NC-ND、OpenClaw Medical
  无 LICENSE、buildwithclaude 聚合平台）。账目 403 = 28+32+5+126+148+64，与 `manifest.json` 逐一对齐；
  场景包 52→57，能力域 27（不变），技能链 88→108。

- 2026-09-27（0.23 候选）：**本批新收录 12 包 / 148 技能（P0-2~P0-9 全落地 + P1 提前五个）**——
  按 `docs/TAXONOMY-V2.md` 开户清单迁入：knowledge-work（Anthropic，Apache-2.0）、engineering-playbook
  （superpowers + addyosmani + mattpocock，MIT）、cloud-platforms（Azure/Cloudflare/Supabase/Firebase）、
  cmo-suite、product-management（phuryn + mattpocock）、wechat-longform（baoyu）、video-code（hyperframes）、
  google-workspace（官方 CLI）、hf-ml-hub（Hugging Face）、scientific-agent-skills（K-Dense 精选）、
  code-quality-pro（wshobson + alibaba）、creator-boosters（humanizer / diagram-design / archify / video-shotcraft）。
  账目 339 = 28+32+5+126+148，与 `manifest.json` 逐一对齐；场景包 40→52，能力域 20→27（新增
  product/hr/legal/finance/ops/customer/leadership），技能链 75→88。

- 2026-09-26（v0.22.0）：**SOURCES 数字对账（第二次）**——总数 154→163、场景包 36→39；
  上游精选 33→32（`pr-review-expert` 已随重构移除），自建 116→126；分域表格补齐 v0.21
  以来未入表的 14 个自研技能（life/communication/design/video/audio/programming 各域），
  并移除 5 个已删技能行（`ai-cover-generator`、`shot-recipe-designer`、`video-prompt-engineer`、
  `figure-maker`、`pr-review-expert`）与共享模块 `_common/publish_common.py` 行
  （`_common/` 已在内容改造中删除）。账目 163 = 32+5+126，与 `manifest.json` 逐一对齐；
  三语 README 徽章 `skills-156`→`163`。

- 2026-09-21（v0.20.0）：**SOURCES 数字对账 + 归属补登记**——总数 137→154、场景包 34→36；
  口径从「两条线」改为「三条线」（上游精选 33 + 上游改造 5 + 自建 116）；补登记 v0.16 以来
  未入表的 33 个自研技能与 5 个上游改造技能；三语 README 徽章 `skills-143`→`154`、
  自研计数 `105`→`116`。账目 154 = 33+5+116，与 `manifest.json` 逐一对齐。

- 2026-09-17：**新增 `workspace-integrations` 场景包（4 技能，全部自研）** —— 首次补齐
  「外部集成」域（此前仅 git/GitHub 有覆盖）。`notion-workspace` / `feishu-dingtalk-bridge` /
  `issue-tracker-sync` / `cloud-drive-manager` 四技能共享一套操作契约：**写操作默认 dry-run
  先出负载、凭证只从环境变量读取、脚本只做「请求构造 + 响应解析」的纯函数**——
  四个脚本仅用标准库（json/argparse/hashlib/pathlib），**不发任何 HTTP 请求**，
  因此无凭证、无网络也可完整实测；真实执行时由 AI 用 curl/SDK 注入凭证。
  各技能 `references/sources-and-methodology.md` 记录了方法论蒸馏来源（两阶段 plan/apply、
  canonical model 语义中介、verify-after-write、十二要素 config）与所用 API 官方文档链接。
  同时新增 `integrations` 链域（3 条链）。

- 2026-09-17：**新增 `toolsmith` 场景包（4 技能，全部自研）** —— 首次补齐「工具与自动化」域。
  `file-organizer` / `batch-renamer` / `format-converter` / `task-scheduler` 四技能均为原创实现，
  共享「只读优先、dry-run 默认、不可逆动作需显式确认」的操作契约。四个脚本仅用标准库实现，
  可选依赖（Pillow / pandoc / ffmpeg / croniter）缺失时均给出针对性安装指引或自动降级。
  各技能 `references/sources-and-methodology.md` 记录了方法论蒸馏来源（如两阶段改名、
  canonicalize-then-check 路径校验、WAL 式变更日志）与所用库的官方文档链接。

- 2026-09-15：**全量测试轮**——三层测试（chains 静态一致性 / 9 编排器 ×19 情景 dry-run /
  139 个本地脚本 ×约 90 用例深测）修复 27 项缺陷（4 P0：paper 13 脚本返回码丢弃致编排层
  门禁被绕过、video 链文件交接断裂、math solver LP 必崩、data_ml 编排器路径错）。链条
  9 域 21 链扩至 12 域 39 链（新增 chat/office/paper 三域），游离技能 53 → 1；12 个
  paper 脚本技能补齐 SKILL.md 并收编进 ai-research-writing 包。详见 docs/FULL-TEST-REPORT.md。

- 2026-09-14（v0.13.x 后期）：新增 `video-design-studio` 包（4 技能，视频前期设计：
  分镜/镜头配方/提示词工程/风格锚定），方法论借鉴 video-storyboard、video-shotcraft、
  visual-skills 等开源项目并已在各技能 references 中署名。
- 2026-09（v0.13.x）：仓库扩至 83 技能 / 21 包。新增 4 个场景包（ai-video-pipeline、
  ai-research-writing、code-planning、data-ml-science）并补齐 36 篇 references；
  重写 CI 为门禁/构建/测试三 job 强制 0 错 0 警；清理孤儿死代码与幽灵技能引用。
- 2026-08-25（0.5.0，旧体系编号 v1.5.0）：恢复 2 个自建场景技能（zhihu-content-manager、cnblogs-skill）并按工程规范改造
  （去私有依赖、修 BOM bug、新增带测试的 zhihu_html_lint.py、删除欺骗性互动话术），
  新增 `content-publishing` 场景包。仓库定位调整为「上游精选 + 自建中文平台场景技能」双轨。
- 2026-08-25（0.4.0，旧体系编号 v1.4.0）：移除 4 个自建 skill（`agent-builder-skill`、`chinese-parents-skill`、
  `cnblogs-skill`、`zhihu-content-manager`）及其场景包（blog-writing、family-communication、
  zhihu-writing）。其中 2 个后于 0.5.0 按新规范恢复。
