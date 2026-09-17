---
name: skill-finder
description: >
  Search this repository's skills by keyword, work out which scene pack a set
  of skills belongs to (or suggest an ad-hoc combo with ordering), and print
  repo-wide statistics — all read from the real manifest.json and SKILL.md
  files, never a hardcoded list. Use when the user asks to 找技能 / 搜索技能 /
  有没有做X的技能 / 这几个技能属于哪个包 / 仓库有多少技能 / find a skill /
  which skill does X / search skills / list repo stats. Do NOT use for lint
  compliance (that is skill-linter) or for writing a new skill (skill-author).
license: Apache-2.0
compatibility: Requires python3 (stdlib only); run from the repository root.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: meta
  pattern: single-task
  tier: standard
  verified-date: "2026-09-17"
---

# Skill Finder（技能检索与装配）

三个子命令解决三件事：**找一个能用的技能**（`search`）、**确认几个技能能不能凑成一个包**（`pack`）、**看清仓库家底**（`stats`）。所有数据实时读自 `manifest.json` 与 `skills/**/SKILL.md`，脚本里没有任何硬编码技能名。

与同包技能的边界：`skill-author` 负责生成，`skill-linter` 负责合规判定；本技能只做检索、装配与统计，不改任何文件。

## 输入清单

| 输入 | 必需 | 默认 | 说明 |
|---|---|---|---|
| 子命令 | 是 | — | `search` / `pack` / `stats` 三选一 |
| 关键词 | `search` 必填 | — | 空格可分隔多个词，任一命中即计分 |
| 技能名列表 | `pack` 必填 | — | 一个或多个技能名 |
| 输出格式 | 否 | 文本 | 加 `--json` 得机器可读结果 |
| 结果条数 | 否 | 10 | `search --top N` |
| category 过滤 | 否 | 全部 | `search --category meta` |

输入缺失时一次性问齐：

> 请提供：① 你想找什么（一句话描述即可，我会提炼关键词）；或 ② 想确认哪几个技能的组合；
> 或 ③ 直接看仓库统计。可选告知：是否需要 JSON 输出（默认否）。

## 前置自检

逐条执行，任一失败 → 按处置动作做，然后 STOP：

```bash
# 1. Python 3 可用
python3 --version
# 预期：Python 3.8+。失败→安装 Python 3 后重试；本脚本不用任何第三方库。

# 2. 脚本存在且在仓库内
ls skills/meta/skill-finder/scripts/find_skill.py
# 预期：打印该路径。失败→确认当前在仓库根目录，路径用仓库相对路径。

# 3. manifest.json 可读（检索与统计的数据源）
python3 -c "import json;print(json.load(open('manifest.json'))['version'])"
# 预期：打印版本号（如 0.16.1）。失败→脚本会以退出码 2 结束并提示未找到 manifest.json，STOP 并回报仓库不完整。
```

## 工作流

### 步骤 1：按关键词检索

- **动作**：`python3 skills/meta/skill-finder/scripts/find_skill.py search <关键词>`
- **预期**：打印命中的技能数与前 N 条，每条含分数、技能名、所属包（中文名）、一行简介、仓库相对路径。
- **若失败**：末行提示「未命中」→ 换更短或更通用的词（`PDF` → `pdf`、`短视频生成` → `视频`）；或用 `stats` 看 category 分布后按类别再检索。

### 步骤 2：装配检查

- **动作**：`python3 skills/meta/skill-finder/scripts/find_skill.py pack <技能名...>`
- **预期**：若同属现成包，打印包 id、中文名与包内技能总数，并建议直接用包；否则打印临时组合的执行顺序与依赖说明。
- **若失败**：输出 `⚠ 以下技能不在盘上，已忽略` → 先用 `search` 确认技能名的准确拼写（本仓技能名是 kebab-case，不带空格）；名字全错时退出码 2。

### 步骤 3：仓库统计

- **动作**：`python3 skills/meta/skill-finder/scripts/find_skill.py stats`
- **预期**：打印技能数、包数、含脚本技能数、按 category 与 tier 的分布条形图；若有孤儿技能或悬空引用会显式列出。
- **若失败**：无输出 → 检查是否在仓库根目录；报 `未找到 manifest.json` → 路径错了，STOP。

