#!/usr/bin/env python3
"""
chinese-parents-skill 画像计算器

把 references/dimensions.md 和 references/dynamics.md 里的公式变成可执行的东西。
存在的理由很简单：v0.3 的诊断报告写着"相似度 85%"，但全文没有算法，那个数字是编的。

纯标准库，无依赖。Python 3.8+。

用法:
    python3 profile.py --quiz                       交互答 30 题
    python3 profile.py --answers abcdabcd...        直接给 30 个字母
    python3 profile.py --scores CTL=75,ANX=80       给部分或全部维度分
    python3 profile.py --type 虎妈虎爸               加载锚点画像
    python3 profile.py --scores ... --json          机器可读输出
    python3 profile.py --dump-quiz                  导出 Markdown 题库

    python3 profile.py --type 强势家长 --simulate T9,T1,C18
                                                    多轮推演，逗号分隔词条
    python3 profile.py --simulate-demo              复现 dynamics.md 7.2 算例
    python3 profile.py --list-moves                 列出全部雷区/破冰词条
"""

import argparse
import json
import sys
from decimal import Decimal, ROUND_HALF_UP

VERSION = "0.5"

# ---------------------------------------------------------------- 内核常量
# 与 references/dimensions.md 第一、二节严格一致，改动必须同步改文档

DIMS = ["CTL", "WRM", "INV", "ANX", "COM", "VAL", "FIN", "EXP", "SOC", "IND"]

DIM_CN = {
    "CTL": "控制", "WRM": "温度", "INV": "参与", "ANX": "焦虑", "COM": "沟通",
    "VAL": "观念", "FIN": "经济", "EXP": "期望", "SOC": "社交", "IND": "独立",
}

# 4 档维度的档位标签，按 0-24 / 25-49 / 50-74 / 75-100
BANDS_4 = {
    "CTL": ["放任", "适度", "严格", "控制"],
    "WRM": ["冷漠", "理性", "温暖", "溺爱"],
    "INV": ["缺席", "被动", "主动", "过度介入"],
    "ANX": ["佛系", "适度", "焦虑", "恐慌"],
    "COM": ["命令", "说教", "商量", "倾听"],
}

# 3 档维度的档位标签，按 0-33 / 34-66 / 67-100
BANDS_3 = {
    "VAL": ["传统保守", "混合", "开明现代"],
    "FIN": ["苛刻", "适度", "慷慨"],
    "EXP": ["无要求", "适度", "极高"],
    "SOC": ["封闭", "引导", "开放"],
    "IND": ["包办", "引导", "放手"],
}

ANCHORS = {
    "虎妈虎爸":   dict(CTL=70, WRM=40, INV=65, ANX=65, COM=15, VAL=20, FIN=45, EXP=90, SOC=25, IND=20),
    "鸡娃家长":   dict(CTL=68, WRM=60, INV=72, ANX=85, COM=35, VAL=45, FIN=78, EXP=92, SOC=50, IND=45),
    "直升机父母": dict(CTL=72, WRM=65, INV=92, ANX=82, COM=20, VAL=45, FIN=80, EXP=55, SOC=25, IND=15),
    "佛系家长":   dict(CTL=35, WRM=62, INV=55, ANX=15, COM=62, VAL=75, FIN=50, EXP=20, SOC=75, IND=78),
    "开明家长": dict(CTL=38, WRM=65, INV=60, ANX=38, COM=85, VAL=80, FIN=55, EXP=50, SOC=78, IND=75),
    "强势家长": dict(CTL=92, WRM=18, INV=60, ANX=60, COM=10, VAL=15, FIN=45, EXP=88, SOC=15, IND=12),
    "诈尸式育儿": dict(CTL=30, WRM=20, INV=15, ANX=40, COM=12, VAL=22, FIN=70, EXP=50, SOC=20, IND=55),
    "丧偶式育儿": dict(CTL=12, WRM=15, INV=8,  ANX=12, COM=15, VAL=25, FIN=72, EXP=15, SOC=30, IND=80),
}

# dimensions.md 第七节：维度耦合规则
COUPLINGS = [
    (lambda p: p["CTL"] >= 70 and p["WRM"] <= 30, "高压无温度", "家变成管理机构，只有指令没有情感回路"),
    (lambda p: p["CTL"] >= 70 and p["WRM"] >= 70, "甜蜜的窒息", "用愧疚感控制，反抗成本比硬控制更高"),
    (lambda p: p["ANX"] >= 75 and p["FIN"] >= 70, "焦虑变现", "焦虑靠砸钱释放，你会被资源绑架"),
    (lambda p: p["ANX"] >= 75 and p["FIN"] <= 33, "焦虑淤积", "焦虑无处释放，转成持续唠叨和迁怒"),
    (lambda p: p["EXP"] >= 80 and p["WRM"] <= 40, "爱与成绩挂钩", "考砸即失爱，冷处理是主要惩罚手段"),
    (lambda p: p["INV"] <= 20 and p["COM"] <= 24 and p["CTL"] >= 25, "诈尸式", "平时消失，一出现就全面接管，没有铺垫"),
    (lambda p: p["COM"] >= 75 and p["CTL"] >= 75, "假民主", "认真听完，然后按原计划执行"),
    (lambda p: p["IND"] <= 25 and p["EXP"] >= 80, "高分低能培养", "只要成绩不要生活能力"),
    (lambda p: p["VAL"] <= 30 and p["SOC"] <= 30, "门第审查", "婚恋场景杀伤力最大"),
    (lambda p: p["WRM"] >= 85 and p["IND"] <= 20, "溺爱包办", "成年后仍无法独立决策"),
]

WRM_BUFFER = [0, 5, 15, 8]  # 按 WRM 的 4 个档位查表，dynamics.md 1.1


# ---------------------------------------------------------------- 题库
# 每题: (维度, 题干, [4 个选项文本])
# 选项分值: 4 档维度 [10,37,62,88]，3 档维度 [8,35,65,92]

SCORES_4 = [10, 37, 62, 88]
SCORES_3 = [8, 35, 65, 92]

