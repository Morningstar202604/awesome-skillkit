#!/usr/bin/env python3
"""Marketing Domain Pipeline — 营销全流程编排。

独立领域，不使用编程/视频领域的 skill。链条：文案 → 战役 → 渠道变体。

用法:
  python3 marketing_pipeline.py --product "316不锈钢保温杯" --goal launch
  python3 marketing_pipeline.py --product "..." --goal single_post --dry-run
"""
import argparse
import json
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
STEPS = {
    "copy": ("product-copywriter", "选框架（FAB/PAS/AIDA）写四段文案，事实卫生自查"),
    "campaign": ("campaign-designer", "营销日历 + 渠道矩阵 + 单变量 A/B 变体对"),
    "adapt": ("channel-adapter", "按渠道约束表改写 + channel_fit_check.py 机器校验"),
}

CAMPAIGN_GOALS = {
    "launch": ["copy", "campaign", "adapt"],
    "single_post": ["copy", "adapt"],
    "restock": ["copy", "campaign", "adapt"],
}


def run_pipeline(product: str, goal: str = "launch", channels: str = None,
                 dry_run: bool = False) -> dict:
    steps = []
    out_dir = Path(f"/tmp/marketing_{datetime.now().strftime('%H%M%S')}")
    if not dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    chain = CAMPAIGN_GOALS.get(goal, CAMPAIGN_GOALS["launch"])
    for name in chain:
        skill, action = STEPS[name]
        detail = {
            "copy": f"product={product} | 框架按受众决策阶段选",
            "campaign": f"goal={goal} | 单变量 A/B，一次 ≤2 对",
            "adapt": f"channels={channels or 'xhs,douyin-spoken,moments'} | 校验后交付",
        }[name]
        steps.append({"step": name, "skill": skill, "status": "planned",
                      "action": action, "detail": detail})

    return {
        "product": product, "goal": goal, "channels": channels,
        "output_dir": str(out_dir) if not dry_run else "(dry-run)",
        "steps": steps,
        "chain_note": "工件流转：base copy → 日历+变体对 → 各渠道过检变体包；"
                      "渠道数据差时带数据回 campaign-designer 调矩阵。",
    }


def main():
    parser = argparse.ArgumentParser(description="Growth marketing pipeline")
    parser.add_argument("--product", required=True, help="商品一句话")
    parser.add_argument("--goal", default="launch",
                        choices=["launch", "single_post", "restock"])
    parser.add_argument("--channels", default=None,
                        help="逗号分隔: xhs,douyin-spoken,moments,email-subject,search-ad")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = run_pipeline(args.product, args.goal, args.channels, args.dry_run)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"# Marketing Pipeline: {args.product}")
        print(f"Goal: {args.goal} | Channels: {args.channels or '(campaign 阶段定)'}")
        print()
        for s in result["steps"]:
            print(f"  □ {s['step']} [{s['skill']}] {s['action']}")
            print(f"      {s['detail']}")
        print(f"\nOutput: {result['output_dir']}")
        print(result["chain_note"])


if __name__ == "__main__":
    main()
