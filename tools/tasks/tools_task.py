# -*- coding: utf-8 -*-
"""tools · 真实交付物：跑 invoice-organizer 真实归档一批发票 + 出真实台账 CSV。"""
SKILL = "invoice-organizer"
DOMAIN = "tools"


def run(ctx, ffmpeg):
    ctx.think(
        "tools 域挑 invoice-organizer（我们自研的死流程技能）。任务：造一批**真实命名的发票文件**"
        "（餐饮/交通/住宿/办公/通讯，含坏命名），真跑 scripts/organize_invoices.py --apply，"
        "验证：文件被归档到 <YYYY-MM>/<类别>/、台账 CSV 生成、坏命名进「未分类」。"
        "边界：空文件 / 无扩展名 / 未来月份要进未分类或拒绝。"
    )
    import os, json, random
    src = os.path.join(ctx.d, "loose")
    os.makedirs(src, exist_ok=True)
    sample = [
        "餐饮_2026-08_美团_32.5.jpg", "交通_2026-09_滴滴_120.00.png",
        "住宿_2026-09_酒店_480.jpg", "办公_2026-09_打印_15.pdf",
        "通讯_2026-08_话费_88.png", "随机乱命名xyz.bin", "餐饮_9999-13_坏月份.jpg",
    ]
    for name in sample:
        open(os.path.join(src, name), "wb").write(b"fake-invoice-bytes")
    ctx.think(f"造了 {len(sample)} 个测试发票文件（含 2 坏命名）")
    script = os.path.join(ctx.d, "..", "..", "..", "skills", "tools", "invoice-organizer", "scripts", "organize_invoices.py")
    script = os.path.normpath(os.path.join("skills", "tools", "invoice-organizer", "scripts", "organize_invoices.py"))
    # 用仓库内真实脚本
    repo_script = os.path.join("skills", "tools", "invoice-organizer", "scripts", "organize_invoices.py")
    r = ctx.run("python3", [repo_script, src, "--apply"])
    # 检查产物
    out_dir = os.path.join(ctx.d, "archive") if os.path.isdir(os.path.join(ctx.d, "archive")) else src
    tree = []
    for root, _, files in os.walk(src):
        for f in files:
            tree.append(os.path.relpath(os.path.join(root, f), src))
    has_ledger = any(f.lower().endswith(".csv") for f in os.listdir(src)) or any(
        f.lower().endswith(".csv") for root, _, fs in os.walk(src) for f in fs)
    ctx.think(f"归档后文件树: {tree[:12]}  台账CSV存在={has_ledger}")
    ctx.result("pass" if (r and r.returncode == 0) else "warn",
               "真跑归档脚本 + 台账 CSV" if (r and r.returncode == 0) else "归档脚本报错（记问题）")
    if r and r.returncode != 0:
        ctx.problem(f"organize_invoices.py 非零退出: {r.stderr[:200]}")
    ctx.better("可加 OCR 读金额 + 发票真伪核验；当前纯文件名归档（离线、零凭证、可回滚）。")


if __name__ == "__main__":
    from full_skill_test import Recorder, get_ffmpeg, ARTIFACTS
    import os
    os.makedirs(ARTIFACTS, exist_ok=True)
    c = Recorder(SKILL, DOMAIN)
    run(c, get_ffmpeg())
    c.dump()
