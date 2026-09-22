---
name: good-skill
description: 合规技能的最小示范样例——用于演示"通过全部校验"的技能长什么样。供 skill-tester 的文档示例引用与对照学习。
---

# good-skill — 合规技能最小示范

## overview

good-skill 是一个**刻意做到全部合规**的最小技能样例，回答一个问题：
"通过 skill-tester 全部校验的技能，最小长什么样？"

它与 `assets/sample-skill/`（故意带缺陷的反面样例）成对使用：

| 对照项 | good-skill（本样例） | sample-skill（反面样例） |
|---|---|---|
| 校验器结论 | 全部通过，退出码 0 | 多项 FAIL，退出码非 0 |
| 脚本 `__main__` guard | 有 | 缺失 |
| 快速上手章节 | 有（quick start） | 缺失 |
| 用途 | 正面教材：照着写 | 反面教材：练习解读 FAIL |

## quick start

在技能目录内直接运行随包脚本（只依赖标准库）：

```bash
python3 scripts/hello_stats.py 1,2,3.5,4 --json
```

预期输出一段 JSON，包含 `count/mean/median/min/max/stddev` 六个统计量，
退出码 0。人类可读格式（默认）：

```bash
python3 scripts/hello_stats.py 1,2,3.5,4
```

## usage

### 参数说明

| 参数 | 必填 | 说明 |
|---|---|---|
| `numbers` | 是 | 逗号分隔的数字串，如 `1,2,3.5` |
| `--json` | 否 | 输出 JSON 而非表格 |

### 输入缺失时

脚本对空输入/非法数字返回退出码 2 并打印可读错误——这是"合格脚本"
错误处理的示范：**失败也要给出下一步怎么办**。

### 从仓库根运行

本技能被 skill-tester 引用时，命令从本技能目录内执行；
若从仓库根执行，路径为
`skills/programming/ai-engineering/skill-tester/examples/good-skill`。

## 内置验证

- [ ] `python3 scripts/hello_stats.py 1,2,3 --json` 退出码 0，JSON 含 `stats.mean`
- [ ] `python3 scripts/hello_stats.py abc` 退出码 2，stderr 提示示例用法
- [ ] `python3 scripts/hello_stats.py --help` 打印参数说明

## 失败处置

| 现象 | 处置 |
|---|---|
| `No such file or directory` | 确认在 good-skill 目录内执行，或使用仓库根全路径 |
| `invalid literal for float` | numbers 参数里有非数字项；逐段检查逗号分隔内容 |

## 红线

1. **不要把 good-skill 当作功能技能使用**——它只做统计演示，真实需求请用对应领域技能。
2. **不要删除对照关系**——本样例与 sample-skill 的正反对照是 skill-tester 教学的一部分。

## references

校验器关注的三类结构与本样例的对应关系：

### 脚本纪律（scripts/）

- 只用标准库：`argparse/json/sys`——任何第三方 import 都会被 script_tester 标记为
  仓库政策违规。
- 每个脚本有 `if __name__ == "__main__":` guard：被 import 时无副作用。
- 支持 `--help`：argparse 自动提供；这是"脚本自描述"的最低要求。
- 支持 `--json`：机器可读输出是 CI 集成的前提；人类可读输出是排障的前提，
  两者都要有（quality_scorer 的 Code Quality 维度会检查）。
- 错误路径：参数非法 → 退出码 2 + stderr 可读提示；成功路径 → 退出码 0。

### 文档纪律（SKILL.md）

- frontmatter 必填 `name` 与 `description`，与目录名一致。
- 章节齐全：overview / usage / quick start / 内置验证 / 失败处置 / 红线——
  quality_scorer 的 Documentation 与 Usability 维度逐项打分。
- 行数达标：校验器按行数推断 tier（BASIC ≥100 / STANDARD ≥200 / POWERFUL ≥300），
  本样例按 BASIC 撰写。
- 示例命令可复制运行：文档里每条 bash 示例都用随包真实路径。

### 目录纪律

- `README.md` 存在（校验器硬性要求）。
- `scripts/` 至少一个脚本（BASIC）。
- `references/` 可选（WARN 级），本样例以本节代替。
