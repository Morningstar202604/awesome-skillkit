我将为你创建一个批量文件重命名技能的 SKILL.md 文档。首先进行前置自检，然后按照工作流逐步生成文档。

```bash
# 1. Python 3 可用性检查
python3 --version
```

```
Python 3.10.12
```

```bash
# 2. 检查目标目录是否已存在
ls skills/automation/file-renamer 2>/dev/null || echo "OK-NEW"
```

```
OK-NEW
```

```bash
# 3. 检查名称是否已被占用
grep -rn "^name: file-renamer$" skills/ | head
```

```bash
# 创建技能目录结构
mkdir -p skills/automation/file-renamer/scripts
mkdir -p skills/automation/file-renamer/references
```

现在我将创建 SKILL.md 文档：