我将为您生成「批量按规则重命名文件」技能的 SKILL.md。先执行前置自检并收集必要信息。

## 前置自检

```bash
# 1. Python 3 版本检测
python3 --version
# 预期：Python 3.10+

# 2. 目标目录检查
ls skills/files/ | grep file-renamer || echo "OK-NEW"
# 预期：目录不存在

# 3. 名称占用检查
grep -rn "^name: file-renamer$" skills/ | head
# 预期：无输出
```

请确认：
1. **技能位置**：建议 `skills/files/file-renamer/SKILL.md`，是否接受？
2. **脚本依赖**：需要 Python 3.10+ 标准库（os/pathlib/exifread），是否需要额外依赖检测？
3. **创作者署名**：默认 `Sapiens AI`，是否修改？

现在生成 SKILL.md：

```markdown
---
name: file-renamer
description: >
  批量按规则重命名文件，支持预览与撤销。Use when: 用户要求批量重命名/重命名多个文件/按模板改名。
  触发词：批量重命名、按规则改名、文件重命名、rename batch。
  Do NOT use for: 单文件改名、移动目录、修改文件内容。
license: Apache-2.0
compatibility: Pure prompt-based; optional python3 for the self-check step.
metadata:
  author: "Sapiens AI"
  version: "1.0"
  category: files
  pattern: single-task
  tier: standard
  verified-date: "2026-09-17"
---

# 文件批量重命名技能

把「批量重命名文件」的模糊需求变成可执行的操作清单：先预览规则、再确认、后执行，全程可撤销。产出物是预览清单与 rename-log，不是散文。

本技能**不处理单文件**（交给用户手动）、**不跨目录移动**、**不修改文件内容**。

## 输入清单

| 输入 | 必需 | 默认 | 说明 |
|---|---|---|---|
| 目标目录路径 | 是 | — | 如 `/photos/2024/tour` 或 `D:\pics` |
| 重命名规则 | 是 | — | 模板（`{date}_{tour}_{num}.jpg`）、正则、前后缀或 EXIF 日期 |
| 预览模式 | 否 | 开启 | 必须先预览，用户确认后才 apply |
| 安全边界检查 | 是 | 自动 | 拒绝系统目录、只读盘、当前工作目录 |

必需项缺失时**在一次提问里问齐**：

> 请提供：① 目标目录的完整路径？② 重命名规则（示例：`2024-10-27_tour_001.jpg` 模板）？③ 是否要预览模式？

## 前置自检

逐条执行，任一失败 → 按处置动作做，然后 STOP：

```bash
# 1. Python 3.10+ 可用
python3 --version
# 预期：Python 3.10+。失败→STOP，提示升级 Python。

# 2. 目标目录存在且可读
test -d "<目标目录>" && echo "OK-DIR" || echo "FAIL-DIR"
# 预期：打印 OK-DIR。失败→STOP，提示检查路径。

# 3. 非系统目录/只读盘
case "<目标目录>" in
  /|/bin|/etc|/usr|/lib|/sbin|/boot) echo "FAIL-SYSTEM" ;;
  *) echo "OK-NOT-SYSTEM" ;;
esac
# 预期：非系统路径。失败→STOP，红线内联。
```

## 工作流

### 步骤 1：规则解析与校验

- **动作**：解析用户提供的重命名规则，转换为内部格式。支持：
  - 模板：`{date}_{tour}_{num}.jpg` → 使用 EXIF 日期填充
  - 正则：提取现有文件名模式
  - 前后缀：追加/删除固定字符串
- **预期**：规则合法，无歧义。
- **若失败**：规则语法错误 → 列出错误位置，请用户修正。

### 步骤 2：文件扫描与预览

- **动作**：扫描目标目录下所有匹配文件，生成预览清单：
  ```
  原文件名 → 新文件名
  DSC001.jpg → 2024-10-27_tour_001.jpg
  DSC002.jpg → 2024-10-27_tour_002.jpg
  ...
  ```
- **预期**：预览清单完整，行数 = 匹配文件数。
- **若失败**：权限不足 → 提示检查目录权限。

### 步骤 3：用户确认

- **动作**：展示预览清单，询问用户：
  > 共 N 个文件将重命名，确认后执行。输入 YES 继续，或提供修改意见。
- **预期**：用户明确确认或提出修改。
- **若失败**：超时/无响应 → 保持预览状态，不执行。

### 步骤 4：执行重命名

- **动作**：逐文件执行重命名，记录操作日志到 `<目录>/rename-log-<时间戳>.txt`：
  ```
  [2024-10-27 14:30:00] RENAME: DSC001.jpg → 2024-10-27_tour_001.jpg
  [2024-10-27 14:30:01] RENAME: DSC002.jpg → 2024-10-27_tour_002.jpg
  ...
  ```
- **预期**：所有文件成功重命名，日志写入。
- **若失败**：单个文件失败 → 记录错误，继续处理其他文件，最后汇总。

### 步骤 5：撤销能力验证

- **动作**：向用户说明撤销方法：
  > 如需撤销，使用命令：`cat <日志文件> | while read line; do mv <新文件名> <原文件名>; done`
- **预期**：撤销路径清晰可执行。
- **若失败**：日志缺失 → 提示无法自动撤销，需手动恢复。

## 交付标准

- 成功定义：预览清单已展示、用户已确认、重命名已完成、日志已写入。
- 产物文件：
  - 预览清单：终端输出或 `<目录>/preview.txt`
  - 操作日志：`<目录>/rename-log-<YYYYMMDD-HHmmss>.txt`
- 完整性验证：
  - `wc -l <日志文件>` > 0
  - `grep "RENAME:" <日志文件>` 行数 = 处理文件数
  - 原文件名已不存在，新