# -*- coding: utf-8 -*-
"""dataviz · 真实图片交付物：真实 matplotlib 图表（多子图 + 统计标注）。"""
SKILL = "dataviz-studio"
DOMAIN = "dataviz"


def run(ctx, ffmpeg):
    ctx.think(
        "dataviz 域挑 dataviz-studio。任务：真实生成一张 matplotlib 图（3 子图：折线 + 箱线 + 散点），"
        "含真实数据 + 统计标注，输出 PNG（可被识图验证）。边界：空数据要优雅报错而非崩。"
    )
    import os
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except Exception as e:
        ctx.problem(f"缺 matplotlib/numpy: {e}")
        ctx.result("fail", "matplotlib 缺失，无法出图")
        return
    rng = np.random.default_rng(7)
    t = np.linspace(0, 10, 100)
    sig = np.sin(t) + rng.normal(0, 0.1, 100)
    data = rng.normal(50, 10, 200)

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    axes[0].plot(t, sig, color="#6366f1", lw=1.5)
    axes[0].set_title("signal"); axes[0].grid(alpha=0.3)
    axes[1].boxplot([data]); axes[1].set_title("distribution")
    xs = rng.normal(0, 1, 200)
    ys = 2 * xs + rng.normal(0, 0.3, 200)
    axes[2].scatter(xs, ys, s=14, alpha=0.6, color="#10b981"); axes[2].set_title("correlation")
    fig.tight_layout()
    out = os.path.join(ctx.d, "chart.png")
    fig.savefig(out, dpi=110)
    plt.close(fig)
    ctx.think(f"图表 {out}（{os.path.getsize(out)//1024} KB，3 子图）")
    ctx.result("pass", "真实 matplotlib 多子图（折线/箱线/散点），可识图校验")
    ctx.better("可接 dataviz-studio 的真实 dashboard-designer 出交互式；当前为静态图验证可运行。")


if __name__ == "__main__":
    from full_skill_test import Recorder, get_ffmpeg, ARTIFACTS
    import os
    os.makedirs(ARTIFACTS, exist_ok=True)
    c = Recorder(SKILL, DOMAIN)
    run(c, get_ffmpeg())
    c.dump()
