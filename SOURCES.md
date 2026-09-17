# SOURCES — 技能来源与更新指引 / Skill Sources & Updates

> 本仓库维护两条线（截至 v0.13，共 **112 个技能 / 27 个场景包**）：
> 1. **上游精选**（`skills/programming/` 下 13 个分类目录，33 个）——全部来自下方上游项目；
> 2. **自建场景技能**（79 个）——分布在 `skills/writing/`、`skills/video/`、`skills/scenarios/`、
>    `skills/paper/`、`skills/ppt/` 及 `skills/programming/` 下的 5 个自建子目录
>    （`data/`、`debug/`、`math/`、`ml/`、`planning/`），本仓库原创维护。

## 上游仓库 / Upstream（skills/programming/ 的 13 个分类目录）

| 项目 | 地址 | 协议 |
|------|------|------|
| alirezarezvani/claude-skills | <https://github.com/alirezarezvani/claude-skills> | MIT |

- 收录数量：**33 个 skill**（全部来自上述上游）。
- 与上游的差异：上游两个近似重复项 `database-schema-designer`、`agent-workflow-designer`
  已合并进同源兄弟 skill，其独有内容以参考文档形式保留在对应 skill 内。
- ⚠️ 注意：`skills/programming/` 下的 `data/`、`debug/`、`math/`、`ml/`、`planning/`
  五个目录是**自建**技能（共 12 个），不属于上游——更新上游时请勿覆盖。

## 更新方法 / How to update

```bash
# 1. 拉取上游最新版
git clone https://github.com/alirezarezvani/claude-skills.git D:\_upstream\claude-skills
#    （已克隆过则：git -C D:\_upstream\claude-skills pull）

# 2. 把需要更新的 skill 文件夹覆盖到本仓库对应位置
#    skills/programming/<分类>/<skill-name>/...
#    （仅限上游 13 个分类目录，勿碰 data/debug/math/ml/planning）

# 3. 校验 manifest.json 中该 skill 的条目仍一致（名称、分类）

# 4. 重新打包发布
python3 build.py         # 唯一构建入口
```

## 自建场景技能 / Self-authored scenarios（79 个）

### 内容发布与写作（skills/writing/，22 个）

| Skill | 场景包 | 说明 |
|-------|--------|------|
| zhihu-content-manager | content-publishing | 知乎发布/编辑/删除/乱码修复 + HTML lint 门禁 |
| cnblogs-skill | content-publishing | 博客园 API 发文全流程 + 预发布格式检查 |
| wechat-mp-publisher | content-publishing | 公众号官方草稿箱/发布 API，默认 dry-run |
| juejin-publisher | content-publishing | 掘金 Web 接口发布（端点需按文档核对） |
| cross-post-orchestrator | content-publishing | 多平台编排：计划→调度→台账 |
| ai-cover-generator | content-publishing / ai-media-toolkit | 对接本地图片服务的封面图生成 |
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

### AI 视频（skills/video/，14 个）

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
| shot-recipe-designer | video-design-studio | 12 张配方卡组装镜头清单 |
| video-prompt-engineer | video-design-studio | 跨模型视频提示词工程 + 六槽位结构审计 |
| visual-style-anchor | video-design-studio | 风格锚 + 角色一致性卡 |

### 编程自建（skills/programming/ 下 5 个目录，12 个）

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

### 办公/研究/娱乐（skills/scenarios/ + skills/paper/ + skills/ppt/，6 个）

| Skill | 场景包 | 说明 |
|-------|--------|------|
| paper-topic-selector | ai-research-writing | 论文选题评估 |
| ppt-builder | office-productivity | PPT 生成（python-pptx） |
| excel-assistant | office-productivity | Excel 处理（openpyxl/pandas） |
| meeting-notes | office-productivity | 会议纪要 |
| resume-tailor | office-productivity | 简历定制 |
| music-generation | ai-media-toolkit | 音乐生成 |

### AI 对话/设计/营销/教育（skills/chat/ + skills/design/ + skills/audio/ + skills/marketing/ + skills/education/，13 个）

| Skill | 场景包 | 说明 |
|-------|--------|------|
| chat-prompt-engineer | chat-prompt-craft | 对话助手提示词工程（豆包/ChatGPT/Kimi 等：五要素公式 + 智能体五段骨架 + 结构审计） |
| design-brief-interpreter | visual-design-studio | 模糊需求 → 7 字段设计规格单（链条入口） |
| image-prompt-engineer | visual-design-studio | 五段式文生图 prompt（含文字渲染铁律与模型方言） |
| layout-spec-auditor | visual-design-studio | 平台版面规格审计脚本（比例/分辨率/安全区/文字预算） |
| podcast-producer | audio-studio | 播客分段脚本（纯口播词纪律 + TTS 安全 lint） |
| tts-voice-director | audio-studio | 跨引擎声音目录选角 + ffmpeg 拼接计划 |
| episode-publisher | audio-studio | shownotes + 时间戳章节 + 平台元数据 + AI 披露 |
| product-copywriter | growth-marketing | 转化框架商品文案（FAB/PAS/AIDA + 异议处理 + 广告法卫生） |
| campaign-designer | growth-marketing | 营销日历 + 渠道矩阵 + 单变量 A/B 变体对 |
| channel-adapter | growth-marketing | 渠道适配（内置约束表 + channel_fit_check.py 校验） |
| course-designer | edu-craft | 学习契约 + checkpoint 依赖排序课程设计 |
| exercise-generator | edu-craft | 开放题严格题库（禁选择题，附评分标准与 lint） |
| feynman-explainer | edu-craft | 费曼六拍补救伴学（诊断→修复→回讲→迁移） |

