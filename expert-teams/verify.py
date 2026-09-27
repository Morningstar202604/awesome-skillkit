#!/usr/bin/env python3
"""全局内容质量校验脚本：验证 skill 包、agent frontmatter、结构完整性（平台中立，不依赖任何具体 agent 框架）。"""

import os
import re
import sys

import yaml

import effectiveness

BASE = os.path.dirname(os.path.abspath(__file__))
errors = []
warnings = []


def err(msg):
    errors.append(msg)
    print(f"  ❌ {msg}")


def ok(msg):
    print(f"  ✅ {msg}")


def warn(msg):
    warnings.append(msg)
    print(f"  ⚠️  {msg}")


def parse_frontmatter(text):
    """解析 markdown 文件的 YAML frontmatter，返回 (dict, body)。"""
    if not text.startswith("---"):
        return None, text
    lines = text.split("\n")
    # 找到闭合的 ---
    close_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            close_idx = i
            break
    if close_idx is None:
        return None, text
    fm_text = "\n".join(lines[1:close_idx])
    body = "\n".join(lines[close_idx + 1 :])
    try:
        fm = yaml.safe_load(fm_text)
        if fm is None:
            fm = {}
        return fm, body
    except yaml.YAMLError as e:
        return f"YAML_ERROR: {e}", body


# ═══════════════════════════════════════════════════════
# 1. 校验 skill 包
# ═══════════════════════════════════════════════════════
print("\n=== 1. Skill 包校验 ===")
skill_dirs = []
# 团队 skills
for team in os.listdir(f"{BASE}/teams"):
    skills_path = f"{BASE}/teams/{team}/skills"
    if os.path.isdir(skills_path):
        for name in sorted(os.listdir(skills_path)):
            d = f"{skills_path}/{name}"
            if os.path.isdir(d):
                skill_dirs.append((name, d, f"teams/{team}/skills"))
# 通用 skills
if os.path.isdir(f"{BASE}/skills"):
    for name in sorted(os.listdir(f"{BASE}/skills")):
        d = f"{BASE}/skills/{name}"
        if os.path.isdir(d):
            skill_dirs.append((name, d, "skills"))

print(f"  发现 {len(skill_dirs)} 个 skill 包")
skill_names = set()
for name, path, location in skill_dirs:
    skill_md = f"{path}/SKILL.md"
    if not os.path.isfile(skill_md):
        err(f"[{name}] 缺少 SKILL.md ({location})")
        continue
    with open(skill_md, encoding="utf-8") as fh:
        text = fh.read()
    fm, body = parse_frontmatter(text)
    if fm is None:
        err(f"[{name}] 无 frontmatter")
        continue
    if isinstance(fm, str) and fm.startswith("YAML_ERROR"):
        err(f"[{name}] frontmatter YAML 语法错误: {fm}")
        continue
    # name 校验
    if "name" not in fm:
        err(f"[{name}] frontmatter 缺 name 字段")
    elif fm["name"] != name:
        err(f"[{name}] name='{fm['name']}' 与目录名不一致")
    # name 格式校验
    if "name" in fm and not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", str(fm["name"])):
        err(f"[{name}] name 格式不合规（须小写字母数字单连字符）")
    # description 校验
    if "description" not in fm:
        err(f"[{name}] frontmatter 缺 description 字段")
    else:
        desc_len = len(str(fm["description"]))
        if desc_len < 1 or desc_len > 1024:
            err(f"[{name}] description 长度 {desc_len} 超出 1-1024")
    # 行数校验
    line_count = len(text.split("\n"))
    if line_count < 50:
        warn(f"[{name}] 仅 {line_count} 行，建议 50-120 行")
    elif line_count > 120:
        warn(f"[{name}] {line_count} 行，超出 120 行上限")
    # 检查关键章节
    if "## " not in body:
        warn(f"[{name}] 正文无 ## 章节标题")
    skill_names.add(name)

ok(f"{len(skill_dirs)} 个 skill 包校验完成（{len(errors)} 错误，{len(warnings)} 警告）")

# ═══════════════════════════════════════════════════════
# 2. 校验 agent frontmatter（平台中立）
# ═══════════════════════════════════════════════════════
print("\n=== 2. Agent frontmatter 校验 ===")
agent_files = []
for team in os.listdir(f"{BASE}/teams"):
    agents_path = f"{BASE}/teams/{team}/agents"
    if os.path.isdir(agents_path):
        for fname in sorted(os.listdir(agents_path)):
            if fname.endswith(".md"):
                agent_files.append((fname[:-3], f"{agents_path}/{fname}", team))

