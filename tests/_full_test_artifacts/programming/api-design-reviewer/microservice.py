
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
