<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo.jpg">
    <img src="assets/logo.jpg" alt="Chinese Parents Skill" width="180">
  </picture>
</p>

<h1 align="center">Chinese Parents Skill</h1>

<p align="center">
  <em>中国式家长模拟器 —— 你的妈是什么妈？</em>
</p>

<p align="center">
  <a href="https://github.com/weed33834/chinese-parents-skill/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/weed33834/chinese-parents-skill?style=flat-square&color=red" alt="License">
  </a>
  <a href="https://github.com/weed33834/chinese-parents-skill/releases">
    <img src="https://img.shields.io/github/v/release/weed33834/chinese-parents-skill?style=flat-square&color=orange" alt="Version">
  </a>
  <a href="https://github.com/weed33834/chinese-parents-skill/stargazers">
    <img src="https://img.shields.io/github/stars/weed33834/chinese-parents-skill?style=flat-square" alt="Stars">
  </a>
  <a href="https://github.com/weed33834/chinese-parents-skill/commits/main">
    <img src="https://img.shields.io/github/last-commit/weed33834/chinese-parents-skill?style=flat-square&color=blue" alt="Last Commit">
  </a>
  <a href="https://github.com/weed33834/chinese-parents-skill/issues">
    <img src="https://img.shields.io/github/issues/weed33834/chinese-parents-skill?style=flat-square&color=green" alt="Issues">
  </a>
  <a href="https://github.com/weed33834/chinese-parents-skill">
    <img src="https://img.shields.io/github/repo-size/weed33834/chinese-parents-skill?style=flat-square" alt="Repo Size">
  </a>
</p>

<p align="center">
  <a href="README.md">**中文**</a> · <a href="README.en.md">English</a> · <a href="README.ja.md">日本語</a> · <a href="README.ko.md">한국어</a>
</p>

<p align="center">
  <a href="#简介">简介</a> ·
  <a href="#三种模式">三种模式</a> ·
  <a href="#10-个维度拆穿中国式家长">10 维画像</a> ·
  <a href="#计算器">计算器</a> ·
  <a href="#18-个场景">场景</a> ·
  <a href="#想加料">想加料</a>
</p>

---

## 简介

你妈说过"你看看人家孩子"吗？

你妈会在你考了第三名之后先夸两句，再问"那第一名多少分"吗？

这个项目不做理论研究，只干三件事：

- **模拟** —— 告诉它你妈是什么样的人，它演给你看
- **诊断** —— 描述你妈的行为，它反推出一份可复算的维度画像
- **应对** —— 你有件事一直不敢开口，它陪你把这场对话先打一遍

中国式家长不是单一模式。同一个"考了第三名"，有的妈先骂再问，有的妈先夸再问，有的妈根本不问。10 个维度，每个 0-100 分，理论覆盖 **59049 种家长形态**。

**这个 skill 的定位只有一句话：还原一份能被你和别人复算的中国式家长画像。** 模拟、诊断、应对都是手段，画像是目的——它算出来的那个"妈"，要站得住（有公式）、对得上（同一个人两次结果一致）、错得起（缺数据就明说"算不出"，而不是编个圆）。v0.5 补的一座地基，正是为了这三点：多轮推演真正落地、假数字被堵死、文档里每个数字都有断言守着。

**v0.5 最大的变化**：v0.4 给了"计算器"但只算首轮快照，问"我顶回去了她怎么反应"它答不了；现在多轮推演状态机完整落地，五轮对话能逐值复现，并且缺失维度不再静默填 50（那是 v0.4 自己警告过的假数字陷阱），而是走 known/inferred/blind 三级置信度 + 污染追踪。

---

## 三种模式

### 1. 模拟

告诉它画像，它演。支持**多轮**——你可以顶回去，看她怎么升级。

```
你：我妈是那种管得严但心软的，我跟她说我要辞职去做自媒体

AI：【画像】控制 严格(72) · 温度 温暖(58) · 焦虑 焦虑(60) · 观念 传统(30)
    【状态】TEMP 24（绷着）· BOND 69 · 让步阈值 70

    "自媒体？那是什么工作，五险一金谁给你交？"
    ...
    ── TEMP 42 ↑18（施压）│ BOND 66 ↓3 │ 说服进度 12/70

你：这是我自己的事，你别管

AI：── TEMP 75 ↑33（情绪化）│ BOND 58 ↓8
    "你自己的事？你从小到大哪件事不是我操心的？行，你的事，你自己的事……"
```