### 步骤 4：串成可复用的检索结论

- **动作**：把 `search` 命中的技能名喂给 `pack`，确认它们是否已成包；未成包时按输出顺序整理成给用户的建议清单。
- **预期**：给出「路径 + 所属包 + 是否带脚本」三要素齐全的建议。
- **若失败**：`pack` 报大量「不在盘上」→ 说明技能名是从记忆里编的，回到步骤 1 用 `search` 取准确名。

## 相关度算法

打分不引入向量模型，用可解释的加权词频，命中即加分：

| 命中位置 | 权重 | 说明 |
|---|---|---|
| 技能 `name` 含关键词 | +5 | 名称是最强信号 |
| `name` 以关键词开头 | 额外 +3 | `pdf-pipeline` 之于 `pdf` |
| `description` 含关键词 | +3 | description 是路由依据，权重次之 |
| 所属包的 name/description 含关键词 | +2 | 每技能最多计一次，避免包内刷分 |
| 正文含关键词 | +1 | 最弱信号，仅作兜底 |

多关键词时逐词累加后排序；同分按技能名升序，保证结果**可复现**。

## 参数速查表

| 参数 | 取值 | 说明 |
|---|---|---|
| `search <关键词>` | 任意字符串，空格分隔多词 | 任一命中即计分 |
| `--top N` | 整数，默认 10 | 只影响展示条数，不影响命中总数 |
| `--category C` | category 值，如 `meta` | 先过滤再检索 |
| `pack <名...>` | 一个或多个技能名 | 给 1 个时只输出该技能的元信息与归属 |
| `stats` | 无参数 | 统计口径见 `references/repo-map.md` |
| `--json` | 三个子命令均支持 | `search` 返回 `matches[]` 与 `total_matches` |
| 退出码 | 0 / 1 / 2 | 0 成功；1 `search` 未命中；2 参数或数据源错误 |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|---|---|---|
| `search` 报「未命中」并返回 1 | 关键词太窄或用了英文全称 | 缩短关键词、改用中文别名，或先 `stats` 看 category |
| `⚠ 以下技能不在盘上，已忽略：xxx` | 技能名拼写不准或该技能是源码里的占位名 | 用 `search` 取准确名；占位名（如 `references/<文件名>.md` 之类）不是技能 |
| 退出码 2 + 「未找到 manifest.json」 | 不在仓库根目录执行 | `cd` 到仓库根目录后重跑，路径一律用仓库相对路径 |
| `search` 结果里同分技能很多 | 关键词过于泛化（如「生成」） | 加 `--category` 限定，或换成更具体的动作词 |
| `stats` 报大量孤儿技能 | 技能在盘上但未被任何 pack 引用 | 属发布流程问题，报告给用户并建议更新 `manifest.json` 与 `packs/*/pack.json` |
| `stats` 报「包引用了盘上不存在的技能」 | pack 里有悬空引用，CI 会因此报错 | 报告清单与路径，交由发布流程修正；本技能不代改 |
| `--json` 输出被截断 | 结果被重定向到文件但进程被中断 | 重跑并把 stdout 完整重定向；JSON 顶层含 `total_matches` 可校验完整性 |

## 交付标准

- 成功定义：所选子命令退出码为 0（`search` 未命中返回 1 属正常结论，不算失败）。
- 产物：默认打到 stdout；需留档时重定向为 `skill-search-<关键词>-<YYYYMMDD>.json`（加 `--json`）或 `.txt`。
- 存放位置：仓库外或用户指定路径，不要写入 `skills/**`。
- 完整性验证：`search --json` 的 `total_matches` 与 `matches` 长度一致（`--top` 截断时前者更大）；`stats` 输出的技能数与 `find skills -name SKILL.md` 的计数相当（差值为被跳过的 `assets/` 等示例）。

## 参考

- `references/repo-map.md` —— 仓库目录地图与统计口径说明（技能数怎么数、什么被跳过）；解读 `stats` 数字或找不到技能时读。
- `references/sources-and-methodology.md` —— 方法论出处与原创性声明；被问「检索规则哪来的」时读。