# 加上 project-director
agent_files.append(("project-director", f"{BASE}/project-director.md", "root"))

print(f"  发现 {len(agent_files)} 个 agent 文件")
READONLY_CORE = {
    "core-architect",
    "core-code-reviewer",
    "core-security-auditor",
    "core-test-engineer",
    "core-fact-checker",
    "visual-design-reviewer",
    "content-reviewer",
    "video-performance-analyst",
    "video-quality-reviewer",
}
# 平台中立：frontmatter 中禁止出现平台专属字段
FORBIDDEN_FIELDS = {"mode", "permission", "hidden"}

agent_errors_before = len(errors)
for agent_id, path, team in agent_files:
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    fm, body = parse_frontmatter(text)
    if fm is None:
        err(f"[{agent_id}] 无 frontmatter")
        continue
    if isinstance(fm, str) and fm.startswith("YAML_ERROR"):
        err(f"[{agent_id}] frontmatter YAML 语法错误: {fm}")
        continue
    # description 校验
    if "description" not in fm:
        err(f"[{agent_id}] 缺 description")
    else:
        desc_len = len(str(fm["description"]))
        if desc_len < 1 or desc_len > 1024:
            err(f"[{agent_id}] description 长度 {desc_len} 超出 1-1024")
    # 禁止 model 字段
    if "model" in fm:
        err(f"[{agent_id}] 不应有 model 字段")
    # 禁止平台专属字段
    for bad in FORBIDDEN_FIELDS:
        if bad in fm:
            err(f"[{agent_id}] 不应有平台专属字段 '{bad}'")
    # temperature：若存在则必须在 0-1 范围（不存在不报错）
    if "temperature" in fm:
        t = fm["temperature"]
        if not isinstance(t, (int, float)) or isinstance(t, bool) or t < 0 or t > 1:
            err(f"[{agent_id}] temperature={t} 不合规（须在 0-1 之间）")
    # 只读角色：若配置了 tools，则 write/edit 必须为 false
    if agent_id in READONLY_CORE and "tools" in fm and isinstance(fm["tools"], dict):
        if fm["tools"].get("write") is not False:
            err(f"[{agent_id}] 只读角色 tools.write 应为 false")
        if fm["tools"].get("edit") is not False:
            err(f"[{agent_id}] 只读角色 tools.edit 应为 false")

agent_err_count = len(errors) - agent_errors_before
ok(f"{len(agent_files)} 个 agent 校验完成（{agent_err_count} 错误）")

# ═══════════════════════════════════════════════════════
# 3. 校验 8 个重写 agent 的结构完整性
# ═══════════════════════════════════════════════════════
print("\n=== 3. 重写 Agent 结构校验 ===")
REWRITE_AGENTS = [
    "teams/academic-paper-team/agents/core-researcher.md",
    "teams/fullstack-web-team/agents/core-architect.md",
    "teams/fullstack-web-team/agents/core-code-reviewer.md",
    "teams/fullstack-web-team/agents/core-security-auditor.md",
    "teams/fullstack-web-team/agents/core-test-engineer.md",
    "teams/software-dev-team/agents/software-architect.md",
    "teams/software-dev-team/agents/software-reviewer.md",
    "teams/software-dev-team/agents/software-tester.md",
]
REQUIRED_SECTIONS = ["核心能力", "工作流程", "输出规范", "输入规范", "注意事项"]
for rel_path in REWRITE_AGENTS:
    path = f"{BASE}/{rel_path}"
    if not os.path.isfile(path):
        err(f"[{rel_path}] 文件不存在")
        continue
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    line_count = len(text.split("\n"))
    if line_count < 30:
        err(f"[{rel_path}] 仅 {line_count} 行，疑似未重写")
    for section in REQUIRED_SECTIONS:
        if section not in text:
            err(f"[{rel_path}] 缺章节: {section}")
    # 检查交接模板
    if "交接模板" not in text:
        err(f"[{rel_path}] 缺交接模板")
ok("8 个重写 agent 结构校验完成")

# ═══════════════════════════════════════════════════════
# 4. 人数口径校验
# ═══════════════════════════════════════════════════════
print("\n=== 4. 人数口径校验 ===")
team_counts = {}
for agent_id, path, team in agent_files:
    if team == "root":
        continue
    team_counts[team] = team_counts.get(team, 0) + 1

