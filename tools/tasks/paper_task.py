# -*- coding: utf-8 -*-
"""paper · 可运行程序交付物：真实可运行的 Python ML 模型（鸢尾花分类，可训练 + 评估 + 保存）。"""
SKILL = "ml-pipeline"
DOMAIN = "paper"


def run(ctx, ffmpeg):
    ctx.think(
        "paper 域挑 ml-pipeline（建模）。要「复杂+可运行」→ 真实写一个鸢尾花分类器："
        "加载 sklearn 数据集 → 划分 → 训练逻辑回归/随机森林 → 交叉验证 + 混淆矩阵 → 保存模型。"
        "真跑一遍，输出准确率 + 混淆矩阵。边界：缺 sklearn 给纯 numpy 降级说明。"
    )
    import os
    code = r'''
import os, sys
def main():
    try:
        from sklearn.datasets import load_iris
        from sklearn.linear_model import LogisticRegression
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import cross_val_score
        from sklearn.metrics import confusion_matrix, accuracy_score
        from sklearn.model_selection import train_test_split
        import pickle
    except ModuleNotFoundError:
        print("SKLEARN_MISSING: 需要 pip install scikit-learn")
        return 1
    X, y = load_iris(return_X_y=True)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
    best = None
    for name, model in [
        ("LogReg", LogisticRegression(max_iter=2000, random_state=42)),
        ("RF", RandomForestClassifier(n_estimators=200, random_state=42)),
    ]:
        cv = cross_val_score(model, Xtr, ytr, cv=5).mean()
        model.fit(Xtr, ytr)
        acc = accuracy_score(yte, model.predict(Xte))
        cm = confusion_matrix(yte, model.predict(Xte))
        print(f"{name}: cv5={cv:.3f} test_acc={acc:.3f} conf_matrix={cm.tolist()}")
        if best is None or cv > best[1]:
            best = (name, cv, model)
    n, cv, m = best
    spath = os.path.join(os.path.dirname(__file__), f"model_{n}.pkl")
    pickle.dump(m, open(spath, "wb"))
    print(f"BEST={n} cv={cv:.3f} saved={os.path.basename(spath)}")
    return 0
if __name__ == "__main__":
    sys.exit(main())
'''
    p = os.path.join(ctx.d, "iris_model.py")
    ctx.write_file("iris_model.py", code, "可运行 ML 模型（鸢尾花）")
    r = ctx.run("python", [p])
    if r and r.returncode == 0:
        ctx.think(f"输出:\n{r.stdout.strip()}")
        ctx.result("pass", "真实可运行 ML 模型：双模型 CV + 测试准确率 + 混淆矩阵 + 模型落盘")
        ctx.better("可接真实数据源 + 超参搜索 + SHAP 解释；当前鸢尾花足以验证可运行性。")
    elif r and "SKLEARN_MISSING" in r.stdout:
        ctx.problem("缺 scikit-learn（需 pip install）")
        ctx.better("纯 numpy 降级：手写逻辑回归（可离线），未在本轮做")
        ctx.result("warn", "sklearn 缺失，记为待补依赖")
    else:
        ctx.problem(f"运行失败: {getattr(r, 'stderr', '')[:200] if r else 'no proc'}")
        ctx.result("fail", "ML 模型运行失败")


if __name__ == "__main__":
    from full_skill_test import Recorder, get_ffmpeg, ARTIFACTS
    import os
    os.makedirs(ARTIFACTS, exist_ok=True)
    c = Recorder(SKILL, DOMAIN)
    run(c, get_ffmpeg())
    c.dump()
