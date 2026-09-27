#!/usr/bin/env python3
"""
build-site.py —— 从仓库实装数据生成官网 index.html（数据永不漂移）

统计 teams/*/agents 与 teams/*/skills 及通用 skills/，计算官网模板占位符，
生成 site/index.html。

用法：
  python3 build-site.py            生成 site/index.html（覆盖写）
  python3 build-site.py --check    生成并对比现有 site/index.html，不一致则退出码 1（CI 防漂移）

口径（与 verify.py / SKILLS_INDEX.md 保持一致）：
  - 专家总数 = 所有团队 agents 合计
  - 团队专属技能 = teams/*/skills 子目录数合计
  - 通用技能 = skills/ 子目录数
  - 总技能 = 团队专属 + 通用
  - software 团队无独立 skills，绑定 3 个通用技能（api-design-reviewer / test-case-generator-v2 / uml-and-software-architecture-visualization）
  - core 单兵 = 所有 teams/*/agents/ 下 core-* 前缀的 agent
"""

import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

# 所有团队（顺序即官网展示顺序）
TEAMS = [
    "academic-paper-team",
    "fullstack-web-team",
    "math-modeling-team",
    "software-dev-team",
    "visual-design-team",
    "content-writing-team",
    "video-production-team",
    "data-analysis-team",
    "marketing-team",
    "ecommerce-ops-team",
    "product-team",
    "finance-team",
    "hr-team",
    "legal-compliance-team",
    "translation-team",
    "education-training-team",
    "audio-podcast-team",
    "game-design-team",
]

# 团队卡片元数据：展示名 / 场景描述 / 热门角色标签 / 全部角色标签（取前5个展示）
TEAM_META = {
    "academic-paper-team": {
        "name": "学术论文战队",
        "scene": "选题、文献、研究设计、写作、审稿、期刊匹配到投稿交付，一条链路出完整论文包。",
        "hot": "选题策略师",
        "roles": ["选题策略师", "文献综述师", "写作主笔", "模拟审稿", "格式守卫"],
        "lead": "academic-team-lead",
    },
    "fullstack-web-team": {
        "name": "全栈 Web 战队",
        "scene": "需求、架构、前后端、API、数据、DevOps、测试、安全、性能到可上线交付包。",
        "hot": "系统架构师",
        "roles": ["系统架构师", "前端工程师", "后端工程师", "DevOps", "QA"],
        "lead": "fullstack-team-lead",
    },
    "math-modeling-team": {
        "name": "数学建模战队",
        "scene": "国赛 72 小时全程托管：选题、建模、求解、写作到查重安全的论文 PDF。",
        "hot": "建模专家",
        "roles": ["建模专家", "算法求解师", "论文质检", "复现查重"],
        "lead": "math-team-lead",
    },
    "software-dev-team": {
        "name": "软件开发战队",
        "scene": "需求拆解、架构、实现、评审、测试到交付，强门禁、小步走、可回滚。",
        "hot": "代码质量评审",
        "roles": ["蓝图师", "服务端", "代码质量评审", "测试"],
        "lead": "software-team-lead",
    },
    "visual-design-team": {
        "name": "视觉设计战队",
        "scene": "需求简报拆解、风格定调、海报/电商/品牌/插画产出到只读评审质检交付。",
        "hot": "电商视觉",
        "roles": ["海报设计师", "电商视觉", "品牌 VI", "插画师", "评审"],
        "lead": "visual-team-lead",
    },
    "content-writing-team": {
        "name": "内容写作战队",
        "scene": "选题、长文/社媒/短视频脚本成稿、标题打磨、多平台改编到事实核查终检。",
        "hot": "事实核查",
        "roles": ["策略师", "长文作者", "社媒作者", "短视频编剧", "事实核查"],
        "lead": "content-team-lead",
    },
    "video-production-team": {
        "name": "视频创作战队",
        "scene": "从 brief 到成片：编剧导演、分镜、剪辑、调色、字幕到质检闸门合规发布。",
        "hot": "编剧导演",
        "roles": ["编剧导演", "分镜师", "剪辑师", "调色师", "质检"],
        "lead": "video-team-lead",
    },
    "data-analysis-team": {
        "name": "数据分析战队",
        "scene": "数据清洗、指标体系、漏斗归因、A/B 实验、可视化报表到数据治理与质检交付。",
        "hot": "A/B 实验",
        "roles": ["数据清洗", "漏斗归因", "A/B 实验", "可视化", "数据治理"],
        "lead": "data-analysis-team-lead",
    },
    "marketing-team": {
        "name": "市场营销战队",
        "scene": "品牌定位、策略规划、活动策划、社媒/SEO/增长、KOC 管理到营销数据复盘。",
        "hot": "增长黑客",
        "roles": ["策略规划", "活动策划", "增长黑客", "品牌公关", "KOC 管理"],
        "lead": "marketing-team-lead",
    },
    "ecommerce-ops-team": {
        "name": "电商运营战队",
        "scene": "选品调研、Listing 优化、店铺运营、定价供应链、客服物流到数据驱动增长。",
        "hot": "选品策略",
        "roles": ["选品", "Listing 优化", "店铺运营", "定价策略", "供应链"],
        "lead": "ecommerce-ops-team-lead",
    },
    "product-team": {
        "name": "产品管理战队",
        "scene": "用户研究、PRD 撰写、路线图规划、竞品分析、数据驱动到体验评审与交付。",
        "hot": "PRD 撰写",
        "roles": ["用户研究", "PRD 撰写", "路线图", "竞品分析", "体验评审"],
        "lead": "product-team-lead",
    },
    "finance-team": {
        "name": "财务会计战队",
        "scene": "会计核算、预算规划、财务报告、税务合规、成本资金管理到审计支持交付。",
        "hot": "税务合规",
        "roles": ["会计核算", "预算规划", "财务报告", "税务顾问", "成本控制"],
        "lead": "finance-team-lead",
    },
    "hr-team": {
        "name": "人力资源战队",
        "scene": "招聘 JD、面试评估、入职设计、绩效薪酬、培训发展到员工关系全流程交付。",
        "hot": "面试评估",
        "roles": ["招聘专员", "JD 撰写", "面试官", "绩效管理", "培训开发"],
        "lead": "hr-team-lead",
    },
    "legal-compliance-team": {
        "name": "法律合规战队",
        "scene": "合同审查、数据隐私、知识产权、劳动法、监管跟踪到法律文书起草交付。",
        "hot": "数据隐私",
        "roles": ["合同审查", "合规官", "数据隐私", "知识产权", "监管跟踪"],
        "lead": "legal-team-lead",
    },
    "translation-team": {
        "name": "翻译本地化战队",
        "scene": "中英互译、技术翻译、术语管理、文化适配、字幕翻译到 QA 校对全流程交付。",
        "hot": "技术翻译",
        "roles": ["中英译", "英中译", "技术翻译", "术语专家", "文化适配"],
        "lead": "translation-team-lead",
    },
    "education-training-team": {
        "name": "教育培训战队",
        "scene": "课程设计、课件撰写、出题解析、讲解辅导、测评设计到学习路径规划交付。",
        "hot": "出题解析",
        "roles": ["课程设计", "课件撰写", "出题师", "讲解师", "学习路径"],
        "lead": "education-team-lead",
    },
    "audio-podcast-team": {
        "name": "音频播客战队",
        "scene": "播客脚本、声音导演、剪辑音效、配乐主持、品牌包装到音频质检评审交付。",
        "hot": "声音导演",
        "roles": ["脚本编剧", "声音导演", "音频剪辑", "音效设计", "主播主持"],
        "lead": "audio-team-lead",
    },
    "game-design-team": {
        "name": "游戏设计战队",
        "scene": "玩法设计、关卡数值、叙事经济、原型开发、美术指导到 QA 评审全流程交付。",
        "hot": "数值平衡",
        "roles": ["玩法设计", "关卡设计", "数值平衡", "叙事设计", "游戏经济"],
        "lead": "game-team-lead",
    },
}

