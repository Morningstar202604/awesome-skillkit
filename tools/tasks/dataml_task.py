# -*- coding: utf-8 -*-
"""data-ml · 可运行程序交付物：一个真实可运行的 ML 训练+评估小工具（鸢尾花）。"""
SKILL = "ml-toolkit"
DOMAIN = "data-ml"


def run(ctx, ffmpeg):
    ctx.think(
        "data-ml-science 域挑 ml-toolkit。任务：生成一个**真实可运行**的 Python ML 程序——"
        "鸢尾花三分类：读 sklearn 内置数据集、划分训练/测试、训练逻辑回归、输出真实准确率。"
        "跑一遍验证可运行 + 准确率>0.9。边界：缺 sklearn 时给降级说明而非崩。"
    )
    import os
    code = r'''import sys
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

def main():
    X, y = load_iris(return_X_y=True)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
    m = LogisticRegression(max_iter=2000, random_state=42).fit(Xtr, ytr)
    acc = accuracy_score(yte, m.predict(Xte))
    print(f"n_train={len(Xtr)} n_test={len(Xte)} accuracy={acc:.3f}")
    return 0 if acc >= 0.9 else 1

if __name__ == "__main__":
    sys.exit(main())
'''
    p = os.path.join(ctx.d, "iris_model.py")
    ctx.write_file("iris_model.py", code, "可运行 ML 程序（鸢尾花三分类）")
    r = ctx.run("python", [p])
    if r and r.returncode == 0:
        ctx.think(f"程序运行成功: {r.stdout.strip()}")
        ctx.result("pass", "真实可运行 ML 程序，准确率达标（>0.9）")
    elif r and r.returncode == 1:
        ctx.problem(f"运行了但准确率不足: {r.stdout.strip()}")
        ctx.result("warn", "程序可运行但指标未达阈值")
    else:
        ctx.problem("缺 sklearn 或运行失败")
        ctx.better("若环境无 sklearn，可换纯 numpy 实现线性判别；当前记为缺失。")
        ctx.result("fail", "缺 sklearn 无法运行")


if __name__ == "__main__":
    from full_skill_test import Recorder, get_ffmpeg, ARTIFACTS
    import os
    os.makedirs(ARTIFACTS, exist_ok=True)
    c = Recorder(SKILL, DOMAIN)
    run(c, get_ffmpeg())
    c.dump()
