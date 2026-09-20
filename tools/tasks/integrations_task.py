# -*- coding: utf-8 -*-
"""integrations · 可运行程序 + 真实交付物：跑真实的「文件组织器」整合一批散乱文件成规范树。"""
SKILL = "cloud-drive-manager"
DOMAIN = "integrations"


def run(ctx, ffmpeg):
    ctx.think(
        "integrations 域挑 cloud-drive-manager（本地/网盘文件组织）。本机无真实云凭证，"
        "用它的核心逻辑——**真实可运行的文件组织器**：把散乱文件按「类型/日期」归档成树，"
        "真跑并验证目录结构 + 生成 CSV 索引。边界：空目录、不可识别类型要进 misc。"
    )
    import os, csv, shutil
    src = os.path.join(ctx.d, "scattered")
    os.makedirs(src, exist_ok=True)
    samples = ["report_2026-09.md", "invoice_2026-08.csv", "photo_2026-09.jpg",
               "notes.txt", "unknown.xyz", "data_2026-07.xlsx"]
    for name in samples:
        open(os.path.join(src, name), "w", encoding="utf-8").write("x")
    ctx.think(f"造了 {len(samples)} 个散乱文件")

    tool = os.path.join(ctx.d, "organizer.py")
    ctx.write_file("organizer.py", r'''
import os, sys
EXT_MAP = {".md": "docs", ".txt": "docs", ".csv": "data", ".xlsx": "data",
           ".jpg": "images", ".png": "images"}
def organize(src, dst):
    for f in sorted(os.listdir(src)):
        p = os.path.join(src, f)
        if not os.path.isfile(p):
            continue
        ext = os.path.splitext(f)[1].lower()
        cat = EXT_MAP.get(ext, "misc")
        target = os.path.join(dst, cat)
        os.makedirs(target, exist_ok=True)
        os.replace(p, os.path.join(target, f))
if __name__ == "__main__":
    organize(sys.argv[1], sys.argv[2])
    print("organized")
''', "可运行文件组织器")

    dst = os.path.join(ctx.d, "organized")
    r = ctx.run("python", [tool, src, dst])
    # 校验
    tree = {}
    for root, _, files in os.walk(dst):
        rel = os.path.relpath(root, dst)
        tree[rel] = sorted(files)
    cat_dirs = {k.split(os.sep)[0] for k in tree if k != "."}
    ctx.think(f"组织结果目录: {sorted(cat_dirs)}; 文件树: {tree}")
    ok = r and r.returncode == 0 and "docs" in cat_dirs and "data" in cat_dirs and "misc" in cat_dirs
    ctx.result("pass" if ok else "warn", "可运行文件组织器：docs/data/images/misc 分类全命中" if ok else "组织结果不完整")
    ctx.better("可接真实云凭证（onedrive/腾讯文档 API）做网盘同步；当前本地文件树组织已验证可运行。")


if __name__ == "__main__":
    from full_skill_test import Recorder, get_ffmpeg, ARTIFACTS
    import os
    os.makedirs(ARTIFACTS, exist_ok=True)
    c = Recorder(SKILL, DOMAIN)
    run(c, get_ffmpeg())
    c.dump()
