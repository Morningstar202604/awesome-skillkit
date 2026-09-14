#!/usr/bin/env python3
"""主流水线 — 三层瀑布式意图识别完整流程"""
import json
import sys
import os
import argparse
from datetime import datetime
from typing import Dict, Any, Optional

sys.path.insert(0, os.path.dirname(__file__))

from l1_matcher import match, match_all
from llm_client import call_l2, call_l3
from plan_renderer import render_markdown, render_json


def detect_project_root() -> str:
    """探测项目根目录"""
    for dir in [".", "..", "../.."]:
        for f in ["package.json", "pyproject.toml", "go.mod", "Cargo.toml", "pom.xml", "build.gradle", "requirements.txt"]:
            if os.path.exists(os.path.join(dir, f)):
                return os.path.abspath(dir)
    return os.getcwd()


def detect_tech_stack(root: str) -> str:
    """探测技术栈"""
    stacks = []
    if os.path.exists(os.path.join(root, "package.json")):
        stacks.append("javascript/typescript")
    if os.path.exists(os.path.join(root, "pyproject.toml")) or os.path.exists(os.path.join(root, "requirements.txt")):
        stacks.append("python")
    if os.path.exists(os.path.join(root, "go.mod")):
        stacks.append("go")
    if os.path.exists(os.path.join(root, "Cargo.toml")):
        stacks.append("rust")
    return ", ".join(stacks) if stacks else "unknown"


def normalize_input(raw_input: str, last_intent: Optional[Dict[str, Any]] = None) -> str:
    """输入规范化（简化版：指代消解 + 省略补全 + 术语标准化）"""
    text = raw_input.strip()
    
    # 指代消解
    if last_intent and last_intent.get("slots"):
        for pronoun in ["它", "这个", "那个", "上一个", "刚才"]:
            if pronoun in text:
                target = last_intent["slots"].get("target", "")
                if target:
                    text = text.replace(pronoun, target)
    
    # 省略补全
    if text in ["帮我写", "帮我做", "实现一下"]:
        text = text + "代码"
    
    # 术语标准化
    term_map = {
        "后端": "backend", "server": "backend", "API": "backend", "api": "backend",
        "前端": "frontend", "client": "frontend", "UI": "frontend",
        "数据库": "database", "DB": "database", "持久化": "database",
    }
    for cn, en in term_map.items():
        text = text.replace(cn, en)
    
    return text


def _session_path(session_id: str) -> str:
    """会话文件的规范位置。

    必须与 session_manager.SESSION_DIR 保持一致（~/.code_intent_planner/sessions）。
    早期版本直接写 f"_session_{session_id}.json"，即落在调用者的当前工作目录——
    用户把技能放进项目里跑一次，项目根就多出一堆 _session_*.json 垃圾文件。
    可用 SKILLKIT_SESSION_DIR 覆盖（测试用），否则用用户主目录下的固定位置。
    """
    base = os.environ.get("SKILLKIT_SESSION_DIR")
    if base:
        d = base
    else:
        d = os.path.join(os.path.expanduser("~"), ".code_intent_planner", "sessions")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, f"_session_{session_id}.json")


def load_session(session_id: str) -> Optional[Dict[str, Any]]:
    """加载 session 状态"""
    path = _session_path(session_id)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return None