SOFTWARE_BOUND_SKILLS = 3  # 绑定通用 skills/ 中 3 个（见 SKILLS_INDEX.md）


def count_agents(team):
    d = os.path.join(ROOT, "teams", team, "agents")
    return (
        len([f for f in os.listdir(d) if f.endswith(".md")]) if os.path.isdir(d) else 0
    )


def count_team_skills(team):
    d = os.path.join(ROOT, "teams", team, "skills")
    if not os.path.isdir(d):
        return 0
    return len([x for x in os.listdir(d) if os.path.isdir(os.path.join(d, x))])


def count_general_skills():
    d = os.path.join(ROOT, "skills")
    return len([x for x in os.listdir(d) if os.path.isdir(os.path.join(d, x))])


def count_core_agents():
    n = 0
    for team in TEAMS:
        d = os.path.join(ROOT, "teams", team, "agents")
        if not os.path.isdir(d):
            continue
        n += len(
            [f for f in os.listdir(d) if f.startswith("core-") and f.endswith(".md")]
        )
    return n


def generate_team_cards(team_agents, team_skills):
    """生成所有团队卡片 HTML + 通用保障卡。"""
    cards = []
    for team in TEAMS:
        meta = TEAM_META[team]
        n_agents = team_agents[team]
        n_skills = team_skills[team]
        roles_html = ""
        for i, role in enumerate(meta["roles"][:5]):
            cls = "role hot" if role == meta["hot"] else "role"
            roles_html += f'<span class="{cls}">{role}</span>'
        card = """      <div class="team-card">
        <div class="t-head"><span class="t-name">{}</span><span class="t-num">{} 人 · {} 技能</span></div>
        <div class="t-scene">{}</div>
        <div class="t-roles">{}</div>
        <div class="t-meta"><span><b>入口：</b>{}</span></div>
      </div>""".format(
            meta["name"], n_agents, n_skills, meta["scene"], roles_html, meta["lead"]
        )
        cards.append(card)
    # 通用保障卡
    general = count_general_skills()
    n_core = count_core_agents()
    core_card = f"""      <div class="team-card core-card">
        <div class="t-head"><span class="t-name">通用保障层（跨团队）</span><span class="t-num">{general} 技能 · {n_core} 单兵</span></div>
        <div class="t-scene">准确性核查、交叉验证、质检门禁、事实核查单兵、深度检索与安全扫描——所有团队共享的底座。</div>
        <div class="t-roles"><span class="role hot">事实核查官</span><span class="role">质检门禁</span><span class="role">准确性核查</span><span class="role">交叉验证</span><span class="role">安全扫描</span></div>
        <div class="t-meta"><span><b>调用：</b>任意团队交付前</span></div>
      </div>"""
    cards.append(core_card)
    return "\n".join(cards)


