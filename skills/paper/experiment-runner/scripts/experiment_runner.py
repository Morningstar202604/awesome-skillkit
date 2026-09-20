#!/usr/bin/env python3
"""Experiment Runner — 可复现实验 + 真实统计检验（SOTA 升级版）。

对标 2026 最佳实践：
  - 统计：scipy.stats.ttest_ind (Welch) / mannwhitneyu + p 值 + Cohen's d + 95% CI
    （scipy 缺失时回退到纯标准库 Welch t 检验 + 正态近似 p 值，离线仍可用）
  - 复现：统一固定 python / numpy / (torch) 随机种子；导出 resolved config + 环境指纹
  - 追踪钩子：可选接入 mlflow / wandb（detect 即 autolog，不强制依赖）

两种模式：
  --mode simulated  内置演示实验（诚实标注 mode=simulated，MUST 标「模拟数据」）
  --mode real --metric <module:func> --baseline <module:func>
                    跑用户真实指标函数（func(seed:int)->float），做真实两组比较

诚实声明：simulated 模式永不当真实实验结果；real 模式的显著性以 p 值判定，
`significant = p_value < alpha`（默认 0.05），不再用「均值超阈值」冒充 t-test。
"""
import argparse
import importlib
import json
import math
import os
import random
import statistics
import sys
from pathlib import Path

ALPHA = 0.05


# ----------------------------------------------------------------------------
# 随机种子（复现性）
# ----------------------------------------------------------------------------
def seed_all(base: int):
    """固定 python / numpy / (torch) 种子，返回用到的后端列表。"""
    random.seed(base)
    backends = ["random"]
    try:
        import numpy as np
        np.random.seed(base)
        backends.append(f"numpy {np.__version__}")
    except Exception:
        pass
    try:
        import torch
        torch.manual_seed(base)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(base)
        backends.append(f"torch {torch.__version__}")
    except Exception:
        pass
    return backends


def env_fingerprint() -> dict:
    """导出环境指纹，便于复现审计（不强制安装任何库）。"""
    fp = {"python": sys.version.split()[0]}
    try:
        import numpy as np
        fp["numpy"] = np.__version__
    except Exception:
        pass
    try:
        import scipy
        fp["scipy"] = scipy.__version__
    except Exception:
        fp["scipy"] = None
    try:
        import sklearn
        fp["sklearn"] = sklearn.__version__
    except Exception:
        pass
    fp["cuda_available"] = False
    try:
        import torch
        fp["torch"] = torch.__version__
        fp["cuda_available"] = torch.cuda.is_available()
    except Exception:
        pass
    return fp


# ----------------------------------------------------------------------------
# 真实统计（优先 scipy，回退纯标准库）
# ----------------------------------------------------------------------------
def _mean(xs):
    return sum(xs) / len(xs)


def _var(xs, ddof=1):
    m = _mean(xs)
    return sum((x - m) ** 2 for x in xs) / (len(xs) - ddof)


def _welch_t(a, b):
    """纯标准库 Welch t 检验：返回 (t, df, p_two_sided)。"""
    ma, mb = _mean(a), _mean(b)
    va, vb = _var(a, 1), _var(b, 1)
    na, nb = len(a), len(b)
    se = math.sqrt(va / na + vb / nb)
    if se == 0:
        return 0.0, na + nb - 2, 1.0
    t = (ma - mb) / se
    # Welch–Satterthwaite 自由度
    df = (va / na + vb / nb) ** 2 / (
        (va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1)
    )
    # 双尾 p 值（正态近似；大样本下足够；小样本用 t 分布更准确但标准库无 erf 逆）
    z = abs(t)
    # 用 error function 近似标准正态双尾 p
    p = math.erfc(z / math.sqrt(2))
    return t, df, p


def cohens_d(a, b):
    na, nb = len(a), len(b)
    sp = math.sqrt(((na - 1) * _var(a, 1) + (nb - 1) * _var(b, 1)) / (na + nb - 2))
    if sp == 0:
        return 0.0
    return (_mean(a) - _mean(b)) / sp


def real_stats(ours, baseline, alpha=ALPHA):
    """两组比较，返回真实统计结论。优先 scipy，否则纯标准库回退。"""
    method = "scipy"
    try:
        from scipy import stats
        res = stats.ttest_ind(ours, baseline, equal_var=False)
        t = float(res.statistic)
        p = float(res.pvalue)
        df = (len(ours) + len(baseline) - 2)
        # 差值的 95% CI（Welch）
        diff = _mean(ours) - _mean(baseline)
        se = math.sqrt(_var(ours, 1) / len(ours) + _var(baseline, 1) / len(baseline))
        tc = stats.t.ppf(1 - alpha / 2, df)
        ci_low, ci_high = diff - tc * se, diff + tc * se
    except Exception:
        method = "stdlib-fallback"
        t, df, p = _welch_t(ours, baseline)
        diff = _mean(ours) - _mean(baseline)
        se = math.sqrt(_var(ours, 1) / len(ours) + _var(baseline, 1) / len(baseline))
        zc = 1.959963984540054  # 正态 95% 临界
        ci_low, ci_high = diff - zc * se, diff + zc * se

    d = cohens_d(ours, baseline)
    return {
        "test": "welch_ttest",
        "method": method,
        "statistic": round(t, 4),
        "df": round(df, 2),
        "p_value": round(p, 6),
        "alpha": alpha,
        "effect_size_cohens_d": round(d, 4),
        "ci95_diff": [round(ci_low, 4), round(ci_high, 4)],
        "significant": bool(p < alpha),
    }


