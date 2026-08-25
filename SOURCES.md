# SOURCES — 技能来源与更新指引 / Skill Sources & Updates

> 本仓库维护两条线：
> 1. **上游精选**（`skills/programming/`，33 个）——全部来自下方上游项目；
> 2. **自建场景技能**（`skills/writing/`，18 个）——中文平台自动化知识，本仓库原创维护。

## 上游仓库 / Upstream（skills/programming/）

| 项目 | 地址 | 协议 |
|------|------|------|
| alirezarezvani/claude-skills | <https://github.com/alirezarezvani/claude-skills> | MIT |

- 收录数量：**33 个 skill**（全部来自上述上游）。
- 与上游的差异：上游两个近似重复项 `database-schema-designer`、`agent-workflow-designer`
  已合并进同源兄弟 skill，其独有内容以参考文档形式保留在对应 skill 内。

## 更新方法 / How to update

```bash
# 1. 拉取上游最新版
git clone https://github.com/alirezarezvani/claude-skills.git D:\_upstream\claude-skills
#    （已克隆过则：git -C D:\_upstream\claude-skills pull）

# 2. 把需要更新的 skill 文件夹覆盖到本仓库对应位置
#    skills/programming/<分类>/<skill-name>/...

# 3. 校验 manifest.json 中该 skill 的条目仍一致（名称、分类）

# 4. 重新打包发布
python build.py          # 或 bash build.sh
```

## 自建场景技能 / Self-authored scenarios（skills/writing/）

| Skill | 场景包 | 说明 |
|-------|--------|------|
| zhihu-content-manager | content-publishing | 知乎发布/编辑/删除/乱码修复 + HTML lint 门禁 |
| cnblogs-skill | content-publishing | 博客园 API 发文全流程 + 预发布格式检查 |
| wechat-mp-publisher | content-publishing | 公众号官方草稿箱/发布 API，默认 dry-run |
| juejin-publisher | content-publishing | 掘金 Web 接口发布（端点需按文档核对） |
| cross-post-orchestrator | content-publishing | 多平台编排：计划→调度→台账 |
| ai-cover-generator | content-publishing | 对接本地图片服务的封面图生成 |
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

这 18 个技能不来自上游，由本仓库原创维护，更新即改本仓库。

## 共享工具 / Shared helper

| 模块 | 说明 |
|------|------|
| `skills/writing/_common/publish_common.py` | 发布类脚本共用的 HTTP/dry-run/凭据逻辑；被 wechat / juejin / ai-cover-generator 复用，避免重复造轮子。非技能（无 SKILL.md），不计入技能数。 |

## 全部技能清单（33）

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

## 历史 / History

- 2026-08-25（v1.5.0）：恢复 2 个自建场景技能（zhihu-content-manager、cnblogs-skill）并按工程规范改造
  （去私有依赖、修 BOM bug、新增带测试的 zhihu_html_lint.py、删除欺骗性互动话术），
  新增 `content-publishing` 场景包。仓库定位调整为「上游精选 + 自建中文平台场景技能」双轨。
- 2026-08-25（v1.4.0）：移除 4 个自建 skill（`agent-builder-skill`、`chinese-parents-skill`、
  `cnblogs-skill`、`zhihu-content-manager`）及其场景包（blog-writing、family-communication、
  zhihu-writing）。其中 2 个后于 v1.5.0 按新规范恢复。
