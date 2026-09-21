## 步骤 1：需求澄清

基于您的描述，我推断以下默认值（请确认或修正）：

| 问题 | 您的输入 | 我的推断默认值 |
|---|---|---|
| ① 技能要解决什么具体问题（举一个真实触发场景） | 摄影师导出的 DSC001.jpg 批量改成 2024-10-27_tour_001.jpg | ✓ 已明确 |
| ② 什么时候该触发 / 绝对不该触发 | 用户明确说批量改名/重命名时触发；单文件改名、移动目录不触发 | ✓ 已明确 |
| ③ 需要脚本吗？ | — | 是（Python 3.10+，跨平台） |
| ④ 产出物形态 | — | `skills/filesystem/batch-rename/` 下的 `SKILL.md` |
| ⑤ 失败了怎么办 | — | 预览失败→停下问人；apply 失败→按条目跳过并记录到 rename-log，不整体回滚 |

---

## 步骤 2：命名与描述

**名称**：`batch-file-rename`（可检索动作短语，符合 kebab-case）

**触发词（中英双语 ≥5 个）**：
- 批量改名 / batch rename / 按规则重命名 / 重命名文件 / 批量重命名 / bulk rename files / 预览并改名

**description**：
> Batch rename files in a directory using rules (template, regex, prefix/suffix, or EXIF date). Always requires explicit user confirmation after preview before applying. Use when: user asks to batch rename / 批量改名 / 按规则重命名 / 批量重命名 files in a folder, or mentions renaming DSC001.jpg-style patterns. Do NOT use for: single file rename (use mv/rename directly), moving files between directories, or any operation on system/read-only directories. First verify dry-run output with user before executing actual renames.

---

## 步骤 3：骨架生成

现在生成 SKILL.md 文件：

```markdown
---
name: batch-file-rename
description: >
  Batch rename files in a directory using rules (template, regex, prefix/suffix,
  or EXIF date). Always requires explicit user confirmation after preview before
  applying. Use when: user asks to batch rename / 批量改名 / 按规则重命名 /
  批量重命名 files in a folder, or mentions renaming DSC001.jpg-style patterns.
  Do NOT use for: single file rename (use mv/rename directly), moving files
  between directories, or any operation on system/read-only directories.
  First verify dry-run output with user before executing actual renames.
license: Apache-2.0
compatibility: Pure script; Python 3.10+, cross-platform (Windows/macOS/Linux).
metadata:
  author: "Sapiens AI"
  version: "1.0.0"
  category: filesystem
  pattern: tool-encapsulation
  tier: standard
  verified-date: "2026-09-17"
---

# 批量文件重命名（含预览与撤销）

把「按规则批量重命名文件夹内文件」变成一次可审计的操作：先 dry-run 预览新旧文件名对照，用户确认后正式执行，并输出 rename-log 用于事后核查。本技能**不移动文件位置**、**不改系统目录**、**不处理单文件**。

## 输入清单

| 输入 | 必需 | 默认 | 说明 |
|---|---|---|---|
| 目标目录路径 | 是 | — | 绝对路径或相对路径，如 `~/photos/2024-10` |
| 重命名规则类型 | 是 | template | 可选：`template`（模板）/ `regex`（正则替换）/ `prefix`（前缀）/ `suffix`（后缀）/ `exif`（按 EXIF 日期） |
| 规则参数 | 是 | — | 依类型而定，见「命令速查表」 |
| 是否包含子目录 | 否 | false | `--recursive` 时才遍历子目录 |
| 覆盖已有同名文件 | 否 | false | 默认跳过并报错，不静默覆盖 |
| 日志输出路径 | 否 | `<目标目录>/rename-log-<时间戳>.csv` | 记录每次改名的原始名、新名、状态 |

**边界判定**：
- 触发条件：用户明确提到「批量改名」「重命名文件」「批量重命名」等表述，且涉及≥2个文件。
- 不触发条件：单文件改名（直接建议用 `mv` 或 `rename` 命令）、移动文件到不同目录（用 `mv`）、修改系统目录（直接拒绝）。

## 前置自检

逐条执行，任一失败 → 按处置动作做，然后 STOP：

```bash
# 1. Python 3.10+ 可用
python3 --version
# 预期：Python 3.10.x 或更高。失败→提示用户安装 Python 3.10+，STOP。

# 2. 目标目录存在且是普通目录（非系统目录）
python3 -c "import os, pathlib; p=pathlib.Path('$TARGET_DIR'); print('OK' if p.is_dir() and not str(p).startswith(('/usr', '/bin', '/System', 'C:\\Windows')) else 'REJECTED')"
# 预期：打印 OK。失败→检查路径是否正确，或提示用户避免系统目录，STOP。

# 3. 目标目录有写权限
python3 -c "import os; print('OK' if os.access('$TARGET_DIR', os.W_OK) else 'READONLY')"
# 预期：打印 OK。失败→提示目录只读，STOP。

# 4. 无正在进行的同名批量重命名任务（可选：检测临时锁文件）
ls "$TARGET_DIR"/.batch-rename-lock 2>/dev/null && echo "LOCKED" || echo "OK"
# 预期：打印 OK。失败→提示先清理锁文件或等待上一个任务结束。
```

## 工作流

### 步骤 1：解析规则与构建映射

- **动作**：根据输入的规则类型和参数，解析出每个源文件的预期新文件名，生成「原始名→新名」映射表。若规则引用 EXIF，则读取文件元数据。
- **预期**：映射表长度等于目标目录内匹配文件数（或子集，若有过滤条件）；每条映射有明确的来源规则。
- **若失败**：规则语法错误（如正则无效、模板缺占位符）→ 输出具体错误行号与修复建议，STOP 让用户修正规则。

### 步骤 2：Dry-run 预览

- **动作**：以 CSV 格式输出预览清单，列包含：`original_name`, `new_name`, `rule_applied`, `status`（pending）。同时计算冲突检测（新名是否已存在或其他源文件也指向同一新名）。
- **预期**：预览文件保存至 `<目标目录>/rename-preview-<时间戳>.csv`；