QUIZ = [
    ("CTL", "你晚上要出门，父母的标准反应是", [
        "基本不问，你走你的",
        "问一句去哪儿",
        "去哪、跟谁、几点回来，一样都不能少",
        "先说不许去，或者规定死几点必须到家"]),
    ("CTL", "你决定换工作或换专业，父母的介入程度", [
        "他们事后才知道，也没什么反应",
        "会问问怎么回事",
        "要求你把方案讲清楚，由他们评估",
        "不用你决定，他们已经安排好了"]),
    ("CTL", "你的房间和你的东西", [
        "他们从来不进",
        "会敲门，进去也不动你东西",
        "直接进，顺手帮你整理",
        "会翻看，会丢掉他们认为没用的"]),

    ("WRM", "你考砸了或者工作出了问题，他们的第一反应", [
        "不接话，或者当没听见",
        "先来一句我早就说过",
        "先安慰你，再一起看问题出在哪",
        "立刻心疼，说不干了不干了，妈养你"]),
    ("WRM", "家里说过我爱你，或者拥抱过吗", [
        "从来没有，想都不敢想",
        "没说过，但会多做一个菜、多塞点钱",
        "说得出口，也抱得起来",
        "天天说，伴随大量的照顾和身体接触"]),
    ("WRM", "你生病的时候", [
        "让你自己去医院",
        "一边唠叨你不注意身体一边给你煮点东西",
        "关心你，帮你安排",
        "立刻请假全程陪护，什么都不让你动手"]),

    ("INV", "父母清楚你现在具体在做什么吗", [
        "说不清楚，问起来只能说个大概行业",
        "知道公司名或者专业名，别的不了解",
        "清楚，还知道你最近在忙哪个项目",
        "清楚到会主动联系你的同事或者老师"]),
    ("INV", "家长会、学校活动、你人生的重要场合", [
        "基本不出现",
        "被叫了才来",
        "每次都来",
        "来了还要跟老师深聊，加上微信长期跟进"]),
    ("INV", "父母主动联系你的频率", [
        "几乎不主动，都是你打过去",
        "有事才找你",
        "定期问你近况",
        "一天好几次，没回就开始着急"]),

    ("ANX", "听说别人家孩子涨薪了、买房了、结婚了", [
        "没什么反应",
        "顺口提一句",
        "反复念叨，开始担心你",
        "当天就要你拿出个计划来"]),
    ("ANX", "你说最近有点累，想休息一阵", [
        "行，歇着吧",
        "别太累，注意身体",
        "休息可以，但别耽误太久",
        "休息？现在这个环境你敢休息？"]),
    ("ANX", "一件小事，比如你一次没接电话", [
        "没在意",
        "事后问一句怎么了",
        "会念叨你一顿",
        "连打十几个，甚至联系你朋友找人"]),

    ("COM", "意见不一致的时候", [
        "直接下结论，不解释理由",
        "长篇大论讲道理，你插不上话",
        "会讨论，能谈条件",
        "先问你怎么想，听完再说他的"]),
    ("COM", "你话说到一半", [
        "被打断，行了我知道了",
        "被打断，你听我说完",
        "让你说完，然后回应",
        "让你说完，还会追问一句然后呢"]),
    ("COM", "父母承认过自己错了吗", [
        "从来没有",
        "不明说，但会用行动补偿",
        "会承认，但很勉强",
        "会直接道歉"]),

    ("VAL", "他们对稳定工作的态度", [
        "只有体制内和国企才算正经工作",
        "还是稳定点好，但不强求",
        "稳定和喜欢都重要，看情况",
        "你喜欢就行，稳定不是唯一标准"]),
    ("VAL", "他们对不结婚或者不生孩子的态度", [
        "完全不能接受，这是原则问题",
        "嘴上说随你，实际一直劝",
        "能理解，但真心替你担心",
        "真的接受，不再提"]),
    ("VAL", "他们对没见过的新职业、新生活方式", [
        "一律排斥，不听解释",
        "不懂，所以先否定",
        "会问问那到底是干什么的",
        "会自己去搜、去了解"]),

    ("FIN", "你买了件比较贵的东西", [
        "盘问价格，说你败家",
        "问多少钱，提醒你省着点",
        "该花就花，没多问",
        "不问价，反过来问你钱还够不够"]),
    ("FIN", "你手头紧的时候", [
        "让你自己想办法",
        "借给你，但说清楚要还",
        "给你，顺便提醒你做点规划",
        "主动转钱过来，还不让你还"]),
    ("FIN", "家里在你身上花钱的方式", [
        "能省则省，每一笔都要过问",
        "必要的才花",
        "该花的都花",
        "自己舍不得吃穿，给你花从不犹豫"]),

    ("EXP", "你考了第二名，或者拿到了不错但不是最好的结果", [
        "挺好的呀",
        "不错，辛苦了",
        "还行，下次争取更好",
        "第一名是谁？差多少分？"]),
    ("EXP", "你说我就想当个普通人", [
        "普通挺好的",
        "健康就行，别的不重要",
        "话不能这么说，人还是要有追求",
        "你怎么这么没出息"]),
    ("EXP", "他们对你的最低预期", [
        "健康快乐就够了",
        "能养活自己就行",
        "至少要比同龄人好一点",
        "必须出人头地，不然对不起这些年"]),

    ("SOC", "你的朋友", [
        "要经过审查，不合适的不许来往",
        "会打听是什么人、家里干什么的",
        "让你带回来看看就行",
        "完全不过问"]),
    ("SOC", "你出去玩到很晚", [
        "不许，到点必须回",
        "可以，但必须报备到几点、跟谁",
        "提醒你注意安全",
        "完全不管，第二天也不问"]),
    ("SOC", "他们对你恋爱对象的态度", [
        "必须符合他们开的条件",
        "会仔细打听家庭情况",
        "关心，但最终尊重你",
        "你喜欢就好"]),

    ("IND", "报名、买票、办手续这类事", [
        "父母全包，你不用管",
        "父母帮你办了",
        "父母教你怎么办，你自己去",
        "你自己搞定，他们也不问"]),
    ("IND", "你遇到困难的时候", [
        "父母直接出面替你解决",
        "父母给你一套现成方案",
        "父母给建议，你自己决定",
        "让你自己扛，扛不住是你的事"]),
    ("IND", "你成年后的重大决定，比如工作、买房、结婚", [
        "父母定，你执行",
        "父母主导，你有发言权",
        "你定，父母提参考意见",
        "你定，通知他们一声"]),
]


# ---------------------------------------------------------------- 计算

def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def _half_up(v, places=0):
    """
    .5 一律进位，与 dynamics.md 的手算约定对齐。

    两个坑叠在一起：Python 的 round() 是银行家舍入（round(0.5)==0），
    而二进制浮点会把 1.425 存成 1.4249999...，直接 quantize 会得到 1.42。
    先截到 10 位小数消掉表示误差，再走 Decimal 的 ROUND_HALF_UP。
    """
    q = Decimal(1).scaleb(-places)
    return Decimal(repr(round(v, 10))).quantize(q, rounding=ROUND_HALF_UP)


def _round(v):
    return int(_half_up(v, 0))


def _round2(v):
    return float(_half_up(v, 2))


