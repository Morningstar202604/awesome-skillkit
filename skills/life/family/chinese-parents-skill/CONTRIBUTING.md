# 贡献指南

这个项目靠的是大家各自妈的经验。

如果你妈有一种独特的语录，这个项目没收录；
如果你觉得某个场景模拟得不像你妈；
如果你发现某个维度的档位区间不准——

别忍着，提 Issue 或者直接改。

v0.4 之后这个仓库不再是一个 Markdown 文件了：文档里的数字和 `scripts/profile.py` 是绑死的，改一边不改另一边就是 bug。所以下面的规则比 v0.3 时代啰嗦，但每一条都是为了别让报告里出现算不出来的数。

---

## 怎么贡献

### 提 Issue

- **Bug 报告**：跑不起来、报错、模拟出来的家长不对劲、文档数字和脚本对不上
- **功能建议**：想加新维度、新场景、新战术、新模式
- **场景补充**：你妈有一种这个项目没覆盖的典型场景
- **维度优化**：你觉得某个维度的档位划分或耦合规则不合理

### 提 PR

1. Fork 本仓库
2. 建分支：`git checkout -b feat/your-feature`
3. 改完提交：`git commit -m "feat: 描述你的改动"`
4. 推上去：`git push origin feat/your-feature`
5. 提 Pull Request

### Commit 规范

用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

| 类型 | 什么时候用 |
|------|-----------|
| `feat:` | 加了新东西 |
| `fix:` | 修了 bug |
| `docs:` | 改文档 |
| `style:` | 格式调整 |
| `refactor:` | 重构 |

---

## 改哪个文件

SKILL.md 从 v0.3 的 627 行单文件拆成了主入口 + `references/` 下 8 个按需加载的文件 + 一个脚本。**动手之前先对一下这张表，别把内容写进错的文件。**

| 你想改的东西 | 动这个文件 |
|-------------|-----------|
| 模式路由、加载导航、输出格式骨架、生成纪律、全局边界 | `SKILL.md` |
| 维度定义、档位分值区间、8 个锚点向量、相似度算法、耦合规则 | `references/dimensions.md` + `scripts/profile.py` |
| 场景条目、某个场景下某个维度的行为影响 | `references/scenarios.md` |
| TEMP/BOND/YIELD 公式、K/D/COOL 系数、雷区表、破冰表、让步判定 | `references/dynamics.md` + `scripts/profile.py` |
| 诊断流程、追问顺序、鉴别诊断、报告格式 | `references/diagnosis.md` |
| 可行性分级、三条路线、12 个战术、反应树、失败兜底 | `references/counterplay.md` |
| 多角色家庭系统、联盟模型、背景修正因子 | `references/family-system.md` |
| 语录、话术翻译表 | `references/quotes.md` |
| 30 题快测题库 | `scripts/profile.py` 里的 `QUIZ` 常量（**不要直接改 quiz.md**，见下） |

**SKILL.md 是入口不是仓库。** 新增细节写进对应的 reference，SKILL.md 里最多加一行导航。往主入口里塞正文，等于把 v0.3 那个 26KB 全量入 context 的问题又搬回来。

---

## 硬性规则：`dimensions.md` 是唯一事实来源

所有档位、分值、百分比、相似度、动力学初值，全部以 `references/dimensions.md` 为准。其他文件和它冲突时，改其他文件。

**任何涉及维度分值、相似度算法、耦合规则的改动，必须同步改 `scripts/profile.py`，并且跑一遍验证。** 文档里的数字不是写上去的，是算出来的——你改了公式却没重算文档，报告就会重新变成 v0.3 那种"印着 85% 但没人知道怎么来的"。

### 改完必须跑的三件事

```bash
# 1. 8 个锚点还能不能正常算完
for t in 虎妈虎爸 鸡娃家长 直升机父母 佛系家长 开明家长 强势家长 诈尸式育儿 丧偶式育儿; do
  python3 scripts/profile.py --type "$t" >/dev/null || echo "FAIL $t"
done

# 2. 抽查一个部分维度的画像，看推断和耦合有没有炸
python3 scripts/profile.py --scores "CTL=88,ANX=85,EXP=92"

# 3. 重算 dynamics.md 的全锚点速查表（见下）
```

### 那张 48 个数字的表

`references/dynamics.md` 第二节末尾有一张**全锚点速查表**：8 个参考类型 × 6 个动力学量（`TEMP₀` / `K` / `D` / `COOL` / `BOND₀` / `YIELD`），一共 48 个数。

**只要你动了 TEMP₀、K、D、COOL、BOND₀、YIELD 里任何一个公式，或者动了任何一个锚点向量，这 48 个数就全都要重算。** 一个都不能漏——这张表是模型手算时唯一的对照基准，错一格就会连着错一整轮推演。

重算并逐格核对：

