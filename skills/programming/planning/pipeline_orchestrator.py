#!/usr/bin/env python3
"""Pipeline Orchestrator — 编程全流程编排器

串联所有 skill，实现从需求到代码的完整自动化流程。

用法:
  python orchestrator.py "帮我实现一个用户认证模块"
  python orchestrator.py --deep "调研 FastAPI 最佳实践"
  python orchestrator.py --plan-only "规划任务"
"""
import json
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional


# Skill 路径配置
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
SKILLS_DIR = BASE_DIR / "skills"


class PipelineStatus:
    """流水线状态"""
    
    def __init__(self):
        self.steps = []
        self.start_time = None
        self.end_time = None
        self.errors = []
        self.outputs = {}
    
    def add_step(self, name: str, status: str, details: str = ""):
        self.steps.append({
            "name": name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def set_output(self, key: str, value: Any):
        self.outputs[key] = value
    
    def add_error(self, step: str, error: str):
        self.errors.append({"step": step, "error": error})
    
    def to_dict(self) -> Dict:
        return {
            "status": "success" if not self.errors else "partial" if self.steps else "failed",
            "steps": self.steps,
            "outputs": self.outputs,
            "errors": self.errors,
            "summary": self._generate_summary()
        }
    
    def _generate_summary(self) -> str:
        completed = [s for s in self.steps if s["status"] == "success"]
        failed = [s for s in self.steps if s["status"] == "failed"]
        
        summary = f"流水线执行完成: {len(completed)} 步成功"
        if failed:
            summary += f", {len(failed)} 步失败"
        return summary


def run_web_search(topic: str) -> Dict:
    """执行网络搜索"""
    try:
        import subprocess
        search_script = SKILLS_DIR / "programming" / "planning" / "web-search" / "scripts" / "search_client.py"
        result = subprocess.run(
            [sys.executable, str(search_script), topic, "--format", "json", "--no-cache"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return {"status": "success", "data": data}
        else:
            return {"status": "error", "error": result.stderr}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def run_deep_research(topic: str, max_rounds: int = 3) -> Dict:
    """执行深度调研"""
    try:
        import subprocess
        research_script = SKILLS_DIR / "programming" / "planning" / "deep-research" / "scripts" / "research_agent.py"
        result = subprocess.run(
            [sys.executable, str(research_script), topic, "--rounds", str(max_rounds), "--format", "json", "--no-cache"],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return {"status": "success", "data": data}
        else:
            return {"status": "error", "error": result.stderr}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def run_intent_planner(raw_input: str, context: Dict = None) -> Dict:
    """执行意图规划"""
    try:
        import subprocess
        planner_script = SKILLS_DIR / "programming" / "planning" / "code-intent-planner" / "scripts" / "pipeline.py"
        result = subprocess.run(
            [sys.executable, str(planner_script), raw_input, "--format", "json", "--no-mock"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return {"status": "success", "data": data}
        else:
            return {"status": "error", "error": result.stderr}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def run_code_generator(plan: Dict, project_root: str = None) -> Dict:
    """执行代码生成"""
    try:
        import subprocess
        import tempfile
        gen_script = SKILLS_DIR / "programming" / "planning" / "code-generator" / "scripts" / "code_generator.py"
        
        # 使用临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(plan, f, ensure_ascii=False)
            plan_file = f.name
        
        try:
            result = subprocess.run(
                [sys.executable, str(gen_script), "--plan", plan_file, "--format", "json", "--dry-run"],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return {"status": "success", "data": data}
            else:
                return {"status": "error", "error": result.stderr}
        finally:
            try:
                os.remove(plan_file)
            except:
                pass
    except Exception as e:
        return {"status": "error", "error": str(e)}


def run_tdd_guide(source_files: List[str]) -> Dict:
    """执行测试生成"""
    try:
        sys.path.insert(0, str(SKILLS_DIR / "programming" / "code-quality" / "tdd-guide" / "scripts"))
        # TDD guide 需要实际代码文件，这里返回占位
        return {
            "status": "success",
            "data": {
                "message": "请提供实际代码文件路径以生成测试",
                "example": "python scripts/test_generator.py --input src/auth/service.py --framework pytest"
            }
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def run_full_pipeline(user_input: str, project_root: str = None, dry_run: bool = False) -> Dict:
    """
    完整流水线执行
    
    流程:
    1. 意图识别 (code-intent-planner)
    2. 任务规划
    3. 代码生成 (code-generator)
    4. 测试生成 (tdd-guide)
    """
    status = PipelineStatus()
    status.start_time = datetime.now()
    
    # Step 1: 意图识别
    status.add_step("intent_recognition", "running", "分析用户需求...")
    if dry_run:
        status.steps[-1]["status"] = "planned"
        status.add_step("task_planning", "planned", "生成任务计划...")
        status.add_step("code_generation", "planned", "生成代码文件...")
        status.add_step("test_generation", "planned", "测试生成占位")
        status.end_time = datetime.now()
        return status.to_dict()

    intent_result = run_intent_planner(user_input)
    
    if intent_result["status"] == "error":
        status.add_step("intent_recognition", "failed", intent_result["error"])
        status.end_time = datetime.now()
        return status.to_dict()
    
    intent_data = intent_result["data"]
    status.set_output("intent", intent_data)
    status.add_step("intent_recognition", "success", f"识别为 {intent_data.get('intent_type')}")
    
    # Step 2: 任务规划 (从意图数据提取)
    status.add_step("task_planning", "running", "生成任务计划...")
    plan = {
        "intent_type": intent_data.get("intent_type"),
        "sub_tasks": intent_data.get("sub_tasks", []),
        "critical_path": intent_data.get("critical_path", []),
        "solution": intent_data.get("solution", ""),
        "slots": intent_data.get("slots", []),
    }
    status.set_output("plan", plan)
    status.add_step("task_planning", "success", f"生成 {len(plan.get('sub_tasks', []))} 个任务")
    
    # Step 3: 代码生成
    status.add_step("code_generation", "running", "生成代码文件...")
    code_result = run_code_generator(plan, project_root)
    
    if code_result["status"] == "error":
        status.add_step("code_generation", "failed", code_result["error"])
    else:
        status.set_output("code", code_result["data"])
        status.add_step("code_generation", "success", f"生成 {len(code_result['data'].get('files', {}))} 个文件")
    
    # Step 4: 测试生成
    status.add_step("test_generation", "pending", "等待代码生成完成后执行")
    
    status.end_time = datetime.now()
    return status.to_dict()


def run_research_pipeline(topic: str) -> Dict:
    """
    调研流水线
    
    流程:
    1. 网络搜索
    2. 深度调研
    3. 报告生成
    """
    status = PipelineStatus()
    status.start_time = datetime.now()
    
    # Step 1: 基础搜索
    status.add_step("web_search", "running", f"搜索: {topic}")
    search_result = run_web_search(topic)
    
    if search_result["status"] == "error":
        status.add_step("web_search", "failed", search_result["error"])
    else:
        status.set_output("search", search_result["data"])
        status.add_step("web_search", "success", f"找到 {search_result['data'].get('total_results', 0)} 条结果")
    
    # Step 2: 深度调研
    status.add_step("deep_research", "running", "执行深度调研...")
    research_result = run_deep_research(topic)
    
    if research_result["status"] == "error":
        status.add_step("deep_research", "failed", research_result["error"])
    else:
        status.set_output("research", research_result["data"])
        status.add_step("deep_research", "success", f"调研完成，{research_result['data'].get('total_results', 0)} 条信源")
    
    status.end_time = datetime.now()
    return status.to_dict()


def main():
    parser = argparse.ArgumentParser(description="Pipeline Orchestrator — 编程全流程编排器")
    parser.add_argument("input", nargs="?", help="用户输入（需求或主题）")
    parser.add_argument("--mode", "-m", choices=["code", "research", "plan"], default="code",
                       help="执行模式: code(代码生成), research(调研), plan(仅规划)")
    parser.add_argument("--project", "-p", help="项目根目录")
    parser.add_argument("--output", "-o", help="输出文件")
    parser.add_argument("--json", "-j", action="store_true", help="JSON 输出")
    parser.add_argument("--dry-run", action="store_true",
                        help="只规划不执行（不调用子技能脚本）")
    
    args = parser.parse_args()
    
    if not args.input:
        parser.print_help()
        sys.exit(1)
    
    # 执行流水线
    if args.mode == "research":
        result = run_research_pipeline(args.input)
    elif args.mode == "plan":
        result = run_intent_planner(args.input)
        result = {"status": "success", "data": result}
    else:
        result = run_full_pipeline(args.input, args.project, dry_run=args.dry_run)
    
    # 输出
    if args.json:
        output = json.dumps(result, ensure_ascii=False, indent=2)
    else:
        # Markdown 格式
        lines = [
            "# Pipeline 执行报告",
            "",
            f"**输入：** {args.input}",
            f"**模式：** {args.mode}",
            f"**状态：** {result.get('status', 'unknown')}",
            "",
            "---",
            "",
            "## 执行步骤",
            "",
        ]
        
        for step in result.get("steps", []):
            icon = {"success": "✓", "failed": "✗", "running": "⟳", "pending": "○"}.get(step["status"], "?")
            lines.append(f"- {icon} **{step['name']}**: {step.get('details', '')}")
        
        if result.get("errors"):
            lines.append("")
            lines.append("## 错误")
            for err in result["errors"]:
                lines.append(f"- ✗ {err['step']}: {err['error']}")
        
        output = "\n".join(lines)
    
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"报告已保存到: {args.output}", file=sys.stderr)
    else:
        print(output)
    
    # 失败时向调用方传播非零退出码
    has_errors = bool(result.get("errors")) or result.get("status") == "error"
    sys.exit(1 if has_errors else 0)


if __name__ == "__main__":
    main()
