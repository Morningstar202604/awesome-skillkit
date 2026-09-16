#!/usr/bin/env python3
"""with_server.py — start a server, wait for readiness, run a test command, always clean up.

Usage:
    python3 with_server.py --cmd "npm run dev" --port 3000 -- <test command...>
    python3 with_server.py --cmd "python3 -m app" --port 8080 --ready-path /health \
        --timeout 90 -- curl -sf http://127.0.0.1:8080/

Lifecycle:
    1. spawn the server command in the background (own process group)
    2. poll the port with socket connect retries until it accepts (or --timeout)
       when --ready-path is given, additionally require an HTTP 200 on that path
    3. run the test command and capture its exit code
    4. in a finally block, terminate the whole server process tree (SIGTERM,
       escalating to SIGKILL) — a crashing test never leaves an orphan server

Exit code: that of the test command; 1 = server never became ready;
           2 = bad usage; 130 = interrupted. Server output is buffered and
           dumped to stderr only when the server dies early or fails cleanup.
"""

import argparse
import os
import signal
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request


def log(msg: str) -> None:
    print(f"[with_server] {msg}", file=sys.stderr, flush=True)


def port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def path_ok(host: str, port: int, path: str) -> bool:
    url = f"http://{host}:{port}{path}"
    try:
        with urllib.request.urlopen(url, timeout=2) as resp:
            return resp.status == 200
    except (urllib.error.URLError, urllib.error.HTTPError, OSError):
        return False


def kill_tree(proc: subprocess.Popen, out_path: str) -> None:
    if proc.poll() is not None:
        return
    try:
        if hasattr(os, "killpg"):
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        else:
            proc.terminate()
        proc.wait(timeout=5)
        log("server process tree terminated (SIGTERM)")
    except (ProcessLookupError, subprocess.TimeoutExpired):
        try:
            if hasattr(os, "killpg"):
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            else:
                proc.kill()
            log("server killed with SIGKILL after grace period")
        except ProcessLookupError:
            pass
    finally:
        try:
            with open(out_path, encoding="utf-8", errors="replace") as f:
                tail = f.read()[-2000:]
            if tail.strip():
                log("--- server output tail ---\n" + tail)
        except OSError:
            pass


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--cmd", required=True, help="server start command (run via shell)")
    ap.add_argument("--port", required=True, type=int, help="port to poll for readiness")
    ap.add_argument("--host", default="127.0.0.1", help="host to poll (default 127.0.0.1)")
    ap.add_argument("--ready-path", default=None,
                    help="optional HTTP path; readiness requires GET 200 on it")
    ap.add_argument("--timeout", type=int, default=60,
                    help="readiness timeout in seconds (default 60)")
    ap.add_argument("test_cmd", nargs=argparse.REMAINDER,
                    help="test command to run after '--'")
    args = ap.parse_args()

    if not args.test_cmd:
        ap.error("no test command given after '--'")
    if args.test_cmd[0] == "--":  # argparse REMAINDER keeps the separator
        args.test_cmd = args.test_cmd[1:]
    if not args.test_cmd:
        ap.error("no test command given after '--'")
    test_cmd = " ".join(args.test_cmd)

    out_path = tempfile.mktemp(prefix="with_server_out_")
    out_file = open(out_path, "w", encoding="utf-8")
    try:
        log(f"starting server: {args.cmd}")
        server = subprocess.Popen(
            args.cmd, shell=True, stdout=out_file, stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    except Exception as exc:  # spawn failure: nothing to clean up
        out_file.close()
        log(f"failed to spawn server: {exc}")
        return 1

    def _bail(*_a):
        sys.exit(130)

    signal.signal(signal.SIGTERM, _bail)
    signal.signal(signal.SIGINT, _bail)

    try:
        deadline = time.monotonic() + args.timeout
        log(f"waiting for {args.host}:{args.port} (timeout {args.timeout}s)")
        while time.monotonic() < deadline:
            if server.poll() is not None:
                log(f"server exited early with code {server.returncode}")
                return 1
            if port_open(args.host, args.port):
                if args.ready_path and not path_ok(args.host, args.port, args.ready_path):
                    time.sleep(0.5)
                    continue
                log("server is ready")
                break
            time.sleep(0.5)
        else:
            log(f"timeout: {args.host}:{args.port} not ready within {args.timeout}s")
            return 1

        log(f"running test: {test_cmd}")
        code = subprocess.call(test_cmd, shell=True)
        log(f"test exit code: {code}")
        return code
    finally:
        kill_tree(server, out_path)
        out_file.close()
        try:
            os.unlink(out_path)
        except OSError:
            pass


if __name__ == "__main__":
    sys.exit(main())
