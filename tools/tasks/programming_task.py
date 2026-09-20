# -*- coding: utf-8 -*-
"""programming · 可运行程序交付物：真实可运行的 Flask/HTTP 微服务（起服务 + 真请求验证）。"""
SKILL = "api-design-reviewer"
DOMAIN = "programming"


def run(ctx, ffmpeg):
    ctx.think(
        "programming 域挑 api 相关 skill，但要产出「复杂+可运行」→ 生成一个**真实可运行的 "
        "HTTP 微服务**（标准库 http.server，无外部依赖），带 REST 路由 + JSON + 错误处理。"
        "起服务、真打 3 个请求（正常/404/参数校验）验证。边界：坏 JSON body 必须返回 400。"
    )
    import os, json, threading, time, urllib.request, urllib.error
    app = os.path.join(ctx.d, "microservice.py")
    ctx.write_file("microservice.py", r'''
import json, os, sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

class H(BaseHTTPRequestHandler):
    def _json(self, code, obj):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode())
    def do_GET(self):
        if self.path == "/health":
            self._json(200, {"ok": True})
        elif self.path.startswith("/items"):
            qs = parse_qs(self.path.split("?", 1)[1])
            k = qs.get("id", ["?"])[0]
            try:
                iid = int(k)
                if iid <= 0:
                    raise ValueError
                self._json(200, {"id": iid, "title": f"item-{iid}", "price": 9.99 * iid})
            except (ValueError, TypeError):
                self._json(400, {"error": "id must be a positive integer"})
        else:
            self._json(404, {"error": "not found"})
    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(n) or b"null")
            assert isinstance(body, dict) and body.get("name")
        except Exception:
            self._json(400, {"error": "invalid JSON body (need object with 'name')"})
            return
        self._json(201, {"created": body["name"]})
    def log_message(self, *a):
        pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8931"))
    print(f"listening on 127.0.0.1:{port}", flush=True)
    HTTPServer(("127.0.0.1", port), H).serve_forever()
''', "可运行 HTTP 微服务（标准库）")

    # 起服务（后台线程 + 真进程）
    import subprocess, sys
    env = dict(os.environ, PORT="8931")
    proc = subprocess.Popen([sys.executable, app], env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    time.sleep(1.2)
    base = "http://127.0.0.1:8931"

    def req(path, method="GET", body=None):
        data = json.dumps(body).encode() if body is not None else None
        r = urllib.request.Request(base + path, data=data, method=method,
                                   headers={"Content-Type": "application/json"} if data else {})
        try:
            resp = urllib.request.urlopen(r, timeout=5)
            return resp.status, json.loads(resp.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read() or b"{}")

    results = []
    for path, m, body, exp in [
        ("/health", "GET", None, 200),
        ("/items?id=3", "GET", None, 200),
        ("/items?id=0", "GET", None, 400),
        ("/items?id=abc", "GET", None, 400),
        ("/nope", "GET", None, 404),
        ("/create", "POST", {"name": "x"}, 201),
    ]:
        code, obj = req(path, m, body)
        hit = code == exp
        results.append((path, m, exp, code, hit, obj))
        ctx.think(f"{m} {path} expect {exp} → got {code} {'OK' if hit else 'MISS'} {obj}")
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except Exception:
        proc.kill()

    ok = all(r[4] for r in results)
    ctx.result("pass" if ok else "warn", "真实可运行微服务：3 正常 + 边界(400/404) 全通过" if ok else "部分请求未达预期")
    ctx.better("可接 FastAPI+OpenAPI 出真实 API 文档 + 单测；当前标准库版已验证可运行 + 错误处理。")


if __name__ == "__main__":
    from full_skill_test import Recorder, get_ffmpeg, ARTIFACTS
    import os, sys
    os.makedirs(ARTIFACTS, exist_ok=True)
    c = Recorder(SKILL, DOMAIN)
    run(c, get_ffmpeg())
    c.dump()