那句"这是我自己的事"在雷区表里是 `+40`，对 `CTL≥75` 的家长还要额外 `+10`。**它是整个词表里性价比最低的一句——你占了理，但输了局。**

### 2. 诊断

描述行为，它反推画像。或者做 30 题快测。

```
  控制  █████████████████████░░░   88  控制
  温度  ██████░░░░░░░░░░░░░░░░░░   25  理性
  参与  █████████████████░░░░░░░   70  主动
  焦虑  ████████████████████░░░░   85  恐慌
  沟通  ████░░░░░░░░░░░░░░░░░░░░   18  命令
  观念  █████░░░░░░░░░░░░░░░░░░░   20  传统保守
  经济  ███████░░░░░░░░░░░░░░░░░   30  苛刻
  期望  ██████████████████████░░   92  极高
  社交  █████░░░░░░░░░░░░░░░░░░░   22  封闭
  独立  ████░░░░░░░░░░░░░░░░░░░░   15  包办

  ── 命中的耦合规则 ──
   ▸ 高压无温度：家变成管理机构，只有指令没有情感回路
   ▸ 焦虑淤积：焦虑无处释放，转成持续唠叨和迁怒
   ▸ 爱与成绩挂钩：考砸即失爱，冷处理是主要惩罚手段

  ── 参考类型相似度 ──
   虎妈虎爸  91%    主要差异 焦虑 85 vs 65、控制 88 vs 70
   强势家长 91%   主要差异 焦虑 85 vs 60、经济 30 vs 45

  ── 怎么读 ──
   起手就在施压区，这场对话没有暖场空间，开口即正题。
   让步阈值 87，一次对话里基本攒不出这么多说服力。
   正确目标不是说服，是不掉关系分地拖到下一次。
```

**这些数字不是编的。** v0.3 的报告也印百分比，但全文没有算法——同一个人问两次能得到两份报告。v0.4 给了公式，也给了计算器，你可以自己验。

### 3. 应对

这是 v0.4 新增的，也是大多数人真正需要的那个。

诊断能告诉你"你妈是虎妈"，但你真正想知道的是**那我该怎么开这个口**。

应对模式给的是：目标可行性分级（有些仗打不赢，它会直说）、三条路线（正面 / 迂回 / 既成事实）、12 个战术、三层深的反应树、以及谈崩了怎么收场。

> **T4 面子保全**
> 中国家庭里大量的施压不是家长自己要的，是亲戚问了她答不上来，压力顺着往下传。
> 你给她一句能在饭桌上说的台词，等于把压力源从她身上摘掉。
> 配套那句更狠：「真问急了你把电话给我，我来说。」
> 她要的不是你结婚，是不用在饭桌上难堪。

---

## 10 个维度，拆穿中国式家长

| 维度 | 管什么 | 0 端 → 100 端 |
|------|--------|--------------|
| 控制 `CTL` | 管得多宽 | 放任 · 适度 · 严格 · 控制 |
| 温度 `WRM` | 情感表达的浓度 | 冷漠 · 理性 · 温暖 · 溺爱 |
| 参与 `INV` | 投入了多少精力 | 缺席 · 被动 · 主动 · 过度介入 |
| 焦虑 `ANX` | 对未来有多焦虑 | 佛系 · 适度 · 焦虑 · 恐慌 |
| 沟通 `COM` | 信息流的方向 | 命令 · 说教 · 商量 · 倾听 |
| 观念 `VAL` | 开明还是保守 | 传统 · 混合 · 开明 |
| 经济 `FIN` | 给钱的方式 | 苛刻 · 适度 · 慷慨 |
| 期望 `EXP` | 期望多高 | 无要求 · 适度 · 极高 |
| 社交 `SOC` | 怎么管你交朋友 | 封闭 · 引导 · 开放 |
| 独立 `IND` | 培养还是包办 | 包办 · 引导 · 放手 |

**两个反直觉的地方**：

`温度` 不是"爱的多少"，是**情感表达的浓度**。0 端冷漠是爱不出口，100 端溺爱是爱到窒息，两头都有问题——它是唯一一个中间偏高才最优的维度。