```bash
for t in 虎妈虎爸 鸡娃家长 直升机父母 佛系家长 开明家长 强势家长 诈尸式育儿 丧偶式育儿; do
  python3 scripts/profile.py --type "$t" --json | python3 -c "
import json,sys
d=json.load(sys.stdin)['dynamics']
print('$t', d['TEMP0'], d['K'], d['D'], d['COOL'], d['BOND0'], d['YIELD'])"
done
```

输出的每一行都要和 `dynamics.md` 表里那一行完全一致。不一致就改文档，不要改脚本去迁就文档。

顺带检查这几处也有硬编码的数字，改公式时容易漏：

- `dimensions.md` 第五节的相似度算例（150 → 85%、79 → 92%）
- `dynamics.md` 第二节的算例 A/B/C（逐步手算过程，不只是结果）
- `dynamics.md` 第七节那段完整多轮推演里的每一个状态条
- `README.md` 及 `README.en.md` / `README.ja.md` / `README.ko.md` 里的示例报告（四语文档要保持一致）

**取整约定按 `dynamics.md` 开头那条**：四舍五入，`.5` 一律进位；TEMP/BOND/YIELD 取整数，K/D 保留两位小数。手算对不上账，先检查是不是这里。

### 加新耦合规则的额外要求

`dimensions.md` 第七节每一条耦合规则都要写清楚**边界条件为什么是这个数**。典型例子是诈尸式那条挂的 `CTL≥25`：不加它，丧偶式（`CTL=12`）也会命中。这种"看起来多余的条件"必须留注释，否则下一个人会顺手删掉。

新规则同时要在 `scripts/profile.py` 里实现，并确认它不会和已有规则互相打架（同一份画像命中两条结论相反的规则，是最难查的一类 bug）。

---

## `references/quiz.md` 是自动导出的，别手改

题库的源头是 `scripts/profile.py` 里的 `QUIZ` 常量。`quiz.md` 只是它的一份 Markdown 快照。

改题、改选项、改选项对应的分值，都改脚本，然后重新导出：

```bash
python3 scripts/profile.py --dump-quiz > references/quiz.md
```

导出后确认答案串还能跑：

```bash
python3 scripts/profile.py --answers cdcbbdcddcaabbcbabcabdddaacbad
```

直接编辑 `quiz.md` 的后果是：文件看着改了，`--quiz` 交互和 `--answers` 复现用的还是老题，两边悄悄对不上。PR 里出现只改 `quiz.md` 不改 `profile.py` 的 diff，会被直接打回。

题目数量固定 30 题，选项固定 a/b/c/d 四个——答案串的长度和解析逻辑依赖这两条，要改先提 Issue。

---

## 贡献语录和场景的质量标准

这是这个项目唯一真正不可替代的东西。公式谁都能推，**"这就是我妈原话"的句子只有你有**。

**收**：

- 有具体名词。"你表哥去年考编上岸了"比"你看看人家"强，因为前者有年份、有身份、有结果
- 有那个多余的半句。真实的话总是拖一点尾巴——"行，你自己决定，反正到时候难受的也不是我"
- 有反常识的组合。夸完立刻问第一名多少分；骂了一晚上，第二天车票买好了
- 能反推出维度。一句好语录应该让人一看就知道它属于哪个维度的哪个档位

**不收**：

- 谁都能编的通用句。"你要好好努力""我这是为你好啊"——太泛，没有信息量
- 网络段子和影视台词。梗图里的家长不是家长，是梗
- 靠地域、口音、职业、学历取笑人的
- 把家长写成纯反派的。哪怕 `WRM 12` 的画像也要留一处关爱底色——不说话，但饭做了。没有底色的不是画像，是刻板印象

**提交格式**：语录写进 `references/quotes.md` 对应的维度/场景分区，并标注它对应的维度档位（比如 `EXP 67-100`）。新场景写进 `references/scenarios.md`，按现有条目的结构补齐维度影响矩阵——只写一句台词不写矩阵的场景，引擎用不了。

场景编号排到 R 了，新场景接着往下排，别插队改已有编号。编号在 `SKILL.md`、`scenarios.md`、两份 README 里都出现过。

---

## 开发流程

```
提 Issue 讨论 → 确认方案 → 实现 → 跑验证 → Review → Merge
```

重大改动（新增维度、改相似度算法、改动力学公式、改诊断逻辑）先提 Issue 讨论，不要直接提 PR。这类改动的影响面是全仓库的，方案没定就动手，返工的是你。

PR 描述里请说明：改了哪些文件、有没有动数值、跑过哪些验证。动了公式的 PR 请把重算后的对照输出贴进来。

改了行为规则或新增内容，记得同步更新四语文档（`README.md` / `README.en.md` / `README.ja.md` / `README.ko.md`），都要保持一致。

---

## 行为准则

看 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)。简单说就是：尊重所有人，不要搞歧视和人身攻击。

再加一条这个项目特有的：**这里聊的是别人的家人。** 可以吐槽，可以刻薄，可以不原谅，但不要在 Issue 里评判别人的父母该不该被原谅——每个人和家里的账，只有他自己算得清。