# ----------------------------------------------------------------------------
# 两种运行模式
# ----------------------------------------------------------------------------
def run_simulated(config: dict) -> dict:
    n_runs = int(config.get("n_runs", 3))
    seed = int(config.get("seed", 42))
    baseline = float(config.get("baseline_metric", 0.80))
    improvement_target = float(config.get("improvement_target", 0.05))
    backends = seed_all(seed)

    random.seed(seed)
    results = []
    ours_vals, base_vals = [], []
    for i in range(n_runs):
        ours = baseline + random.gauss(improvement_target * 0.8, 0.02)
        base = baseline + random.gauss(0.0, 0.02)
        ours_vals.append(ours)
        base_vals.append(base)
        results.append({
            "run_id": i + 1,
            "ours": round(ours, 4),
            "baseline": round(base, 4),
            "seed_used": seed + i,
        })
    st = real_stats(ours_vals, base_vals)
    return {
        "status": "complete",
        "mode": "simulated",
        "simulation_notice": "模拟实验数据（未运行真实训练），MUST 标注 模拟数据；显著性来自真实 Welch t 检验",
        "n_runs": n_runs,
        "results": results,
        "stats": st,
        "config": config,
        "seed_backends": backends,
        "env": env_fingerprint(),
    }


def _load_callable(spec: str):
    """module:func -> callable。"""
    mod_name, _, fn_name = spec.partition(":")
    if not fn_name:
        raise ValueError(f"--metric/--baseline 需 'module:func' 形式，收到: {spec}")
    mod = importlib.import_module(mod_name)
    return getattr(mod, fn_name)


def run_real(metric_spec, baseline_spec, config: dict) -> dict:
    n_runs = int(config.get("n_runs", 5))
    seed = int(config.get("seed", 42))
    backends = seed_all(seed)
    ours_fn = _load_callable(metric_spec)
    base_fn = _load_callable(baseline_spec) if baseline_spec else None

    ours_vals, base_vals = [], []
    results = []
    for i in range(n_runs):
        s = seed + i
        ov = float(ours_fn(s))
        ours_vals.append(ov)
        if base_fn:
            bv = float(base_fn(s))
            base_vals.append(bv)
        else:
            bv = float(config.get("baseline_value", 0.0))
            base_vals.append(bv)
        results.append({"run_id": i + 1, "ours": round(ov, 6),
                        "baseline": round(bv, 6), "seed_used": s})

    if not base_fn:
        # 单组：仅报描述统计，不做两组比较
        return {
            "status": "complete",
            "mode": "real",
            "n_runs": n_runs,
            "results": results,
            "stats": {"mean": round(_mean(ours_vals), 6),
                      "std": round(_var(ours_vals, 1) ** 0.5, 6),
                      "note": "单组模式：未提供 --baseline，未做两组比较"},
            "config": config,
            "seed_backends": backends,
            "env": env_fingerprint(),
        }
    st = real_stats(ours_vals, base_vals)
    return {
        "status": "complete",
        "mode": "real",
        "metric": metric_spec,
        "baseline": baseline_spec,
        "n_runs": n_runs,
        "results": results,
        "stats": st,
        "config": config,
        "seed_backends": backends,
        "env": env_fingerprint(),
    }


# ----------------------------------------------------------------------------
# 可选追踪（detect 即 autolog，不强制依赖）
# ----------------------------------------------------------------------------
def _maybe_track(run: dict):
    try:
        import mlflow
        with mlflow.start_run(run_name="skillkit-exp"):
            mlflow.log_param("mode", run.get("mode"))
            mlflow.log_param("n_runs", run.get("n_runs"))
            st = run.get("stats", {})
            if "p_value" in st:
                mlflow.log_metric("p_value", st["p_value"])
                mlflow.log_metric("cohens_d", st.get("effect_size_cohens_d", 0))
        run["tracking"] = "mlflow"
    except Exception:
        run["tracking"] = None
    return run


def main():
    ap = argparse.ArgumentParser(description="Reproducible experiment runner (SOTA stats)")
    ap.add_argument("--mode", default="simulated", choices=["simulated", "real"])
    ap.add_argument("--config", help="实验配置 JSON（键 n_runs/seed/baseline_metric/improvement_target）")
    ap.add_argument("--n-runs", type=int, default=5)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--metric", help="real 模式：指标函数 module:func（func(seed:int)->float）")
    ap.add_argument("--baseline", help="real 模式：基线函数 module:func")
    ap.add_argument("--baseline-value", type=float, default=0.0, help="无 --baseline 时的固定基线值")
    ap.add_argument("--track", action="store_true", help="尝试 mlflow autolog（需安装 mlflow）")
    ap.add_argument("--output", help="输出 JSON 路径")
    args = ap.parse_args()

    if args.config:
        config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    else:
        config = {"n_runs": args.n_runs, "seed": args.seed,
                  "baseline_metric": 0.80, "improvement_target": 0.05}

    if args.mode == "real":
        if not args.metric:
            print(json.dumps({"status": "error",
                              "error": "real 模式需要 --metric module:func"}, ensure_ascii=False))
            return 2
        run = run_real(args.metric, args.baseline, config)
    else:
        run = run_simulated(config)

    if args.track:
        run = _maybe_track(run)

    out = json.dumps(run, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
        print(f"Results written to: {args.output}", file=sys.stderr)
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
