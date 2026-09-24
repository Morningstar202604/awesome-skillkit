# 仓库地图与统计口径

本文件说明 `find_skill.py` 看到的世界长什么样：哪些目录被扫、什么被跳过、
`stats` 的每个数字怎么算出来。**解读统计数字或「明明有这个技能却搜不到」时读。**

## Table of Contents地图

```
awesome-skillkit/
├── manifest.json          # 唯一权威清单：hub / version / packs[]
├── packs/<pack-id>/pack.json   # 每个包的成员技能名列表（与 manifest 镜像）
├── skills/                # 技能本体，按品类分一级目录
│   ├── meta/              # 元技能（本技能所在，Skill Forge 场景包）
│   ├── programming/       # 软件开发，下分 19 个二级域
│   ├── video/  ppt/  office/  paper/  audio/  design/  education/
│   ├── writing/           # 内容发布，下分 blog/ community/ news/ social/ video/
│   ├── marketing/  memory/  chat/  scenarios/
│   └── _common/           # 跨技能共享模块，不是技能
└── tools/                 # 仓库级门禁与构建脚本，不是技能```

## 什么算一个「技能」

扫描规则：`skills/**/SKILL.md`，**任一层级**都算（发布类技能常见的
`skills/writing/…/csdn-publisher/SKILL.md` 三层深，与 `skills/video/video-generation/SKILL.md`
两层深同等对待）。

以下路径下的 `SKILL.md` 被**跳过**，因为它们不是技能本体：

| 路径片段 | 为什么跳过 |
|---|---|
| `assets/` | 技能自带的示例工程，如 `skill-tester/assets/sample-skill/SKILL.md` |
| `templates/` | 模板文件，非可加载技能 |
| `_common/` | 跨技能共享代码目录 |
| `__pycache__/` | 编译产物 |

因此 `stats` 的技能数会比 `find skills -name SKILL.md` 的原始计数少几个，
差额就是上表这几类。两者对不上不是 bug。

## 每个字段从哪来

| 字段 | 来源 | 缺失时 |
|---|---|---|
| `name` | SKILL.md frontmatter `name` | 回退为目录名 |
| `description` | frontmatter `description` | 空串，检索时该技能只能靠名称与正文命中 |
| `category` / `tier` | frontmatter `metadata.*` | 归入「（未标注）」桶 |
| `title` | 正文第一个 `# ` 一级标题 | 空串 |
| `summary` | 正文首个非标题、非空、非代码块的段落，截断到 80 字符 | 回退为 `title` |
| `has_scripts` | 技能目录下是否存在 `scripts/` 子目录 | 布尔值，无需回退 |
| `has_references` | 是否存在 `references/` 子目录 | 同上 |
| 所属包 | `manifest.json` 的 `packs[].skills[].name` 反向索引 | 空列表 → 计入孤儿 |
| 包中文名 | `packs[].name_zh` | 回退为包 id |

正文与 description 全部 `lower()` 后匹配，因此 `PDF` 与 `pdf` 等价；
中文不受大小写影响，直接子串匹配。

## `stats` 的统计口径

| 指标 | 算法 |
|---|---|
| `skills_on_disk` | 扫到的技能记录数（已按上文规则跳过示例目录） |
| `packs` | `manifest.json` 的 `packs` 数组长度 |
| `skills_referenced_by_packs` | 所有 pack 成员技能名的**去重**集合大小 |
| `skills_with_scripts` | 技能目录含 `scripts/` 的数量 |
| `by_category` | 对 `category` 计数，未标注归入「（未标注）」 |
| `by_tier` | 同上，对 `tier` 计数 |
| `orphan_skills` | 在盘上但不在任何 pack 的 `skills[].name` 里 → WARN 级问题 |
| `pack_references_missing_on_disk` | pack 引用了但盘上找不到 → ERROR 级问题（仓库门禁会拦） |

`skills_on_disk` 通常略大于 `skills_referenced_by_packs`：差值是孤儿技能或新增未入包技能。
两者相等且两个告警列表都为空，说明包 ↔ 磁盘完全一致。

## 检索不到技能时的排查顺序

1. **关键词太窄**：先用 `stats` 看 category 分布，按类别名再搜；
2. **技能名记错了**：本仓技能名全是 kebab-case，不带空格、不带大写，
   如 `video-generation` 而非 `Video Generation`；
3. **该技能在 `assets/` 里**：那是示例，不是可加载技能，搜不到是预期行为；
4. **技能在盘上但不在 `manifest.json`**：`search` 仍能命中（它扫盘），
   但 `pack` 会告诉你它不属于任何包；
5. **技能只在 `manifest.json` 里**：`search` 命不中，且 `stats` 会把它列进
   `pack_references_missing_on_disk`——这是需要修的数据错误。

## 权重设计的取舍

名称权重（5）远高于正文（1），是因为技能名本身就是一次人工压缩：
作者在命名时已经把「这个技能干什么」压进了几个词。description 权重（3）
对应「模型仅凭 name+description 决定是否加载」这一机制。
包描述命中给 +2 且每技能只计一次，是为了让「整包都相关」的情形浮上来，
同时防止同一个包里 20 个技能靠包描述互相刷分淹没真正命中的那个。
