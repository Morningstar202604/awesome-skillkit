# good-skill

合规技能的最小示范样例（与 `assets/sample-skill/` 反面样例成对使用）。

## 这是什么

good-skill 回答一个具体问题："通过 skill-tester 全部校验的技能，最小长什么样？"
它被 skill-tester 的文档示例引用，作为"审计一个合格技能"的目标；
同时它本身就是一份**可运行的写作模板**——新技能作者可以从复制本目录开始。

对照关系：

| 对照项 | good-skill（本样例） | sample-skill（反面样例） |
|---|---|---|
| 校验器结论 | 全部通过，退出码 0 | 多项 FAIL，退出码非 0 |
| 脚本 `__main__` guard | 有 | 缺失 |
| 快速上手章节 | 有（quick start） | 缺失 |
| 自动化测试 | tests/ 有 unittest | 无 |
| 用途 | 正面教材：照着写 | 反面教材：练习解读 FAIL |

## 目录结构

```
good-skill/
├── SKILL.md              # 技能主文档（frontmatter + 章节 + 可运行示例）
├── README.md             # 本文件
├── scripts/
│   └── hello_stats.py    # 演示脚本（纯标准库，150+ 行）
├── tests/
│   └── test_hello_stats.py  # unittest 自动化测试
├── expected_outputs/
│   └── sample_numbers_stats.json  # golden 输出（供 script_tester 比对）
├── assets/
│   └── sample_numbers.txt   # 样例输入数据
└── references/
    └── notes.md          # 设计说明
```

## 快速验证

在本目录内执行：

```bash
python3 scripts/hello_stats.py 1,2,3.5,4 --json
python3 -m unittest discover tests
```

第一条命令输出统计 JSON（退出码 0）；第二条跑 10 个单元测试（全部通过）。

## 作为模板使用

1. 复制本目录为新技能目录，改目录名与 frontmatter 的 `name`。
2. 把 `scripts/hello_stats.py` 换成你的真实脚本——保留五条纪律：
   stdlib-only、`__main__` guard、`--help` 自描述、`--json` 机器可读、
   错误路径退出码非 0 且提示可读。
3. 按你的功能重写 SKILL.md 各章节，**每条示例命令都必须可复制运行**。
4. 用 `python3 ../../scripts/skill_validator.py . --json` 自检，
   直到 `compliance_level` 不为 FAIL。

## 相关文档

- 详细设计说明见 [references/notes.md](references/notes.md)
- 五条脚本纪律的逐条解释见 [SKILL.md](SKILL.md) 的 references 节
- 反面样例：[../../assets/sample-skill/](../../assets/sample-skill/)