def save_session(session_id: str, state: Dict[str, Any]):
    """保存 session 状态"""
    path = _session_path(session_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def get_clarification_questions(l2_result: Dict[str, Any], missing_slots: list) -> list:
    """生成澄清问题"""
    slot_questions = {
        "target": "需要操作哪个模块或文件？（如：auth、user-service、payment）",
        "scope": "改动范围是？（新功能开发 / 现有功能修改 / 代码重构 / 纯配置变更）",
        "tech_stack": "目标技术栈是什么？（如：python/fastapi、node/express、go/gin）",
        "deadline": "截止时间？（今天/本周/本月/不急）",
    }
    questions = []
    for slot in missing_slots[:3]:
        if slot in slot_questions:
            questions.append(f"① {slot_questions[slot]}")
    return questions


def run_pipeline(
    raw_input: str,
    session_id: Optional[str] = None,
    project_root: Optional[str] = None,
    skip_normalization: bool = False,
    use_mock: bool = True,
) -> Dict[str, Any]:
    """运行完整流水线"""
    
    # 初始化
    if not session_id:
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if not project_root:
        project_root = detect_project_root()
    
    tech_stack = detect_tech_stack(project_root)
    session = load_session(session_id)
    last_intent = session.get("last_intent") if session else None
    
    # 步骤 0：缓存检查
    if session:
        cache_key = f"{session_id}:{last_intent.get('intent_type', '')}:{hash(raw_input[:100])}"
        if cache_key in session.get("cache", {}):
            print(f"[Cache Hit] 返回缓存结果", file=sys.stderr)
            return session["cache"][cache_key]
    
    # 步骤 1：输入规范化
    normalized = raw_input if skip_normalization else normalize_input(raw_input, last_intent)
    
    # 步骤 2：L1 规则层
    l1_result = match(normalized)
    
    # 初始化变量
    intent_type = None
    confidence = 0.0
    source_layer = "L1"
    l2_result = {}
    l3_result = {}
    subtype = None
    
    # 三层瀑布
    if l1_result["matched"] and l1_result["confidence"] >= 0.85:
        # L1 直接命中
        intent_type = l1_result["intent_type"]
        confidence = l1_result["confidence"]
        source_layer = "L1"
        subtype = l1_result.get("subtype")
        l2_result = {"slots": {}, "description": normalized}
    else:
        # L1 未命中，进入 L2
        if use_mock:
            os.environ["USE_MOCK_LLM"] = "true"
        
        l2_result = call_l2(normalized, tech_stack)
        
        if "error" in l2_result:
            return {"error": f"L2 失败: {l2_result['error']}", "session_id": session_id}
        
        confidence = l2_result.get("confidence", 0)
        intent_type = l2_result.get("intent_type")
        source_layer = "L2"
        
        if confidence >= 0.85:
            pass  # L2 直接接受
        elif confidence >= 0.60:
            # 澄清协议
            missing = [k for k, v in l2_result.get("slots", {}).items() if not v]
            questions = get_clarification_questions(l2_result, missing)
            return {
                "status": "clarification_needed",
                "questions": get_clarification_questions(l2_result, missing),
                "partial_intent": l2_result,
                "session_id": session_id,
            }
        else:
            # 置信度 < 0.60，进入 L3
            l3_result = call_l3(
                raw_input=raw_input,
                normalized_text=normalized,
                tech_stack=tech_stack,
                project_snippet="",
                intent_type=l2_result.get("intent_type", "implement"),
                slots=l2_result.get("slots", {}),
                last_intent=last_intent
            )
            
            if "error" in l3_result:
                return {"error": f"L3 失败: {l3_result['error']}", "session_id": session_id}
            
            # 合并 L3 结果
            intent_type = l3_result.get("intent_type")
            confidence = l3_result.get("confidence", 0)
            source_layer = "L3"
            l2_result.update(l3_result)
    
    # 槽位合并与证据分级
    slots = l2_result.get("slots", {})
    if source_layer == "L1":
        # L1 直接命中，无槽位信息
        slots = {"target": "", "scope": "", "tech_stack": detect_tech_stack(detect_project_root())}
    
    slot_list = []
    for name, value in slots.items():
        if not value:
            continue
        evidence = "provisional"
        if name in ["target", "tech_stack"] and value:
            evidence = "verified" if any(k in raw_input.lower() for k in [value.lower()]) else "provisional"
        slot_list.append({"name": name, "value": value, "evidence": evidence})
    
    # 方案建议（L1/L2 简单情况使用模板，L3 已包含）
    solution = l2_result.get("solution", "")
    if source_layer == "L1" and not solution:
        solution = get_default_solution(intent_type)
    
    # 假设
    assumptions = l2_result.get("assumptions", [])
    if source_layer == "L1" and not assumptions:
        assumptions = []
    
    # 子任务
    sub_tasks = l2_result.get("sub_tasks", [])
    critical_path = l2_result.get("critical_path", [])
    parallel_groups = l2_result.get("parallel_groups", [])
    
    # 约束
    constraints = l2_result.get("constraints", {"hard": [], "soft": []})
    
    # 构建最终结果
    result = {
        "intent_type": intent_type,
        "subtype": subtype,
        "confidence": confidence,
        "source_layer": source_layer,
        "description": l2_result.get("description", normalized) if source_layer != "L1" else normalized,
        "slots": slot_list,
        "constraints": constraints if source_layer != "L1" else {"hard": [], "soft": []},
        "sub_tasks": sub_tasks,
        "critical_path": critical_path,
        "parallel_groups": parallel_groups,
        "solution": solution,
        "assumptions": assumptions,
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
    }
    
    # 更新 session
    new_session = {
        "session_id": session_id,
        "turn": (session.get("turn", 0) + 1) if session else 1,
        "last_intent": {
            "type": intent_type,
            "slots": {s["name"]: s["value"] for s in slot_list}
        },
        "slots_history": (session.get("slots_history", []) + [slot_list]) if session else [slot_list],
        "cache": session.get("cache", {}) if session else {},
    }
    # 更新缓存
    cache_key = f"{session_id}:{intent_type}:{hash(normalized[:100])}"
    new_session["cache"][cache_key] = result
    save_session(session_id, new_session)
    
    return result


def get_default_solution(intent_type: str) -> str:
    """L1 直接命中时的默认方案"""
    solutions = {
        "implement": "先设计 schema，再实现 model/service，最后加 API",
        "fix": "先复现 → 定位 → 修复 → 回归测试",
        "refactor": "先分析影响 → 写保护测试 → 小步重构 → 验证",
        "review": "扫描安全/性能/可读性 → 生成报告",
        "test": "分析覆盖 → 补测试 → 验证",
        "optimize": "建基线 → profiling → 优化 → 回归",
        "plan": "需求澄清 → 方案设计 → 任务分解",
        "design": "需求澄清 → 方案草稿 → 选型论证 → 评审",
        "migrate": "兼容性分析 → 计划 → 试点 → 全量",
        "destructive": "风险评估 → 备份 → 确认 → 执行 → 验证",
        "test": "分析覆盖 → 补测试 → 验证",
    }
    return solutions.get(intent_type, "遵循标准开发流程")


def main():
    parser = argparse.ArgumentParser(description="Code Intent Planner — 三层瀑布式意图识别")
    parser.add_argument("input", nargs="?", help="用户输入（自然语言）")
    parser.add_argument("--session", "-s", help="Session ID")
    parser.add_argument("--project", "-p", help="项目根目录")
    parser.add_argument("--skip-normalization", action="store_true")
    parser.add_argument("--no-mock", action="store_true", help="使用真实 LLM（需配置环境变量）")
    parser.add_argument("--format", "-f", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--output", "-o", help="输出文件路径")
    
    args = parser.parse_args()
    
    if not args.input:
        parser.print_help()
        sys.exit(1)
    
    result = run_pipeline(
        raw_input=args.input,
        session_id=args.session,
        project_root=args.project,
        skip_normalization=args.skip_normalization,
        use_mock=not args.no_mock,
    )
    
    if args.format == "markdown":
        output = render_markdown(result)
    else:
        output = render_json(result)
    
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
    else:
        print(output)


if __name__ == "__main__":
    main()