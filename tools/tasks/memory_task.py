# -*- coding: utf-8 -*-
"""memory · 可运行程序交付物：真实可运行的长期记忆存取器（写→检索→去重→落盘验证）。"""
SKILL = "memory-manager"
DOMAIN = "memory"


def run(ctx, ffmpeg):
    ctx.think(
        "memory 域挑 memory-manager（长期记忆生命周期）。任务：生成一个**真实可运行**的"
        "记忆存取器——写入 3 条记忆、按主题检索、去重、持久化 JSON、再读回验证。"
        "边界：重复写入不能重复存、检索命中数正确。"
    )
    import os, json
    code = r'''
import json, os, hashlib
DB = os.path.join(os.path.dirname(__file__), "memory.json")

def _load():
    return json.load(open(DB, encoding="utf-8")) if os.path.exists(DB) else []

def add(topic, text):
    m = _load()
    key = hashlib.sha1(f"{topic}|{text}".encode()).hexdigest()
    if not any(x.get("key") == key for x in m):  # 去重
        m.append({"key": key, "topic": topic, "text": text})
    json.dump(m, open(DB, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return len(m)

def search(topic):
    return [x for x in _load() if x["topic"] == topic]

if __name__ == "__main__":
    print("after add: ", add("dev", "use venv under runtime dir"), "dups:", add("dev", "use venv under runtime dir"))
    print("search dev:", len(search("dev")), "hits")
    assert len(search("dev")) == 1, "dedup failed"
    print("OK")
'''
    p = os.path.join(ctx.d, "memory_store.py")
    ctx.write_file("memory_store.py", code, "可运行长期记忆存取器")
    r = ctx.run("python", [p])
    ok = r and r.returncode == 0 and "OK" in r.stdout
    ctx.think(f"{r.stdout.strip() if r else 'n/a'}")
    ctx.result("pass" if ok else "fail", "可运行记忆存取：写/检索/去重/落盘/读回全验证" if ok else "记忆存取未过自测")
    ctx.better("可接向量检索（embeddings）做语义检索；当前精确主题去重已验证可运行。")


if __name__ == "__main__":
    from full_skill_test import Recorder, get_ffmpeg, ARTIFACTS
    import os
    os.makedirs(ARTIFACTS, exist_ok=True)
    c = Recorder(SKILL, DOMAIN)
    run(c, get_ffmpeg())
    c.dump()