### 学术论文工具（skills/paper/，12 个）

| Skill | 场景包 | 说明 |
|-------|--------|------|
| lit-review | ai-research-writing | 文献检索+关系图谱+总结（--arxiv 为离线 mock，输出须标注模拟数据） |
| experiment-runner | ai-research-writing | 实验多轮运行+统计检验（实验体为 mock 逻辑，同上） |
| figure-maker | ai-research-writing | bar/line/boxplot 论文图表（heatmap 未实现，诚实返回 unsupported） |
| arch-diagram | ai-research-writing | 架构/框架图 TikZ+SVG（学习自 torchdiagram / archscope / PlotNeuralNet） |
| neural-net-draw | ai-research-writing | 神经网络结构图 TikZ（学习自 PlotNeuralNet） |
| latex-formatter | ai-research-writing | LaTeX 格式化+编译前检查（缺文件 rc=1 门禁语义） |
| self-reviewer | ai-research-writing | 模拟审稿 ready/needs_work 结构判定 |
| journal-adapt | ai-research-writing | IEEE/ACM/NeurIPS/ACL/Nature/Cell 适配+禁用语筛查（学习自 Awesome-Journal-Skills） |
| anti-defensive | ai-research-writing | 防御性学术写作检测修复（学习自 anti-defensive-writing） |
| ai-humanizer | ai-research-writing | 去 AI 痕迹保学术声音（学习自 academic-humanizer） |
| tex-cleaner | ai-research-writing | arXiv 提交前清理五类检查（学习自 arxiv-latex-cleaner） |
| pub-plotter | ai-research-writing | SciencePlots 风格学术图（学习自 garrettj403/SciencePlots） |

以上 79 个技能不来自上游，由本仓库原创维护，更新即改本仓库。

## 全部技能清单（112 = 上游 33 + 自建 79）

### 上游精选（33）

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
| 14 | pr-review-expert | code-review, github-workflow | 同上 |
| 15 | code-reviewer | code-review | 同上 |
| 16 | tech-debt-tracker | code-review | 同上 |
| 17 | dependency-auditor | code-review | 同上 |
| 18 | docker-development | containers | 同上 |
| 19 | helm-chart-builder | containers | 同上 |
| 20 | kubernetes-operator | containers, infrastructure | 同上 |
| 21 | database-designer | database | 同上 |
| 22 | sql-database-assistant | database | 同上 |
| 23 | git-worktree-manager | github-workflow | 同上 |
| 24 | changelog-generator | github-workflow | 同上 |
| 25 | incident-commander | incident-response | 同上 |
| 26 | runbook-generator | incident-response | 同上 |
| 27 | slo-architect | incident-response | 同上 |
| 28 | terraform-patterns | infrastructure | 同上 |
| 29 | observability-designer | infrastructure | 同上 |
| 30 | performance-profiler | performance | 同上 |
| 31 | secrets-vault-manager | security | 同上 |
| 32 | env-secrets-manager | security | 同上 |
| 33 | tdd-guide | tdd | 同上 |

> 注：`skill-tester/assets/sample-skill/` 是 skill-tester 自带的示例资产，不算独立 skill。

### 自建（79）

按上文"自建场景技能"四个小节的表格为准，此处不重复罗列。
单一事实来源是 `manifest.json`（由 `build.py` 从 `packs/*/pack.json` 自动同步）。

## 共享工具 / Shared helpers

| 模块 | 说明 |
|------|------|
| `skills/writing/_common/publish_common.py` | 发布类脚本共用的 HTTP/dry-run/凭据逻辑；被 wechat / juejin / ai-cover-generator 复用，避免重复造轮子。非技能（无 SKILL.md），不计入技能数。 |
| `skills/writing/writing_pipeline.py` | 写作域编排器：选题→大纲→初稿→编辑→SEO→发布 |
| `skills/video/video_pipeline.py` | 视频域编排器：脚本→配音→口型→剪辑→字幕→封面 |
| `skills/paper/paper_pipeline.py` | 论文域编排器 |
| `skills/ppt/ppt_pipeline.py` | PPT 域编排器 |
| `skills/programming/math/math_pipeline.py` | 数学建模域编排器：建模→求解→仿真→可视化 |
| `skills/programming/planning/pipeline_orchestrator.py` | 代码计划域编排器：意图→计划→生成 |

## 历史 / History

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
