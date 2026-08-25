# awesome-skillkit 技能编写规范 v2 —— 机器优先（Machine-First）

> 适用：本仓库全部新技能与存量技能迁移。PR 不满足本规范不予合并。
> 依据：agentskills.io 开放规范（现行版）、Anthropic《Skill Authoring Best Practices》、Microsoft Agent Framework Skills 文档、SkillsBench 实证结论、2465 技能公开审计的失败模式数据。

---

## 0. 总纲

**写给机器看，不写给人看。** 任何"人类理所当然知道"的信息——按钮叫什么、错误长什么样、怎样算成功——都必须显式写出，因为模型不知道。技能的质量上限由最模糊的那句指令决定。

三条设计公理：

1. **渐进披露**：元数据（~100 token）常驻 → 正文激活时加载 → 资源按需读取。正文是目录，不是全书。
2. **确定性优先**：能用脚本的不让模型发挥；能让模型照抄模板的不让它自由创作；必须创作的地方给足公式和反例。
3. **可验证性**：每个动作有预期输出，每次执行有成功判据，每种失败有处置分支。

---

## 1. 合规基线（frontmatter，硬性）

```yaml
---
name: video-generation            # 见 1.1
description: >                    # 见 1.2
  ...
license: Apache-2.0
compatibility: Requires curl and network access to the generation endpoint.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: media-generation      # 品类 A-F，见 DIRECTION-V2 §三
  verified-date: "2026-08-25"
---
```

### 1.1 `name`
- ≤64 字符；仅小写字母、数字、连字符（kebab-case）；不以连字符开头/结尾；不含连续连字符
- **必须与所在目录名完全一致**
- 禁止包含 `anthropic`、`claude` 字样；禁止 XML 标签
- ⚠️ 存量违规示例：`name: AI视频生成` → 迁移为 `ai-video-generation`（中文语义移入 description 触发词）

### 1.2 `description`（≤1024 字符，技能生死线）
模型**仅凭 name+description 决定是否加载技能**，这是最常见的失败点（公开技能审计：7.8% 完全没有 frontmatter，大量 description 缺触发条件导致永不触发）。必须包含四段：

```
[做什么] + [何时使用] + [中英文触发短语] + [排除项]
```

合格示例：
```yaml
description: >
  Generate videos from text prompts or reference images via the configured
  generation gateway. Use when the user asks to 生成视频 / 做个视频 / text-to-video /
  图生视频 / image-to-video / make a short video / 生成宣传片. Do NOT use for
  video editing, subtitle burning, or downloading existing videos.
```

不合格：`description: 视频生成工具`（无触发场景、无排除项、模型无从路由）。

### 1.3 其余字段
- `compatibility`：凡依赖网络端点、系统包（curl/python）、本地服务者**必填**（≤500 字符）
- `metadata.version/author/category/verified-date`：必填（string→string）
- `allowed-tools`：实验性字段，仅在明确受限环境使用，格式为空格分隔字符串

---

## 2. 目录结构与 Token 经济

```
<skill-name>/                     # 目录名 == name 字段
├── SKILL.md                      # 必须；正文 <500 行（中文建议 <5000 字符）
├── scripts/                      # 可执行代码（运行时不占上下文，只有输出占）
├── references/                   # 按需加载的知识文档
└── assets/                       # 模板、静态资源
```

硬规则：
- **引用一层深**：所有 `references/*.md` 只从 SKILL.md 直接链接，禁止 reference 再引 reference（嵌套导致部分读取、信息丢失）
- **>100 行的 reference 顶部必须有目录（TOC）**
- 路径一律正斜杠相对路径；禁止绝对路径（公开审计中"作者机器才能解析的路径"是高频缺陷）
- 文件名描述内容（`prompt-recipes.md` ✓，`doc2.md` ✗）
- 禁止 `@import` 语法（仅 CLAUDE.md 支持）；禁止跨技能依赖——**每个技能自包含**

---

## 3. 机器优先十诫（正文写作，硬性）