`沟通` 不是"话多话少"，是**信息流方向**。`COM=88` 的家长可能一晚上只说三句话，但都是"然后呢""你怎么想"。别把话痨当成高分。

### 单看一个维度看不出来的东西

真正决定一个家长难不难搞的，往往是组合：

| 组合 | 是什么 |
|------|--------|
| `沟通高` + `控制高` | **假民主**。她会认真听你说完四十分钟，然后按原计划执行 |
| `参与低` + `沟通低` + `控制中` | **诈尸式**。平时消失，一出现就全面接管，没有铺垫 |
| `控制高` + `温度高` | **甜蜜的窒息**。不吵不骂，只叹气抹泪，你连吵架的入口都找不到 |
| `焦虑高` + `经济低` | 焦虑无处释放，全转成唠叨和迁怒 |
| `期望高` + `温度低` | 爱与成绩挂钩，考砸即失爱，冷处理是主要惩罚 |

**假民主是最难识别的一种**，因为过程完全符合"好好沟通"的所有标准，所以你连生气都找不到理由，只能怀疑自己。

判断标准只有一个：**听完之后，结论变了吗？**

---

## 计算器

### 画像

```bash
# 部分维度，其余按耦合规则推断
python3 scripts/profile.py --scores "CTL=88,ANX=85,EXP=92"

# 加载参考类型
python3 scripts/profile.py --type 虎妈虎爸

# 交互答 30 题
python3 scripts/profile.py --quiz

# 答案串可存档，下次直接复现
python3 scripts/profile.py --answers cdcbbdcddcaabbcbabcabdddaacbad

# 机器可读
python3 scripts/profile.py --scores "..." --json
```

纯标准库，零依赖，Python 3.8+。输出维度条形图、极端维度、耦合规则、相似度排名、六个动力学初始值和读法。

**缺失维度不靠猜：** 你只给 `CTL=90`，其余维度会按耦合规则推断（`inferred`，方向可信、数值别当真）或硬填 50（`blind`，结论作废）。硬填维度污染下游动力学量时，输出会标 `⚠` 并**抑制相似度与读法**；`blind` 维度 ≥4 个则直接"不报相似度"。宁可少说，不乱说。

**文档里的每一个数字都跟这个脚本复算一致**，包括 8 个参考类型 × 6 个动力学量那张表。不一致就是 bug，欢迎提 Issue。

### 多轮推演

```bash
# 看雷区/破冰表里所有可用招式
python3 scripts/profile.py --list-moves

# 用内置示例跑五轮（dynamics.md 7.2 算例）
python3 scripts/profile.py --simulate-demo

# 自己指定招式序列、关系账户初值与沟通渠道
python3 scripts/profile.py --type 虎妈虎爸 \
    --simulate T21 T9 T1 C2 C18 --bond 69 --channel wechat --who 我

# 也支持从部分维度起推
python3 scripts/profile.py --scores "CTL=72,WRM=48,INV=68,ANX=60,COM=32,VAL=30,FIN=58,EXP=68,SOC=38,IND=32" \
    --simulate T21 T9 T1 C2 C18
```

`--simulate` 把每一轮都打印成逐行对账：哪句话、加了/降了几度、BOND 怎么动、说服进度到哪；最后给出**判定**（真让步 / 假让步 / 不让步）和**"最贵的一句"**——那句让你占了理、却把关系分掉得最狠的话。非当面（电话/微信）升温打 8 折、微信再 8 折，但 BOND 伤害 ×1.2。

**这套推演不是演示**，是 `dynamics.md` 第四~七节的可执行规格：加成只取最高一条不叠加、单轮净升温封顶 +35、TEMP≥85 只有 `[高温]` 条目生效且 ×1.5、同条破冰第二次 ×0.5 第三次 ×0。`--simulate-demo` 的五轮结果与文档 7.2 逐值一致，改公式会被 `scripts/test_profile.py` 的 68 项断言当场拦下。

---

## 18 个场景

前 10 个是老的，后 8 个是 v0.4 新加的。完整矩阵见 [scenarios.md](references/scenarios.md)。

