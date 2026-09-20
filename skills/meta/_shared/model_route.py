# -*- coding: utf-8 -*-
"""
model_route.py — 生成式技能的「离线兜底 / 真模型路由」共享 helper（第二代改进 P1）。

为何存在（自审结论）：
  第一代全量测试里 video/image/audio/music/design 用 PIL/numpy 程序化生成，
  保真度远低于 SOTA（Sora / Midjourney / Suno ...）。根因是**本机无 GPU、LLM 网关宕机**，
  不是技能逻辑错。正确做法是：技能统一走本 helper——

    - 若环境变量 <env_key> 已设且对应网关可达 → 调真模型（diffusion / TTS / musicgen ...）
    - 否则 → 调 offline_fn（PIL/numpy 确定性生成）

  离线兜底**不是缺陷，是可移植性特性**：没有算力/密钥的环境照样产出真实文件；
  有算力/密钥的环境自动升级为 SOTA 级内容。所有生成式技能照此模式接入即可。

用法：
    from model_route import offline_or_model
    out = offline_or_model(
        prompt, kind="image",
        offline_fn=my_pil_poster,            # 离线生成函数
        env_key="IMAGEN_MODEL_URL",          # 真模型网关（缺省走离线）
        ping_url="https://.../health",       # 可选可达性探测
        model_fn=my_real_diffusion,          # 可选真模型函数
    )
"""
import os
import sys
import urllib.request


def model_available(env_key: str, ping_url: str = "") -> bool:
    """env_key 已设，且（若给了 ping_url）网关可达，才判真模型可用。"""
    if not os.environ.get(env_key):
        return False
    if ping_url:
        try:
            urllib.request.urlopen(ping_url, timeout=5)
            return True
        except Exception:
            return False
    return True


def offline_or_model(prompt: str, kind: str, offline_fn, env_key: str = "SKILLKIT_MODEL_URL",
                     ping_url: str = "", model_fn=None, *args, **kwargs):
    """
    prompt    : 文本提示
    kind      : 'image'|'video'|'audio'|'music'|'design'（仅用于日志）
    offline_fn: 离线生成函数，签名 offline_fn(prompt, *args, **kwargs)
    model_fn  : 可选真模型函数，签名 model_fn(prompt, *args, **kwargs)；缺省走离线
    env_key   : 真模型网关 URL 的环境变量名
    ping_url  : 可选可达性探测 URL
    """
    if model_available(env_key, ping_url) and model_fn is not None:
        try:
            sys.stderr.write(f"[model_route] {kind}: 真模型可用，调用 {env_key}\n")
            return model_fn(prompt, *args, **kwargs)
        except Exception as e:  # 真模型失败 → 安全回退离线，保证总有交付物
            sys.stderr.write(f"[model_route] {kind}: 真模型失败({e})，回退离线\n")
    sys.stderr.write(f"[model_route] {kind}: 离线兜底（{env_key} 未设/不可达）\n")
    return offline_fn(prompt, *args, **kwargs)


# ---- 离线自测（无网络依赖，确保 helper 本身可跑）----
if __name__ == "__main__":
    def _offline(p, suffix=""):
        return f"OFFLINE[{p}{suffix}]"
    def _model(p, suffix=""):
        return f"MODEL[{p}{suffix}]"
    # 1) 无 env → 走离线
    r1 = offline_or_model("cat", "image", _offline)
    assert r1 == "OFFLINE[cat]", r1
    # 2) 设了 env 但无 model_fn → 走离线
    os.environ["SKILLKIT_MODEL_URL"] = "http://fake"
    r2 = offline_or_model("cat", "image", _offline)
    assert r2 == "OFFLINE[cat]", r2
    # 3) 设了 env 且有 model_fn → 走模型
    r3 = offline_or_model("cat", "image", _offline, model_fn=_model)
    assert r3 == "MODEL[cat]", r3
    # 4) 模型异常 → 回退离线
    def _boom(p, *a, **k):
        raise RuntimeError("boom")
    r4 = offline_or_model("cat", "image", _offline, model_fn=_boom)
    assert r4 == "OFFLINE[cat]", r4
    print("model_route self-test: 4/4 OK（离线兜底 / 真模型路由 / 异常回退 均正确）")
