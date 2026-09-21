"""Smoke tests per SKILL-STANDARD-v2 G7: CLI contract stays runnable.

--help exercises argparse wiring without touching the network or filesystem.
"""
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "seo_optimizer.py"


def test_help_contract():
    r = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, r.stderr
    assert "usage" in (r.stdout + r.stderr).lower()


SP = Path(__file__).resolve().parent  # noqa: E305
import json  # noqa: E402
import importlib.util  # noqa: E402

# --- 强测试：路径被当正文分析的老 bug ---

def test_nonexistent_path_like_content_rejected():
    """--content 给了不存在的 .md 路径必须 rc=2，不许拿路径字符串算假报告。"""
    import subprocess, sys, json
    r = subprocess.run([sys.executable, str(SP / "seo_optimizer.py"),
                        "--title", "t", "--content", "article.md"],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 2, r
    o = json.loads(r.stdout)
    assert o["status"] == "error" and "不存在" in o["error"]


def test_literal_text_still_accepted():
    import subprocess, sys, json
    r = subprocess.run([sys.executable, str(SP / "seo_optimizer.py"),
                        "--title", "FastAPI 性能优化 2026 实战",
                        "--content", "FastAPI 性能优化有很多技巧，FastAPI 性能优化的核心是异步与缓存，实测吞吐提升三倍"],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    o = json.loads(r.stdout)
    assert o["meta"]["score"] > 0 and "FastAPI" in "".join(o["meta"]["keywords"])
