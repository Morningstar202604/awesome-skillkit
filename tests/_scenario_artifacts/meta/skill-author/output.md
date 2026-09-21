# 步骤 1：前置自检

```bash
# 1. Python 3 可用
python3 --version
# 预期：Python 3.10+

# 2. 目标目录尚不存在
ls skills/writing/file/批量按规则重命名文件-含预览与撤销 2>/dev/null || echo "OK-NEW"
# 预期：OK-NEW

# 3. 名称未被仓库占用
grep -rn "^name: batch-file-renamer$" skills/ | head
# 预期：无输出
```

# 步骤 2：命名与描述

**名称**：`batch-file-renamer`

**描述**：
```yaml
name: batch-file-renamer
description: >
  批量按规则重命名文件，支持预览清单与撤销日志。
  Use when: 用户说批量改名、重命名一批文件、按模板改文件、批量重命名、preview rename、undo rename、DSC001改成日期、文件名加前后缀、批量修改文件名模式。
  中文触发词：批量改名、批量重命名、按规则改文件名、生成预览清单、撤销批量改名、文件名模板、正则重命名、EXIF日期提取、前后缀批量添加。
  Do NOT use for: 单个文件改名（用 mv/rename）、移动文件到目录、重命名文件夹、处理手写 CSV/Excel、解析 PDF 文本、生成文件名列表而不执行改名。
```

# 步骤 3：骨架生成

```bash
mkdir -p skills/writing/file/批量按规则重命名文件-含预览与撤销/scripts
mkdir -p skills/writing/file/批量按规则重命名文件-含预览与撤销/references
```

**SKILL.md 内容**：

```markdown
---
name: batch-file-renamer
description: >
  批量按规则重命名文件，支持预览清单与撤销日志。
  Use when: 用户说批量改名、重命名一批文件、按模板改文件、批量重命名、preview rename、undo rename、DSC001改成日期、文件名加前后缀、批量修改文件名模式。
  中文触发词：批量改名、批量重命名、按规则改文件名、生成预览清单、撤销批量改名、文件名模板、正则重命名、EXIF日期提取、前后缀批量添加。
  Do NOT use for: 单个文件改名（用 mv/rename）、移动文件到目录、重命名文件夹、处理手写 CSV/Excel、解析 PDF 文本、生成文件名列表而不执行改名。
license: Apache-2.0
compatibility: Pure prompt-based; optional python3 for the self-check step.
metadata:
  author: "Sapiens AI"
  version: "1.0"
  category: writing
  pattern: single-task
  tier: standard
  verified-date: "2026-09-17"
---

# 批量按规则重命名文件（含预览与撤销）

把一个模糊的「把这一堆 DSC001.jpg 按日期改成 2024-10-27_tour_001.jpg」变成一份可执行的批量改名方案：先解析规则、再生成预览清单让用户确认、执行改名并记录日志、支持撤销。

本技能**不处理单文件改名**（交给 `mv`/`rename`）、**不移动文件**、**不处理文件夹**。红线是必须先预览再 apply，绝不碰系统目录与只读盘。

## 输入清单

| 输入 | 必需 | 默认 | 说明 |
|---|---|---|---|
| 目标目录 | 是 | — | 要批量改名的文件夹路径 |
| 规则类型 | 是 | — | 模板 / 正则 / 前后缀 / EXIF 日期 |
| 规则详情 | 是 | — | 如 `{date}_{tour}_{seq}`、正则替换表达式等 |
| 是否含脚本 | 否 | 有脚本 | 推荐用脚本保证幂等与安全 |
| 产物形态 | 否 | 文本 + 日志 | 预览清单文件 + rename-log.json |
| 创作者署名 | 否 | 仓库默认 | `metadata.author` |

必需项缺失时**在一次提问里问齐 5 个问题**：

> 请提供：① 目标目录路径？② 规则类型（模板/正则/前后缀/EXIF日期）？③ 规则详情是什么？④ 需要脚本吗（有则说明输入输出格式）？⑤ 失败了怎么办（重试/降级/停下问人）？

## 前置自检

逐条执行，任一失败 → 按处置动作做，然后 STOP：

```bash
# 1. Python 3.10+ 可用（脚本型技能需要）
python3 --version
# 预期：Python 3.10+。失败→脚本型技能 STOP，改用纯提示型。

# 2. 目标目录存在且可写
ls <target-dir> 2>/dev/null && test -w <target-dir> && echo "OK" || echo "FAIL"
# 预期：OK。失败→问用户是否选错目录或权限不足，STOP。

# 3. 目标目录非系统目录、非只读盘
realpath <target-dir>
# 预期：不是 /usr /system /boot 等系统路径，且 mount 非 readonly。
# 失败→STOP，报安全红线。
```

## 工作流

### 步骤 1：规则解析（一次性解析，给出候选）

- **动作**：根据用户给的规则类型解析规则，列出所有会匹配的文件及新文件名候选。
- **预期**：输出「候选清单」（旧名 → 新名），行数 ≤ 1000；若超 1000 行提示用户拆分任务。
- **若失败**：规则语法错误 → 报错原文展示，问用户修正；无法解析 → STOP，建议改用更简单的规则。

### 步骤 2：预览清单生成（必须，不可跳过）

- **动作**：把候选清单写入 `preview-<timestamp>.md`，格式为：
  ```
  ## 预览清单（时间戳：2024-10-27T10:00:00Z）
  | 原文件名 | 新文件名 | 变更说明 |
  |---|---|---|
  | DSC001.jpg | 2024-10-27_tour_001.jpg | EXIF日期 + 模板 |
  ```
- **预期**：文件存在于目标目录，用户可打开审阅。
- **若失败**：写入失败 → 提示用户检查磁盘空间，STOP。

### 步骤 3：用户确认（红线内联）

- **动作**：要求用户明确说「确认执行」或「apply」后才继续。
- **预期**：用户回复确认词。
- **若失败**：用户未确认或说「取消」→ STOP，不执行任何写操作。

### 步骤 4：执行改名（dry-run 默认，execute 显式）

- **动作**：运行脚本 `python3 scripts/batch_rename.py