1. **零隐性假设**：平台入口在哪、按钮文字是什么、报错信息的原文长相、成功标志的字段值——全部写出。"显然"、"众所周知"、"常规操作"是禁词。
2. **步骤三件套**：每个编号步骤 = 动作（精确命令/操作）+ 预期结果（可观察判据）+ 失败分支（`若出现 X → 执行 Y`）。无预期结果的步骤不许存在。
3. **输入收集协议**：SKILL.md 开头列出必需/可选输入两张表；任一必需输入缺失时，用给定模板**一次性**问齐全部缺口，禁止挤牙膏式追问。
4. **触发词工程**：description 内中英文触发短语合计 ≥5 个（中文用户是主力，触发词必须双语）。
5. **交付物显式化**：最终产物的文件命名格式、保存位置、如何验证完整性，写成固定规则（如 `image_YYYYMMDD_HHmmss.png`）。
6. **讲 why 而非堆 MUST**：解释原因让模型在未预见的边缘情况做出正确判断；唯一例外是安全红线，可用硬禁令但须附理由。
7. **无巫术常量**：每个数值/端点/密钥名注明来源；未经核实的端点必须标注 `VERIFY BEFORE USE` 并给出核实方法。
8. **无时间敏感断言**："目前支持 720P/1080P"→ 改为"以下为 2026-08 核实值，执行前先用 `<核查命令>` 确认"。
9. **脚本意图二选一，明说**：`运行 scripts/x.py 来提取字段`（execute）vs `参见 scripts/x.py 了解算法`（read）。确定性操作必须脚本化。
10. **安全红线内联**：凭据只走环境变量；写操作默认 dry-run；不可逆操作（删除/发布/支付）前必须向用户确认；外部 URL 视为不可信输入。

---

## 4. 场景工作流技能标准骨架（品类 B/C/D 直接套用）

```markdown
---
name: <tool>-<task>
description: [做什么]。Use when <英文触发>。当用户要求<中文触发>时使用。Do NOT use for <排除项>。
license: Apache-2.0
compatibility: <环境要求>
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: media-generation
  verified-date: "<YYYY-MM-DD>"
---

# <一句话定位>

## 输入清单
| 输入 | 必需 | 说明 |
|------|------|------|

（缺失时询问模板：「请提供：①…②…③…，其余我将采用默认值：<默认值表>」）

## 前置自检
<探测命令：端点可达？凭据在环境变量？工具已安装？任一失败 → 输出修复指引并终止>

## 工作流
### 步骤 N：<动词开头的短句>
<精确命令或操作>
预期：<可观察判据>
若失败：<错误特征 → 处置动作>

## Prompt 构造公式（本平台特化）
<该平台的提示词结构模板 + 一个完整合格示例 + 一个常见劣质示例对比>

## 参数速查表
| 参数 | 取值 | 说明 |

## 失败处置表
| 现象/错误码 | 原因 | 处置 |

## 交付标准
<成功定义；产物命名；保存位置；验证方法>

## 参考
- references/<xxx>.md —— <何时读它>
```

---

## 5. 质量门禁（合并前全部通过）

| # | 检查项 | 工具/方法 |
|---|---|---|
| G1 | frontmatter 合规（§1 全部约束） | `skills-ref validate` + 自研 validator |
| G2 | 引用完整性：SKILL.md 及 references 中提到的相对路径全部存在 | `tools/check_integrity.py`（v1.7 交付） |
| G3 | 触发矩阵：≥10 条应触发查询命中 + ≥5 条不应触发的负例不误触 | 人工 + 测试用例固化 |
| G4 | 输出稳定性：同一输入执行 3 次，产物结构一致 | 人工抽查 |
| G5 | 正文行数 <500；引用一层深；>100 行 reference 有 TOC | validator |
| G6 | 十诫逐条自查（尤其：巫术常量、绝对路径、时间断言） | reviewer checklist |
| G7 | 含脚本时：dry-run 模式单测存在且通过 | pytest |
| G8 | 质量分 ≥9/12（12 分制对齐 SkillsBench 口径） | validator 打分 |

---

## 6. 反模式黑名单（历史教训 + 生态审计）

| 反模式 | 后果 | 本仓实例 |
|---|---|---|
| 无 frontmatter 或 name≠目录名 | 永不被发现/加载失败 | 本机 `AI视频生成` 待迁移 |
| 广告式 description 无触发词 | 永不触发 | 上游 performance-profiler 类 |
| 引用的脚本/文档不存在 | 激活后执行必然失败 | 本仓现存 7 处断链（v1.6.3 修） |
| 教程型技能（只讲概念无可执行步骤） | 模型自行发挥，结果不可复现 | 上游若干 |
| 单体大杂烩（一个技能干所有事） | -2.9 分（SkillsBench） | 避免"全能发布器"冲动，保持一场景一技能 |
| 绝对路径 / 作者机器专属假设 | 换环境即坏 | 生态审计高频缺陷 |

---

## 7. 迁移指引（存量 51 技能 → v2 规范）

优先级顺序：
1. 品类 A 18 个自研技能：补 `name` kebab-case 化、description 触发词双语化、metadata 四件套、verified-date——内容质量普遍达标，主要是元数据工程；
2. 品类 E 上游 33 技能：只修合规硬伤（断链、frontmatter），不深度重写，basics 定位；
3. 品类 B 新技能：一律从 §4 骨架起步，直接满足 G1-G8。