def compute():
    stats = {}
    team_agents = {}
    team_skills = {}
    for team in TEAMS:
        a = count_agents(team)
        s = count_team_skills(team)
        if team == "software-dev-team":
            s = SOFTWARE_BOUND_SKILLS
        team_agents[team] = a
        team_skills[team] = s
    general = count_general_skills()
    n_agents = sum(team_agents.values())
    # 团队专属技能（不含软件绑定的通用）
    n_team_skills = sum(team_skills.values()) - SOFTWARE_BOUND_SKILLS
    n_skills = n_team_skills + general
    n_teams = len(TEAMS)
    n_core = count_core_agents()

    stats["N_AGENTS"] = n_agents
    stats["N_SKILLS"] = n_skills
    stats["N_TEAMS"] = n_teams
    stats["N_TEAM_SKILLS"] = n_team_skills
    stats["N_GENERAL_SKILLS"] = general
    stats["N_CORE_UNITS"] = n_core

    # BAR_DATA：横向条形图，按 TEAMS 顺序（ECharts yAxis data 与 series data 对应）
    bar_labels = [TEAM_META[t]["name"].replace("战队", "") for t in TEAMS]
    bar_values = [team_agents[t] for t in TEAMS]
    stats["BAR_LABELS"] = json_dumps(bar_labels)
    stats["BAR_DATA"] = json_dumps(bar_values)

    # 技能构成：团队专属 vs 通用（两段 donut）
    stats["DONUT_DATA"] = json_dumps(
        [
            {"value": n_team_skills, "name": "团队专属技能"},
            {"value": general, "name": "通用保障技能"},
        ]
    )

    # 团队卡片 HTML
    stats["TEAM_CARDS"] = generate_team_cards(team_agents, team_skills)

    return stats


def json_dumps(obj):
    """简易 JSON 序列化（避免 import json 在模板替换时的转义问题）。"""
    import json

    return json.dumps(obj, ensure_ascii=False)


def build(stats):
    with open(os.path.join(ROOT, "site", "template.html"), encoding="utf-8") as fh:
        tpl = fh.read()
    for k, v in stats.items():
        tpl = tpl.replace("{{" + k + "}}", str(v))
    leftovers = re.findall(r"\{\{[A-Z_]+\}\}", tpl)
    if leftovers:
        raise SystemExit(f"模板存在未替换占位符: {leftovers}")
    return tpl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--check", action="store_true", help="对比现有 site/index.html，不一致则失败"
    )
    args = ap.parse_args()
    stats = compute()
    out = build(stats)
    if args.check:
        target = os.path.join(ROOT, "site", "index.html")
        if not os.path.exists(target):
            print("site/index.html 不存在，请先运行 python3 build-site.py")
            sys.exit(1)
        with open(target, encoding="utf-8") as fh:
            cur = fh.read()
        if cur != out:
            print(
                "✗ site/index.html 与仓库实装数据不一致（数据漂移）。请运行 python3 build-site.py 重新生成。"
            )
            sys.exit(1)
        print(
            f"✓ site/index.html 与仓库实装一致（{stats['N_AGENTS']} 专家 / {stats['N_SKILLS']} 技能 / {stats['N_TEAMS']} 团队）"
        )
    else:
        target = os.path.join(ROOT, "site", "index.html")
        with open(target, "w", encoding="utf-8") as f:
            f.write(out)
        print(
            f"✓ site/index.html 已生成：{stats['N_AGENTS']} 专家 / {stats['N_SKILLS']} 技能 / {stats['N_TEAMS']} 团队 / {stats['N_GENERAL_SKILLS']} 通用技能 / {stats['N_CORE_UNITS']} core 单兵"
        )


if __name__ == "__main__":
    main()