# 规模口径单一来源：effectiveness.EXPECTED_TEAM_AGENTS（与第 7 节共用）
expected = effectiveness.EXPECTED_TEAM_AGENTS
total = 0
for team, count in sorted(team_counts.items()):
    exp = expected.get(team, "?")
    status = "✅" if count == exp else "❌"
    print(f"  {status} {team}: {count} (预期 {exp})")
    total += count
    if count != exp:
        err(f"{team} 人数 {count} != 预期 {exp}")
expected_total = sum(expected.values())
print(f"  总计: {total} (预期 {expected_total})")
if total != expected_total:
    err(f"总人数 {total} != {expected_total}")

# ═══════════════════════════════════════════════════════
# 5. 关键文件存在性校验（平台中立）
# ═══════════════════════════════════════════════════════
print("\n=== 5. 关键文件校验 ===")
for f in [
    "SKILLS_INDEX.md",
    "README.md",
    "AGENTS.md",
    "project-director.md",
    "export-agents.py",
    "export-platforms.py",
    "effectiveness.py",
    "orchestration-protocol.md",
]:
    if os.path.isfile(f"{BASE}/{f}"):
        ok(f"{f} 存在")
    else:
        err(f"{f} 不存在")

# ═══════════════════════════════════════════════════════
# 6. 团队 skill 绑定检查
# ═══════════════════════════════════════════════════════
print("\n=== 6. 团队 skill 绑定检查 ===")
unbound_count = 0
total_checked = 0


def read_agent_bodies(agents_path):
    bodies = []
    if os.path.isdir(agents_path):
        for fname in sorted(os.listdir(agents_path)):
            if fname.endswith(".md"):
                with open(f"{agents_path}/{fname}", encoding="utf-8") as fh:
                    bodies.append(fh.read())
    return bodies


# 团队 skill：每个 teams/<team>/skills/* 必须被该团队至少 1 个 agent 显式反引号引用
for team in sorted(os.listdir(f"{BASE}/teams")):
    skills_path = f"{BASE}/teams/{team}/skills"
    agents_path = f"{BASE}/teams/{team}/agents"
    if not os.path.isdir(skills_path):
        continue
    team_body = "\n".join(read_agent_bodies(agents_path))
    for skill_name in sorted(os.listdir(skills_path)):
        if not os.path.isdir(f"{skills_path}/{skill_name}"):
            continue
        total_checked += 1
        if f"`{skill_name}`" not in team_body:
            err(f"[skill绑定] {team}/{skill_name} 未被该团队任何 agent 显式反引号引用")
            unbound_count += 1

# 通用 skill：skills/* 必须被至少 1 个 agent（全团队 + project-director）显式反引号引用
general_skills_path = f"{BASE}/skills"
if os.path.isdir(general_skills_path):
    all_bodies = []
    for team in sorted(os.listdir(f"{BASE}/teams")):
        all_bodies.extend(read_agent_bodies(f"{BASE}/teams/{team}/agents"))
    pd_path = f"{BASE}/project-director.md"
    if os.path.isfile(pd_path):
        with open(pd_path, encoding="utf-8") as fh:
            all_bodies.append(fh.read())
    global_body = "\n".join(all_bodies)
    for skill_name in sorted(os.listdir(general_skills_path)):
        if not os.path.isdir(f"{general_skills_path}/{skill_name}"):
            continue
        total_checked += 1
        if f"`{skill_name}`" not in global_body:
            err(f"[skill绑定] 通用 skill {skill_name} 未被任何 agent 显式反引号引用")
            unbound_count += 1

ok(f"skill 绑定检查：{total_checked} 个 skill，{unbound_count} 个未绑定")

# ═══════════════════════════════════════════════════════
# 7. 团队有效性与跨文档一致性（见 effectiveness.py）
# ═══════════════════════════════════════════════════════
print("\n=== 7. 团队有效性检查 ===")
eff_errors = effectiveness.check_all(BASE)
for e in eff_errors:
    err(e)
if eff_errors:
    warn(f"有效性检查 {len(eff_errors)} 个错误（见上方 ❌）")
else:
    ok(
        "有效性检查完成（0 错误，覆盖路由/成员/调度/技能索引/徽章/只读/编排协议/规模口径）"
    )

# ═══════════════════════════════════════════════════════
# 总结
# ═══════════════════════════════════════════════════════
print("\n" + "=" * 50)
if errors:
    print(f"❌ 校验失败：{len(errors)} 个错误")
    for e in errors:
        print(f"   - {e}")
    sys.exit(1)
else:
    print(f"✅ 全部校验通过！{len(warnings)} 个警告（非阻断）")
    if warnings:
        for w in warnings:
            print(f"   ⚠️  {w}")
    sys.exit(0)
