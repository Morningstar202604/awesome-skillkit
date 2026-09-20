# -*- coding: utf-8 -*-
"""education · 可运行程序 + 成文交付物：真实可运行的「间隔复习」学习调度器 + 课程大纲。"""
SKILL = "course-designer"
DOMAIN = "education"


def run(ctx, ffmpeg):
    ctx.think(
        "education 域挑 course-designer/exercise-generator。任务：生成一个**真实可运行**的"
        "间隔复习调度器（按 Ebbinghaus 曲线算下次复习日）+ 一份成文课程大纲。"
        "可运行验证：import 函数、喂 3 天记忆数据，断言复习间隔单调递增。边界：负天数拒绝。"
    )
    import os
    tool = os.path.join(ctx.d, "spaced_repetition.py")
    ctx.write_file("spaced_repetition.py", r'''
def next_review(day, last_rating="good"):
    # 简化 Ebbinghaus：基础间隔 [1,2,4,7,14,30]，按记忆轮次递增
    base = [1, 2, 4, 7, 14, 30, 60]
    if day < 0:
        raise ValueError("day must be >= 0")
    if last_rating == "bad":
        idx = 0
    elif last_rating == "easy":
        idx = min(day + 2, len(base) - 1)
    else:
        idx = min(day + 1, len(base) - 1)
    return base[idx]

if __name__ == "__main__":
    seq = [next_review(i, "good") for i in range(6)]
    print("intervals:", seq)
    assert seq == sorted(seq), "intervals must be non-decreasing"
    print("monotonic OK", seq)
''', "可运行间隔复习调度器")
    r = ctx.run("python", [tool])
    ok = r and r.returncode == 0 and "monotonic OK" in r.stdout

    # 成文课程大纲
    outline = """# 数据结构速成课 · 大纲（Mastery-based）
## 模块 1：数组与复杂度（45min）
- 目标：能口述 O(1)/O(n) 并解释
- 练习：3 道 O(n) 判复杂度
## 模块 2：链表（40min）
- 目标：手写单链表反转
- 练习：边界（空表/单节点）
## 模块 3：递归与分治（50min）
- 目标：归并排序 O(n log n)
## 验收：3 模块练习全过 → 解锁综合题
"""
    ctx.write_file("course_outline.md", outline, "成文课程大纲")
    ctx.think(f"调度器: {r.stdout.strip() if r else 'n/a'}")
    ctx.result("pass" if ok else "warn", "可运行间隔复习器（单调性自测）+ 成文课程大纲" if ok else "调度器自测未过")
    ctx.better("可接 Anki 导出 .apkg 真实文件；当前验证调度逻辑 + 大纲成文。")


if __name__ == "__main__":
    from full_skill_test import Recorder, get_ffmpeg, ARTIFACTS
    import os
    os.makedirs(ARTIFACTS, exist_ok=True)
    c = Recorder(SKILL, DOMAIN)
    run(c, get_ffmpeg())
    c.dump()