def band_index(dim, score):
    """返回档位序号（0 起）"""
    if dim in BANDS_4:
        return min(3, max(0, int(score) // 25))
    for i, edge in enumerate((33, 66)):
        if score <= edge:
            return i
    return 2


def band_label(dim, score):
    table = BANDS_4.get(dim) or BANDS_3[dim]
    return table[band_index(dim, score)]


def similarity(profile, anchor):
    """
    dimensions.md 第五节：归一化曼哈顿距离。

    这里必须用 _half_up 而不是内置 round()。总差 350 时得 65.0，
    银行家舍入在 .5 边界会往偶数偏，跟文档里的手算算例对不上账——
    v0.4 就在这儿留了个会漂移的口子。
    """
    total = sum(abs(profile[d] - anchor[d]) for d in DIMS)
    return _round((1 - total / 1000) * 100)


def rank_anchors(profile, floor=55):
    out = []
    for name, vec in ANCHORS.items():
        s = similarity(profile, vec)
        if s < floor:
            continue
        gaps = sorted(((abs(profile[d] - vec[d]), d) for d in DIMS), reverse=True)
        out.append({
            "type": name,
            "similarity": s,
            "top_gaps": [{"dim": d, "gap": g, "yours": profile[d], "anchor": vec[d]}
                         for g, d in gaps[:2] if g >= 15],
        })
    return sorted(out, key=lambda x: -x["similarity"])


def dynamics(p):
    """dynamics.md 第一节的六个量"""
    wrm_eff = 100 - abs(p["WRM"] - 62)
    inv_eff = 100 - abs(p["INV"] - 62)
    buf = WRM_BUFFER[band_index("WRM", p["WRM"])]

    temp0 = _clamp(0.25 * p["ANX"] + 0.15 * p["CTL"] + 0.10 * p["EXP"] - buf - 0.10 * p["COM"], 5, 60)
    k = 1 + (p["ANX"] - 50) / 100 + (p["CTL"] - p["COM"]) / 200
    d = 1 + (p["COM"] - 50) / 200 + (wrm_eff - 80) / 200
    cool = _clamp(_round(5 + p["COM"] / 20 - p["ANX"] / 20), 1, 10)
    bond0 = 0.40 * wrm_eff + 0.25 * p["COM"] + 0.25 * inv_eff + 0.10 * (100 - p["CTL"])
    yld = (0.35 * p["CTL"] + 0.25 * p["EXP"] + 0.15 * (100 - p["COM"])
           + 0.15 * (100 - p["VAL"]) + 0.10 * (100 - p["IND"]))

    notes = []
    if p["INV"] <= 20 and p["COM"] <= 24 and p["CTL"] >= 25:
        k += 0.25
        notes.append("诈尸式修正 K +0.25")
    if p["ANX"] >= 75 and p["FIN"] <= 33:
        k += 0.10
        notes.append("焦虑淤积修正 K +0.10")
    if p["CTL"] >= 70 and p["WRM"] >= 70:
        k -= 0.15
        notes.append("甜蜜的窒息 K −0.15，但 BOND 伤害 ×1.5")
    if p["COM"] >= 75 and p["CTL"] >= 75:
        k -= 0.30
        notes.append("假民主 K −0.30，让步判定强制走假让步")
    temp_cap = 100
    if p["WRM"] <= 20 and p["INV"] <= 20:
        temp_cap = 35
        notes.append("冷漠型 TEMP 上限锁 35，这种画像不会吵，只会更冷")

    return {
        "TEMP0": _round(temp0),
        "K": _round2(_clamp(k, 0.6, 1.8)),
        "D": _round2(_clamp(d, 0.6, 1.4)),
        "COOL": cool,
        "BOND0": _round(bond0),
        "YIELD": _round(yld),
        "TEMP_CAP": temp_cap,
        "notes": notes,
    }


def hit_couplings(p):
    return [{"name": n, "effect": e} for cond, n, e in COUPLINGS if cond(p)]


def extremes(p):
    out = []
    for dim in DIMS:
        v = p[dim]
        if v >= 85 or v <= 15:
            out.append({"dim": dim, "score": v, "label": band_label(dim, v)})
    return out


# ---------------------------------------------------------------- 词条表
# dynamics.md 第四节。加成"只取最高的一条，不叠加"——所以存成列表后取 max，
# 不要 sum。这条规矩在 v0.4 只写在文档里，没人执行，因为根本没有执行者。

def _b(cond, val):
    return (cond, val)


# id: (名称, 台词, 基础Δ, [(条件, 加成), ...])
TRIGGERS = {
    "T1":  ("划界宣言", "这是我自己的事，我自己负责。", 20, [
        _b(lambda p: p["CTL"] >= 75, 20),
        _b(lambda p: 50 <= p["CTL"] <= 74, 8),
        _b(lambda p: p["IND"] <= 33, 10)]),
    "T2":  ("否定其付出", "又没人求你为我做这些。", 30, [
        _b(lambda p: p["INV"] >= 75, 10),
        _b(lambda p: p["FIN"] >= 67, 8),
        _b(lambda p: p["WRM"] <= 40, 8)]),
    "T3":  ("拒绝竞争", "我不想卷了，我就想过点普通日子。", 18, [
        _b(lambda p: p["EXP"] >= 80, 17),
        _b(lambda p: 67 <= p["EXP"] <= 79, 10),
        _b(lambda p: p["ANX"] >= 75, 10)]),
    "T4":  ("反向翻旧账", "你当年不也没做到，凭什么要求我。", 25, [
        _b(lambda p: p["CTL"] >= 70, 10),
        _b(lambda p: p["WRM"] <= 40, 8)]),
    "T5":  ("谈钱切割", "你的钱我一分不要，你也别管我。", 20, [
        _b(lambda p: p["FIN"] >= 67, 15),
        _b(lambda p: p["FIN"] <= 33, 6)]),
    "T6":  ("中途离场", "（不接话，起身进屋／把电话挂了）", 22, [
        _b(lambda p: p["INV"] >= 75, 13),
        _b(lambda p: p["ANX"] >= 75, 10)]),
    "T7":  ("拿别人父母比", "人家爸妈都不像你这样。", 25, [
        _b(lambda p: p["WRM"] <= 40, 10),
        _b(lambda p: p["EXP"] >= 80, 8),
        _b(lambda p: p["SOC"] <= 33, 8)]),
    "T8":  ("质疑其见识", "你不懂，你那套早过时了。", 22, [
        _b(lambda p: p["VAL"] <= 33, 13),
        _b(lambda p: p["COM"] <= 24, 10)]),
    "T9":  ("宣布非常规路径", "我想辞了做自媒体。", 25, [
        _b(lambda p: p["VAL"] <= 33, 12),
        _b(lambda p: p["ANX"] >= 75, 10),
        _b(lambda p: p["EXP"] >= 67, 5)]),
    "T10": ("硬性拒绝", "我不去。（不给理由）", 20, [
        _b(lambda p: p["CTL"] >= 75, 15),
        _b(lambda p: p["COM"] <= 24, 10)]),
    "T11": ("沉默不答", "（同一个问题问了三遍，一声不吭）", 15, [
        _b(lambda p: p["ANX"] >= 75, 12),
        _b(lambda p: p["INV"] >= 75, 10),
        _b(lambda p: p["COM"] <= 24, 8)]),
    "T12": ("既成事实", "我已经辞了。／合同签完了。", 35, [
        _b(lambda p: p["CTL"] >= 75, 5)]),
    "T13": ("打断", "你先听我说完行吗。", 18, [
        _b(lambda p: p["COM"] <= 24, 12),
        _b(lambda p: p["CTL"] >= 70, 8)]),
    "T14": ("扯上夫妻关系", "你跟我爸不也是这么过来的。", 28, [
        _b(lambda p: p["WRM"] <= 40, 8)]),
    "T15": ("戳面子", "你就是怕别人问起来不好答。", 25, [
        _b(lambda p: p["SOC"] <= 33, 15),
        _b(lambda p: p["EXP"] >= 80, 8)]),
    "T16": ("术语反击", "你这是控制欲。／这叫原生家庭创伤。", 25, [
        _b(lambda p: p["COM"] <= 24, 13),
        _b(lambda p: p["VAL"] <= 33, 10)]),
    "T17": ("回吼", "够了！（提高音量）", 25, [
        _b(lambda p: p["WRM"] <= 24, 10),
        _b(lambda p: p["CTL"] >= 75, 10)]),
    "T18": ("否定既往安排", "早知道当初就不该听你的。", 25, [
        _b(lambda p: p["CTL"] >= 75, 12),
        _b(lambda p: p["EXP"] >= 80, 8)]),
    "T19": ("婚育宣言", "我不打算结婚。／我不生。", 20, [
        _b(lambda p: p["VAL"] <= 33, 18),
        _b(lambda p: p["SOC"] <= 33, 10),
        _b(lambda p: p["ANX"] >= 75, 8)]),
    "T20": ("宣布搬出去", "我打算搬出去自己住。", 18, [
        _b(lambda p: p["IND"] <= 33, 17),
        _b(lambda p: p["INV"] >= 75, 12),
        _b(lambda p: p["WRM"] >= 75, 12)]),
    "T21": ("流露去意", "这班我真上不下去了。", 15, [
        _b(lambda p: p["ANX"] >= 67, 10),
        _b(lambda p: p["EXP"] >= 75, 8)]),
}

# id: (名称, 台词, 基础Δ, [(条件, 加成), ...], 是否 [高温] 条目)
COOLERS = {
    "C1":  ("承接情绪", "我知道你是怕我以后没着落。", 12, [
        _b(lambda p: p["ANX"] >= 75, 8),
        _b(lambda p: 50 <= p["WRM"] <= 74, 5)], False),
    "C2":  ("给硬数字", "我卡里还有十四个月的房租和生活费，我算过账。", 15, [
        _b(lambda p: p["ANX"] >= 75, 10),
        _b(lambda p: p["FIN"] <= 33, 8)], False),
    "C3":  ("给期限和退路", "给我一年。到明年这时候没起色，我回去投简历。", 20, [
        _b(lambda p: p["CTL"] >= 70, 6),
        _b(lambda p: p["ANX"] >= 75, 6)], False),
    "C4":  ("承诺可核查", "我每周日晚上给你打电话，走到哪一步都跟你说。", 15, [
        _b(lambda p: p["INV"] >= 75, 10),
        _b(lambda p: p["CTL"] >= 70, 8)], False),
    "C5":  ("认小错保大方向", "这事我该早点跟你商量，是我不对。", 18, [
        _b(lambda p: 25 <= p["COM"] <= 49, 7),
        _b(lambda p: p["CTL"] >= 70, 6)], False),
    "C6":  ("抬对方", "这块我想听听你的意见，你见的比我多。", 15, [
        _b(lambda p: p["CTL"] >= 70, 10),
        _b(lambda p: 25 <= p["COM"] <= 49, 8)], False),
    "C7":  ("第三方背书", "我问过我舅了，他说这行现在都是正规公司。", 18, [
        _b(lambda p: p["VAL"] <= 33, 10),
        _b(lambda p: p["SOC"] <= 33, 8)], False),
    "C8":  ("谈她的身体", "妈你先坐下，你血压又该上来了。", 10, [
        _b(lambda p: p["WRM"] >= 50, 8),
        _b(lambda p: p["ANX"] >= 75, 5)], True),
    "C9":  ("给面子话术", "以后有人问，你就说我做新媒体，正经注册的公司。", 20, [
        _b(lambda p: p["SOC"] <= 33, 10),
        _b(lambda p: p["EXP"] >= 67, 8)], False),
    "C10": ("承认依赖", "以后好多事还得靠你们，我一个人真弄不明白。", 15, [
        _b(lambda p: p["IND"] <= 33, 10),
        _b(lambda p: p["WRM"] >= 75, 10)], False),
    "C11": ("调共同记忆", "跟我小时候你带我去报那个班一样，你当时也说先试试。", 12, [
        _b(lambda p: p["WRM"] >= 50, 6),
        _b(lambda p: p["INV"] >= 50, 5)], False),
    "C12": ("送台阶", "你说得对，这些我确实没想那么细。", 15, [
        _b(lambda p: p["CTL"] >= 75, 8),
        _b(lambda p: p["COM"] <= 24, 10)], False),
    "C13": ("转具体事务", "锅上水开了吧。／你那个药今天吃了没。", 8, [], True),
    "C14": ("让渡一个决定", "社保公积金怎么接你帮我看看，这个我听你的。", 18, [
        _b(lambda p: p["CTL"] >= 70, 10),
        _b(lambda p: p["INV"] >= 75, 8)], False),
    "C15": ("澄清不是针对她", "我不是嫌你烦。我是自己也慌。", 14, [
        _b(lambda p: p["WRM"] <= 40, 6),
        _b(lambda p: p["COM"] <= 24, 6)], False),
    "C16": ("钱的兜底承诺", "钱我不问你要。但真到揭不开锅那天，我一定张嘴。", 16, [
        _b(lambda p: p["FIN"] >= 67, 10),
        _b(lambda p: p["ANX"] >= 75, 6)], False),
    "C17": ("沉默陪着", "（倒杯水放她面前，坐下，不辩解）", 10, [
        _b(lambda p: p["WRM"] >= 50, 8)], True),
    "C18": ("示弱求助", "妈，我不是要跟你吵。我是真的有点撑不住了。", 25, [
        _b(lambda p: p["WRM"] >= 40, 8),
        _b(lambda p: p["INV"] >= 50, 6)], True),
    "C19": ("交出决定权", "那你说，我到底该怎么办。", 15, [
        _b(lambda p: p["CTL"] >= 70, 10),
        _b(lambda p: p["COM"] <= 24, 8)], True),
}

TEMP_ZONES = [(20, "常温"), (40, "绷着"), (60, "施压"), (84, "情绪化"), (100, "爆发")]

# 甜蜜的窒息下效果翻倍的三条（dynamics.md 第八节）
GUILT_DOUBLED = {"C5", "C6", "C10"}

# dynamics.md 6.1 的首次奖励，同一次对话内每项只计一次
FIRST_BONUS_CN = {
    "C3": "给出明确期限",
    "money": "给出可核查的钱的方案",
    "C7": "引入她信任的第三方",
    "C9": "解决面子问题",
}


def temp_zone(t):
    for edge, name in TEMP_ZONES:
        if t <= edge:
            return name
    return "爆发"


def bond_coef(bond):
    """dynamics.md 4.1 的 BOND 系数表 → (升温系数, 破冰系数)"""
    if bond >= 75:
        return 0.8, 1.2
    if bond >= 41:
        return 1.0, 1.0
    if bond >= 21:
        return 1.15, 0.8
    return 0.0, 0.5


def _best_bonus(p, bonuses):
    """加成只取最高一条，不叠加"""
    hit = [v for cond, v in bonuses if cond(p)]
    return max(hit) if hit else 0


CHANNELS = {"face": 1.0, "phone": 0.8, "wechat": 0.64}


# ---------------------------------------------------------------- 多轮状态机

def simulate(p, moves, bond=None, channel="face", dyn=None):
    """
    dynamics.md 第四~六节的完整状态机。

    v0.4 的最大窟窿：文档把雷区表、破冰表、冷却、BOND 溢出、让步判定
    全写成了可执行规格，脚本却只算首轮快照。用户问"我顶回去了，然后呢"，
    照样答不上来——跟 v0.3 一个毛病，只是把无解藏进了更漂亮的公式里。

    moves: ["T9", "C18", ...]，大小写不敏感。
    返回逐轮明细 + 结算，7.2 算例可原样复现。
    """
    dyn = dyn or dynamics(p)
    temp = dyn["TEMP0"]
    bond_v = dyn["BOND0"] if bond is None else _clamp(int(bond), 0, 100)
    bond_start, temp_start = bond_v, temp
    persuade = 0

    guilt = p["CTL"] >= 70 and p["WRM"] >= 70          # 甜蜜的窒息：BOND 扣减 ×1.5
    self_heat = p["ANX"] >= 85                          # 每轮末反而 +5
    ch = CHANNELS.get(channel, 1.0)
    bond_dmg_mul = 1.0 if channel == "face" else 1.2

    used = {}
    first_bonus_used = set()
    c14_count = 0
    hot_rounds = 0
    rounds = []

    for i, raw_id in enumerate(moves, 1):
        mid = raw_id.strip().upper()
        if mid not in TRIGGERS and mid not in COOLERS:
            raise ValueError(f"未知词条 {raw_id!r}，用 --list-moves 看全部")

        before = temp
        cap = min(dyn["TEMP_CAP"], 40 if bond_v <= 20 else 100)
        up_c, cool_c = bond_coef(bond_v)
        log = []
        bond_delta = 0

        if mid in TRIGGERS:
            name, line, base, bonuses = TRIGGERS[mid]
            bonus = _best_bonus(p, bonuses)
            if up_c == 0:
                delta = 0
                log.append(f"BOND≤20 冷处理，升温系数 ×0：{mid} {name} 不起波澜")
            else:
                delta = _round((base + bonus) * dyn["K"] * up_c * ch)
                delta = min(delta, 35)
                log.append(f"{mid} {name} ({base}{'+' + str(bonus) if bonus else ''})"
                           f"×{dyn['K']:.2f}{'' if up_c == 1.0 else f'×{up_c}'}"
                           f"{'' if ch == 1.0 else f'×{ch}'} = +{delta}")
            if mid == "T12":
                persuade += 15
                bond_delta -= 3
                log.append("既成事实：说服 +15，但 BOND −3")
            if mid in ("T2", "T14", "T18"):
                bond_delta -= 3
                log.append(f"{mid} 直伤关系：BOND 额外 −3")
        else:
            name, line, base, bonuses, hot = COOLERS[mid]
            n = used.get(mid, 0)
            repeat_mul = (1.0, 0.5, 0.0)[min(n, 2)]
            if before >= 85 and not hot:
                delta = 10
                log.append(f"爆发区非[高温]条目：{mid} {name} 失效，说理反噬 +10")
            elif mid == "C18" and p["WRM"] <= 24:
                delta = 0
                log.append("WRM≤24，C18 示弱本条失效——她不接这个，甚至读成软弱")
            elif repeat_mul == 0:
                delta = 0
                log.append(f"{mid} 第 {n + 1} 次用，效果归零。她听出来这是话术了")
            else:
                bonus = _best_bonus(p, bonuses)
                mul = dyn["D"] * cool_c * repeat_mul
                if before >= 85 and hot:
                    mul *= 1.5
                if guilt and mid in GUILT_DOUBLED:
                    mul *= 2
                    bond_delta -= 2
                    log.append(f"甜蜜的窒息：{mid} 效果翻倍，但借的是愧疚，BOND −2")
                cut = min(_round((base + bonus) * mul), 30)
                delta = -cut
                persuade += cut
                bits = f"({base}{'+' + str(bonus) if bonus else ''})×D{dyn['D']:.2f}"
                if cool_c != 1.0:
                    bits += f"×{cool_c}"
                if repeat_mul != 1.0:
                    bits += f"×{repeat_mul}(重复)"
                if before >= 85 and hot:
                    bits += "×1.5(高温)"
                log.append(f"{mid} {name} {bits} = −{cut}，说服 +{cut}")
                used[mid] = n + 1

                for key, cond, pts in (
                        ("C3", mid == "C3", 10),
                        ("money", mid in ("C2", "C16"), 12),
                        ("C7", mid == "C7", 10),
                        ("C9", mid == "C9", 15 if p["SOC"] <= 33 else 10)):
                    if cond and key not in first_bonus_used:
                        first_bonus_used.add(key)
                        persuade += pts
                        log.append(f"首次{FIRST_BONUS_CN[key]} 说服 +{pts}")
                if mid == "C14" and c14_count < 2:
                    c14_count += 1
                    persuade += 8
                    log.append("首次让渡决定权 说服 +8")

        after_hit = _clamp(before + delta, 0, cap)

        # 自然冷却（5.1）：净升温只扣一半，向下取整，最小 1
        if self_heat:
            cool = -5
            log.append("ANX≥85：灾难化推演自动运行，本轮末不降反升 +5")
        elif after_hit > before:
            cool = max(1, dyn["COOL"] // 2)
        else:
            cool = dyn["COOL"]
        temp = _clamp(after_hit - cool, 0, cap)

        # BOND 溢出（5.2），按轮末 TEMP 结算
        if temp >= 95:
            bond_delta -= 8
        elif temp >= 85:
            bond_delta -= 5
        if before >= 85 and temp < 40:
            bond_delta += 3
        if temp >= 61:
            hot_rounds += 1

        if guilt and bond_delta < 0:
            bond_delta = -_round(abs(bond_delta) * 1.5)
        if bond_delta < 0 and bond_dmg_mul != 1.0:
            bond_delta = -_round(abs(bond_delta) * bond_dmg_mul)
        bond_v = _clamp(bond_v + bond_delta, 0, 100)

        rounds.append({
            "n": i, "move": mid, "name": name, "line": line,
            "temp_before": before, "temp_peak": after_hit, "cool": cool,
            "temp": temp, "zone": temp_zone(temp),
            "bond": bond_v, "bond_delta": bond_delta,
            "persuade": persuade, "log": log,
        })

    tail = []
    if hot_rounds >= 3:
        bond_v = _clamp(bond_v - (_round(3 * 1.5) if guilt else 3), 0, 100)
        tail.append(f"全程进入 61+ 共 {hot_rounds} 轮（≥3），对话结束额外 −3")

    verdict, why = _verdict(p, dyn, temp, bond_v, persuade)

    # "最贵的一句"先看 BOND 损耗再看升温：TEMP 会退，BOND 不会。
    # 两句同样把温度打满，真正贵的是那句把关系账户打穿的。
    worst = max(rounds, key=lambda r: (-r["bond_delta"],
                                       r["temp_peak"] - r["temp_before"])) if rounds else None

    return {
        "profile": p, "dynamics": dyn, "channel": channel,
        "temp_start": temp_start, "temp_end": temp,
        "bond_start": bond_start, "bond_end": bond_v,
        "persuade": persuade, "yield": dyn["YIELD"],
        "hot_rounds": hot_rounds, "tail": tail,
        "rounds": rounds, "verdict": verdict, "verdict_why": why,
        "worst_move": None if not worst else {
            "n": worst["n"], "move": worst["move"], "name": worst["name"],
            "temp_cost": worst["temp_peak"] - worst["temp_before"],
            "bond_cost": -worst["bond_delta"]},
    }


def _verdict(p, dyn, temp, bond, persuade):
    """dynamics.md 6.2 判定表，按顺序匹配，命中即停"""
    y = dyn["YIELD"]
    if bond <= 20:
        return "冷让步", "BOND≤20：那句\"随你便\"不是让步，是断连"
    if p["COM"] >= 75 and p["CTL"] >= 75:
        return "假让步·条件型", "假民主画像强制走假让步，攒多少说服力都一样"
    if persuade >= y and temp <= 35 and bond >= 35:
        return "真让步", f"说服 {persuade} ≥ {y}，且温度已落到 {temp}——她会开始问细节"
    if persuade >= y and temp > 35:
        return "假让步·休战型", f"说服够了但温度还在 {temp}。气头上说的同意一律不算"
    if y * 0.6 <= persuade < y and temp <= 40:
        return "假让步·拖延型", f"说服 {persuade} 过了六成线（{_round(y * 0.6)}），够换一句\"再说吧\""
    return "不让步", f"说服 {persuade} < 六成线 {_round(y * 0.6)}，这次没谈成"


# ---------------------------------------------------------------- 输入

def from_answers(letters):
    letters = [c for c in letters.lower() if c in "abcd"]
    if len(letters) != len(QUIZ):
        raise ValueError(f"需要 {len(QUIZ)} 个答案（a/b/c/d），实际收到 {len(letters)} 个")
    buckets = {d: [] for d in DIMS}
    for (dim, _, _), ch in zip(QUIZ, letters):
        table = SCORES_4 if dim in BANDS_4 else SCORES_3
        buckets[dim].append(table["abcd".index(ch)])
    return {d: _round(sum(v) / len(v)) for d, v in buckets.items()}


def run_quiz():
    print("\n  30 题，凭第一反应答，别想太久。想太久答的是你希望的样子，不是实际的样子。\n")
    letters = []
    for i, (dim, q, opts) in enumerate(QUIZ, 1):
        print(f"  [{i:>2}/30] {q}")
        for ch, text in zip("abcd", opts):
            print(f"          {ch}. {text}")
        while True:
            ans = input("       > ").strip().lower()
            if ans in ("a", "b", "c", "d"):
                letters.append(ans)
                break
            if ans in ("q", "quit"):
                sys.exit("  中断。")
            print("       输 a / b / c / d")
        print()
    print(f"  答案串（下次可直接用 --answers 复现）: {''.join(letters)}\n")
    return from_answers("".join(letters))


def from_scores(text, base=None):
    p = dict(base) if base else {}
    for chunk in text.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "=" not in chunk:
            raise ValueError(f"格式应为 CTL=75，收到 {chunk!r}")
        k, v = chunk.split("=", 1)
        k = k.strip().upper()
        if k not in DIMS:
            raise ValueError(f"未知维度 {k}，合法值：{' '.join(DIMS)}")
        p[k] = _clamp(int(v), 0, 100)
    return p


# ---------------------------------------------------------------- 输出

BAR_W = 24
BOX_W = 62


def bar(score):
    filled = _round(score / 100 * BAR_W)
    return "█" * filled + "░" * (BAR_W - filled)


def _width(s):
    """终端显示宽度，CJK 算 2 格。不这么算，框线就是歪的"""
    return sum(2 if ord(c) > 0x2E80 else 1 for c in s)


def _center(s, width):
    pad = width - _width(s)
    left = pad // 2
    return " " * left + s + " " * (pad - left)


def _section(title):
    return "  ── " + title + "─" * max(2, BOX_W - _width(title) - 2)


def render(p, missing, conf=None):
    conf = conf or {}
    L = []
    L.append("")
    L.append("  ┌" + "─" * BOX_W + "┐")
    L.append("  │" + _center("中国式家长维度画像", BOX_W) + "│")
    L.append("  └" + "─" * BOX_W + "┘")
    L.append("")

    for dim in DIMS:
        v = p[dim]
        mark = CONF_MARK.get(conf.get(dim, "known"), "")
        L.append(f"   {DIM_CN[dim]}  {bar(v)}  {v:>3}  {band_label(dim, v)}{mark}")

    if missing:
        L.append("")
        blind = [DIM_CN[d] for d in DIMS if conf.get(d) == "blind"]
        L.append("   ?  = 未提供，但有耦合规则可依。方向可信，数值别当真。")
        if blind:
            L.append(f"   ?? = 无任何依据，硬填 50：{'、'.join(blind)}。")
            L.append("        凡是靠这几维得出的结论一律作废，去补答对应的题再来。")

    ext = extremes(p)
    if ext:
        L.append("")
        L.append(_section("人格底色（极端维度，优先级最高）"))
        for e in ext:
            L.append(f"   {DIM_CN[e['dim']]} {e['score']} · {e['label']}")

    hits = hit_couplings(p)
    if hits:
        L.append("")
        L.append(_section("命中的耦合规则"))
        for h in hits:
            L.append(f"   ▸ {h['name']}：{h['effect']}")

    blind = blind_dims(conf)
    L.append("")
    L.append(_section("参考类型相似度"))
    if len(blind) >= SIM_BLIND_LIMIT:
        # 拿 6 个硬填的 50 去比对锚点，能算出 84%——那不是画像，是回声。
        # 宁可不报，也不给一个看起来很专业的假数字。
        L.append(f"   不报。10 维里有 {len(blind)} 维是硬填的 50"
                 f"（{'、'.join(DIM_CN[d] for d in blind)}），")
        L.append("   拿它去比对锚点，算出来的百分比只是这些 50 的回声。")
        L.append("   补齐这几维再来，或者跑 --quiz。")
    else:
        ranked = rank_anchors(p)
        if not ranked:
            L.append("   没有锚点达到 55%。这不是数据有问题，是这位家长确实不典型，")
            L.append("   别硬套类型，直接按维度分析。")
        for r in ranked[:3]:
            L.append(f"   {r['type']}  {r['similarity']}%")
            for g in r["top_gaps"]:
                L.append(f"       主要差异 {DIM_CN[g['dim']]}："
                         f"你的 {g['yours']} vs 该类型 {g['anchor']}")

    dyn = dynamics(p)
    bad = tainted(conf)
    flag = lambda k: " ⚠" if k in bad else ""
    L.append("")
    L.append(_section("对话动力学（首轮初始值）"))
    L.append(f"   起手情绪 TEMP₀ {dyn['TEMP0']}{flag('TEMP0')}    "
             f"升温增益 K {dyn['K']}{flag('K')}    降温效率 D {dyn['D']}{flag('D')}")
    L.append(f"   自然冷却 COOL {dyn['COOL']}{flag('COOL')}      "
             f"关系账户 BOND₀ {dyn['BOND0']}{flag('BOND0')}    "
             f"让步阈值 YIELD {dyn['YIELD']}{flag('YIELD')}")
    if dyn["TEMP_CAP"] < 100:
        L.append(f"   TEMP 上限锁定 {dyn['TEMP_CAP']}")
    for n in dyn["notes"]:
        L.append(f"   ▸ {n}")
    if bad:
        L.append("   ⚠ 该值依赖硬填维度，不可用：")
        for k, ds in bad.items():
            L.append(f"       {k} ← {'、'.join(DIM_CN[d] for d in ds)}")

    L.append("")
    L.append(_section("怎么读"))
    L.extend("   " + line for line in read_advice(p, dyn, bad, conf))
    L.append("")
    return "\n".join(L)


def read_advice(p, dyn, bad=None, conf=None):
    """
    bad 是被硬填维度污染的动力学量。被污染的量不出建议——
    基于虚数的读法比不给读法更危险，用户不会记得那个 ⚠。
    """
    bad = bad or {}
    conf = conf or {}
    ok = lambda *keys: not any(k in bad for k in keys)
    solid = lambda *dims: all(conf.get(d, "known") == "known" for d in dims)
    out = []

    if ok("TEMP0"):
        if dyn["TEMP0"] >= 35:
            out.append(f"起手就在施压区（{dyn['TEMP0']}），这场对话没有暖场空间，开口即正题。")
        elif dyn["TEMP0"] <= 15:
            out.append(f"起手很平（{dyn['TEMP0']}），有铺垫的余地，别急着抛结论。")

    if ok("K") and dyn["K"] >= 1.4:
        out.append(f"升温增益 {dyn['K']}，一句雷区话就能点着，措辞比逻辑重要。")
    if ok("D") and dyn["D"] <= 0.8:
        out.append(f"降温效率只有 {dyn['D']}，破冰话打折严重，别指望一句软话翻盘。")

    if ok("YIELD"):
        if dyn["YIELD"] >= 80:
            out.append(f"让步阈值 {dyn['YIELD']}，一次对话里基本攒不出这么多说服力。")
            out.append("正确目标不是说服，是不掉 BOND 地拖到下一次。")
        elif dyn["YIELD"] <= 45:
            out.append(f"让步阈值 {dyn['YIELD']}，讲清楚理由就有机会，别用对抗姿态浪费这个条件。")
        else:
            out.append(f"让步阈值 {dyn['YIELD']}，中等难度：一次谈不完，两三轮有戏。别指望首轮出结果。")

    # 耦合结论只在相关维度是用户亲口给的时候才讲，推断值不足以支撑定性
    if solid("COM", "CTL") and p["COM"] >= 75 and p["CTL"] >= 75:
        out.append("假民主画像：她会认真听完，然后按原计划执行。判断标准只有一个——听完之后结论变了吗。")
    if solid("INV", "COM", "CTL") and p["INV"] <= 20 and p["COM"] <= 24 and p["CTL"] >= 25:
        out.append("诈尸式画像：平时不管，一管就没有铺垫，直接进高档。别在她突然出现时硬刚。")
    if ok("BOND0") and dyn["BOND0"] <= 35:
        out.append(f"关系账户只有 {dyn['BOND0']}，余额太低，任何冲突都是透支。先修关系再谈事。")

    if not out:
        if bad:
            out.append("这份画像撑不起任何读法——能算的量全被硬填值污染了。")
            out.append("跑 --quiz 补 30 题，或者至少把上面标 ?? 的维度说清楚。")
        else:
            out.append("各项都在中段，是可以正常谈事的画像。按 counterplay.md 的正面沟通路线走。")
    return out


def _signed(v):
    """带全角负号的增量，0 不显示。BOND 也可能回正（破冰救场 +3、真让步 +4）"""
    if v == 0:
        return ""
    return f"（+{v}）" if v > 0 else f"（−{-v}）"


def render_sim(sim, who="妈"):
    """dynamics.md 7.1 的输出格式：对话是主体，数字是脚注"""
    p, dyn = sim["profile"], sim["dynamics"]
    L = [""]
    dims = " ".join(f"{d}{p[d]}" for d in DIMS)
    L.append(f"  【建档】{who} · {dims}")
    L.append(f"          TEMP {sim['temp_start']}（{temp_zone(sim['temp_start'])}）"
             f"│ BOND {sim['bond_start']} │ YIELD {dyn['YIELD']} "
             f"│ K {dyn['K']:.2f} │ D {dyn['D']:.2f} │ COOL {dyn['COOL']}")
    if sim["channel"] != "face":
        L.append(f"          渠道：{'电话' if sim['channel'] == 'phone' else '微信文字'}"
                 f"（升温 ×{CHANNELS[sim['channel']]}，BOND 伤害 ×1.2）")
    for n in dyn["notes"]:
        L.append(f"          ▸ {n}")

    for r in sim["rounds"]:
        L.append("")
        L.append(f"  ── 第 {r['n']} 轮 " + "─" * 30)
        L.append(f"  你：「{r['line']}」")
        for line in r["log"]:
            L.append(f"      ▸ {line}")
        peak = "" if r["temp_peak"] == r["temp"] else f" → {r['temp_peak']} → 冷却 −{r['cool']}"
        bd = _signed(r["bond_delta"])
        L.append(f"      TEMP {r['temp_before']}{peak} → {r['temp']}（{r['zone']}）"
                 f"  BOND {r['bond']}{bd}  说服 {r['persuade']}/{dyn['YIELD']}")

    L.append("")
    L.append("  【结算】")
    L.append(f"  TEMP {sim['temp_start']} → {sim['temp_end']} │ "
             f"BOND {sim['bond_start']} → {sim['bond_end']}"
             f"{_signed(sim['bond_end'] - sim['bond_start'])} │ "
             f"说服 {sim['persuade']}/{sim['yield']}")
    for t in sim["tail"]:
        L.append(f"      {t}")
    L.append(f"      判定：{sim['verdict']}——{sim['verdict_why']}")
    w = sim["worst_move"]
    if w and (w["temp_cost"] > 0 or w["bond_cost"] > 0):
        cost = f"TEMP +{w['temp_cost']}"
        if w["bond_cost"] > 0:
            cost += f"，BOND −{w['bond_cost']}"
        L.append(f"      最贵的一句：第 {w['n']} 轮 {w['move']} {w['name']}（{cost}）")
    L.append("")
    return "\n".join(L)


def list_moves(p=None):
    L = ["", "  雷区（升温）", ""]
    for mid, (name, line, base, bonuses) in TRIGGERS.items():
        extra = f"  → 对当前画像 +{_best_bonus(p, bonuses)}" if p else ""
        L.append(f"   {mid:<4} {name:<8} 基础 +{base:<3}「{line}」{extra}")
    L.append("")
    L.append("  破冰（降温）　✔ = 爆发区仍生效")
    L.append("")
    for mid, (name, line, base, bonuses, hot) in COOLERS.items():
        extra = f"  → 对当前画像 −{_best_bonus(p, bonuses)}" if p else ""
        L.append(f"   {mid:<4}{'✔' if hot else ' '} {name:<8} 基础 −{base:<3}「{line}」{extra}")
    L.append("")
    L.append("  用法：--simulate T9,T1,C18   （顺序即出牌顺序）")
    L.append("")
    return "\n".join(L)


def _sim_json(sim):
    return {
        "version": VERSION,
        "profile": sim["profile"],
        "dynamics": sim["dynamics"],
        "channel": sim["channel"],
        "temp": {"start": sim["temp_start"], "end": sim["temp_end"],
                 "zone": temp_zone(sim["temp_end"])},
        "bond": {"start": sim["bond_start"], "end": sim["bond_end"],
                 "delta": sim["bond_end"] - sim["bond_start"]},
        "persuade": sim["persuade"], "yield": sim["yield"],
        "hot_rounds": sim["hot_rounds"],
        "verdict": sim["verdict"], "verdict_why": sim["verdict_why"],
        "worst_move": sim["worst_move"],
        "rounds": [{k: v for k, v in r.items()} for r in sim["rounds"]],
        "archive": f"BOND:{sim['bond_end']}",
    }


# dynamics.md 7.2 的完整算例，作为可执行的回归基准
DEMO_PROFILE = dict(CTL=72, WRM=48, INV=68, ANX=60, COM=32,
                    VAL=30, FIN=58, EXP=68, SOC=38, IND=32)
DEMO_MOVES = ["T21", "T9", "T1", "C2", "C18"]


def dump_quiz():
    L = ["# 30 题快测题库", "",
         "由 `scripts/profile.py` 自动导出，改题库请改脚本，不要改这里。", "",
         "答完把 30 个字母连起来，跑 `python3 scripts/profile.py --answers <你的答案串>`。", ""]
    cur = None
    for i, (dim, q, opts) in enumerate(QUIZ, 1):
        if dim != cur:
            cur = dim
            L.append(f"## {DIM_CN[dim]}（{dim}）")
            L.append("")
        L.append(f"**{i}. {q}**")
        L.append("")
        for ch, text in zip("abcd", opts):
            L.append(f"- {ch}. {text}")
        L.append("")
    L.append("## 计分")
    L.append("")
    L.append(f"- 4 档维度（{'/'.join(BANDS_4)}）：a={SCORES_4[0]} b={SCORES_4[1]} c={SCORES_4[2]} d={SCORES_4[3]}")
    L.append(f"- 3 档维度（{'/'.join(BANDS_3)}）：a={SCORES_3[0]} b={SCORES_3[1]} c={SCORES_3[2]} d={SCORES_3[3]}")
    L.append("- 每个维度 3 题，取平均，四舍五入。")
    L.append("")
    return "\n".join(L)


# ---------------------------------------------------------------- 缺失维度推断

def infer_missing(p):
    """
    没给的维度不能填 50——那会造出一个不存在的"平均家长"。
    按 dimensions.md 第七节的耦合方向做保守推断，并标出每一维的可信度。

    v0.4 的自相矛盾：注释写着"不能填 50"，实现却先把所有缺失项设成 50，
    只覆盖规则命中的那几个，命不中的就静默留在 50——正是它自己警告的陷阱，
    而且用户看不出哪些是推出来的、哪些是硬填的。v0.5 把这层区分显式化：

      known    用户给的，照单全收
      inferred 有耦合规则可依，方向可信、数值别当真
      blind    无任何依据的 50。凡是靠它得出的结论一律作废
    """
    missing = [d for d in DIMS if d not in p]
    conf = {d: ("known" if d in p else "blind") for d in DIMS}
    if not missing:
        return dict(p), [], conf

    guess = dict(p)
    for d in missing:
        guess[d] = 50

    known = set(p)
    # 控制高 → 沟通偏低、独立偏低；焦虑高 → 期望偏高；温度低 → 关系相关维度偏低
    rules = [
        ("CTL", "COM", lambda v: 100 - v, 0.6),
        ("CTL", "IND", lambda v: 100 - v, 0.6),
        ("CTL", "SOC", lambda v: 100 - v, 0.5),
        ("ANX", "EXP", lambda v: v, 0.5),
        ("EXP", "ANX", lambda v: v, 0.5),
        ("COM", "CTL", lambda v: 100 - v, 0.5),
        ("WRM", "INV", lambda v: v, 0.4),
        ("VAL", "SOC", lambda v: v, 0.5),
        ("IND", "CTL", lambda v: 100 - v, 0.5),
    ]
    for src, dst, fn, weight in rules:
        if src in known and dst in missing:
            guess[dst] = _round(50 * (1 - weight) + fn(p[src]) * weight)
            conf[dst] = "inferred"
    return {d: _clamp(guess[d], 0, 100) for d in DIMS}, missing, conf


CONF_MARK = {"known": "", "inferred": "  ?", "blind": "  ??"}

# 每个动力学量真正依赖哪几维。硬填的 50 会顺着这张表往下游污染，
# 不标出来的话，用户会把一个凭空造出来的 K=1.30 当成结论拿去用。
DYN_DEPS = {
    "TEMP0": ("ANX", "CTL", "EXP", "WRM", "COM"),
    "K":     ("ANX", "CTL", "COM"),
    "D":     ("COM", "WRM"),
    "COOL":  ("COM", "ANX"),
    "BOND0": ("WRM", "COM", "INV", "CTL"),
    "YIELD": ("CTL", "EXP", "COM", "VAL", "IND"),
}

# 10 维里有这么多维是硬填的，相似度就别报了——那不是画像，是回声
SIM_BLIND_LIMIT = 4


def blind_dims(conf):
    return [d for d in DIMS if conf.get(d) == "blind"]


def tainted(conf):
    """返回 {动力学量: [污染它的 blind 维度]}，不在表里的量才可信"""
    blind = set(blind_dims(conf))
    return {k: [d for d in deps if d in blind]
            for k, deps in DYN_DEPS.items() if blind & set(deps)}


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(
        description="中国式家长维度画像计算器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("用法:")[-1])
    ap.add_argument("--version", action="version", version=f"chinese-parents-skill {VERSION}")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--quiz", action="store_true", help="交互答 30 题")
    g.add_argument("--answers", metavar="ABCD...", help="30 个字母的答案串")
    g.add_argument("--dump-quiz", action="store_true", help="导出 Markdown 题库")
    ap.add_argument("--scores", metavar="CTL=75,ANX=80", help="直接指定维度分，可只给一部分")
    ap.add_argument("--type", metavar="名称", help="加载锚点画像：" + " / ".join(ANCHORS))
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--simulate", metavar="T9,C18", help="多轮推演，逗号分隔词条 id")
    ap.add_argument("--simulate-demo", action="store_true", help="复现 dynamics.md 7.2 算例")
    ap.add_argument("--list-moves", action="store_true", help="列出全部雷区/破冰词条")
    ap.add_argument("--bond", type=int, metavar="N", help="从存档读入 BOND，跨对话累积用")
    ap.add_argument("--channel", choices=list(CHANNELS), default="face",
                    help="face 当面 / phone 电话 / wechat 微信文字")
    ap.add_argument("--who", default="妈", help="称呼，仅影响输出")
    args = ap.parse_args()

    if args.dump_quiz:
        print(dump_quiz())
        return

    if args.simulate_demo:
        sim = simulate(DEMO_PROFILE, DEMO_MOVES, channel="face")
        print(render_sim(sim, "妈") if not args.json
              else json.dumps(_sim_json(sim), ensure_ascii=False, indent=2))
        return

    base = None
    if args.type:
        if args.type not in ANCHORS:
            sys.exit(f"未知类型 {args.type}\n可选：{' / '.join(ANCHORS)}")
        base = ANCHORS[args.type]

    try:
        if args.quiz:
            profile = run_quiz()
        elif args.answers:
            profile = from_answers(args.answers)
        elif args.scores:
            profile = from_scores(args.scores, base)
        elif base:
            profile = dict(base)
        elif args.list_moves:
            print(list_moves())
            return
        else:
            ap.print_help()
            return
    except ValueError as e:
        sys.exit(f"输入有问题：{e}")

    profile, missing, conf = infer_missing(profile)

    if args.list_moves:
        print(list_moves(profile))
        return

    if args.simulate:
        blind = blind_dims(conf)
        if len(blind) >= SIM_BLIND_LIMIT:
            print(f"  ⚠ {len(blind)} 个维度是硬填的 50"
                  f"（{'、'.join(DIM_CN[d] for d in blind)}），"
                  f"推出来的每一度都是虚的。\n"
                  f"    先补齐画像再推演，别拿这个结果做决定。\n", file=sys.stderr)
        try:
            sim = simulate(profile, args.simulate.split(","),
                           bond=args.bond, channel=args.channel)
        except ValueError as e:
            sys.exit(f"推演失败：{e}")
        print(json.dumps(_sim_json(sim), ensure_ascii=False, indent=2) if args.json
              else render_sim(sim, args.who))
        return

    if args.json:
        print(json.dumps({
            "version": VERSION,
            "profile": profile,
            "inferred": missing,
            "confidence": conf,
            "blind_dims": blind_dims(conf),
            "tainted_dynamics": tainted(conf),
            "similarity_reportable": len(blind_dims(conf)) < SIM_BLIND_LIMIT,
            "bands": {d: band_label(d, profile[d]) for d in DIMS},
            "extremes": extremes(profile),
            "couplings": hit_couplings(profile),
            "similar_types": rank_anchors(profile),
            "dynamics": dynamics(profile),
        }, ensure_ascii=False, indent=2))
    else:
        print(render(profile, missing, conf))


if __name__ == "__main__":
    main()
