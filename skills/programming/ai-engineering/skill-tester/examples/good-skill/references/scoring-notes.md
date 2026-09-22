# 评分器怎么给分（作者视角速查）

quality_scorer.py 的四个维度各占 25%。本文件记录每个维度的检查点，
写新技能时按此自检，避免反复试错。

## Documentation（文档 40% SKILL.md + 25% README + 20% references + 15% 其他）

- SKILL.md 深度：行数（300 行满分）、frontmatter 完整、代码块数量（4 个满分）。
- README：字符数分档（<200 字符只有 45 分，≥1000 字符 95 分）——所以 README
  要写实内容，不要一句话占位。
- references/：≥2 个文件且合计 ≥2000 字符拿 90 分——设计说明、速查表都算。

## Code Quality（脚本质量）

- 脚本平均 LOC 太薄会扣分（avg <100 LOC 记 "Scripts are thin"）。
- 每个脚本都要支持 --json 与人类可读两种输出。
- 脚本须有 __main__ guard、--help、stdlib-only。

## Completeness（完备性）

- scripts/ 数量、tests/ 自动化测试目录、assets/ 样例数据、
  expected_outputs/ golden 输出、references/ 说明文档——五类都查。

## Usability（易用性）

- Quick Start / Usage 章节存在性、示例是否可复制运行。

## 退出码语义（CI 视角）

| 脚本 | 全部通过 | 发现问题 |
|---|---|---|
| skill_validator.py | 0 | 1 |
| script_tester.py | 0 | 1 |
| quality_scorer.py --minimum-score N | 0 | 2（评分低于 N） |
| audit_skills.py | 0 | 1（仅 --fail-under 时） |

这就是为什么文档示例要指向 good-skill：它保证示例命令退出码为 0，
读者复制运行不会被"预期内的失败"绊住。