| | 场景 | 关键维度 |
|---|------|---------|
| A | 学业 / 工作表现 | 控制 · 焦虑 · 期望 |
| B | 人生选择（辞职创业 gap） | 观念 · 控制 · 焦虑 |
| C | 婚恋关系 | 观念 · 社交 · 控制 |
| D | 消费 / 经济 | 经济 · 控制 |
| E | 家庭相处 | 温度 · 参与 |
| F | 社交 / 交友 | 社交 · 控制 |
| G | 网络 / 电子产品 | 控制 · 焦虑 |
| H | 健康 / 生活习惯 | 温度 · 参与 |
| I | 外表 / 形象 | 观念 · 控制 |
| J | 教育择校 | 焦虑 · 经济 · 期望 |
| **K** | **亲戚聚会与横向比较** | 焦虑 · 社交 · 期望 |
| **L** | **催婚催生与彩礼** | 观念 · 焦虑 · 控制 |
| **M** | **买房与经济支援** | 经济 · 控制 · 独立 |
| **N** | **养老与赡养** | 温度 · 参与 · 经济 |
| **O** | **多子女与偏心** | 温度 · 经济 · 期望 |
| **P** | **情绪与心理健康** | 观念 · 温度 · 沟通 |
| **Q** | **隐私边界（翻手机）** | 控制 · 社交 |
| **R** | **非主流职业** | 观念 · 焦虑 · 期望 |

新场景里，**M（买房）** 争的从来不是钱，是"接受了这笔钱之后你还有多少话语权"；**O（偏心）** 里最重的从来不是少给的十万，是那句"别指望他了"。

---

## 目录结构

```
chinese-parents-skill/
├── SKILL.md                    # 主入口，模式路由与加载导航
├── references/
│   ├── dimensions.md           # 10 维数值内核（唯一事实来源）
│   ├── scenarios.md            # 18 场景 × 维度影响矩阵
│   ├── dynamics.md             # 情绪状态机、雷区/破冰词表、让步判定
│   ├── diagnosis.md            # 诊断流程、鉴别诊断、报告格式
│   ├── counterplay.md          # 应对模式：路线、12 战术、反应树
│   ├── family-system.md        # 多角色家庭系统、背景修正因子
│   ├── quotes.md               # 语录库、话术翻译表
│   ├── quirks.md               # 神人家长魔怔案例集：17 种奇葩思维模板 + 场景案例库 + 反逻辑模拟纪律
│   └── quiz.md                 # 30 题快测题库（脚本自动导出）
├── scripts/
│   └── profile.py              # 画像计算器，纯标准库
├── README.md · README.en.md · README.ja.md · README.ko.md · CHANGELOG.md
├── CONTRIBUTING.md · CODE_OF_CONDUCT.md · LICENSE
└── assets/ · .github/
```

SKILL.md 从 v0.3 的 627 行单文件拆成了主入口 + 按需加载。**不是为了好看，是因为 26KB 的单文件每次都要全量进上下文。**

---

## 边界

这个 skill 不做亲子关系咨询，不做家庭治疗，不替任何一方站队。它也不会：

- 模拟肢体暴力、虐待、限制人身自由
- 使用地域刻板印象，或做城乡、学历、职业的歧视性归因
- 给人贴"人格障碍""PUA"这类标签——它描述行为模式，不下临床判断
- 在模拟末尾硬加"其实父母都是爱你的"

**如果你的处境涉及人身安全、严重情感虐待、经济胁迫或自伤念头，请不要在这里找话术。** 那不是沟通技巧能解决的问题，去找现实中能帮到你的人。

---

## 想加料

你妈有一句这里没收录的独特语录？某个场景演得不像你妈？某个维度的分值区间不准？

别忍着。这项目靠大家共建，你妈的经验大概率别人妈也用得上。

- 发现问题 → [提 Issue](https://github.com/weed33834/chinese-parents-skill/issues/new?template=bug_report.md)
- 有想法 → [功能建议](https://github.com/weed33834/chinese-parents-skill/issues/new?template=feature_request.md)
- 有新场景 → [场景补充](https://github.com/weed33834/chinese-parents-skill/issues/new?template=scenario_suggestion.md)

贡献前看一眼 [CONTRIBUTING.md](CONTRIBUTING.md)。改了公式或维度向量的，记得跑一遍 `scripts/profile.py` 确认文档里的数字还对得上。

## 许可

[Apache-2.0](LICENSE) © 2026 badhope
