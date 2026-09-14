"""Smoke tests for channel-adapter's channel_fit_check.py."""
import importlib.util
import json
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "channel_fit_check.py"
spec = importlib.util.spec_from_file_location("channel_fit_check", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

GOOD_XHS = ("被这个保温杯惊艳到了\n"
            "早上装的热水，下午开会还是烫的\n"
            "杯口设计单手就能开，开车党狂喜\n"
            "316 不锈钢内胆，官方检测报告都在\n"
            "需要的姐妹评论区找我")

BAD_XHS = ("我们本公司隆重推出超级保温杯！！！\n"
           "这是世界上最好的保温杯，赶紧下单，立即抢购，点击锁定优惠，"
           "手慢无，速来评论区，马上私信我们，关注订阅店铺\n"
           "错过等一年") * 16

GOOD_AD = "316不锈钢保温杯12小时保温"
BAD_AD = "史上最强！！！最强保温杯限时秒杀速来抢购点击下单立即购买错过今天再等一年"


def test_good_xhs_passes():
    report, code = mod.audit(GOOD_XHS, "xhs")
    assert code == 0 and report["status"] == "pass", report


def test_bad_xhs_fails_multiple():
    report, code = mod.audit(BAD_XHS, "xhs")
    assert code == 1
    failed = {c["check"] for c in report["checks"] if not c["pass"]}
    assert "word_budget" in failed and "cta_count" in failed


def test_search_ad_length_and_bang():
    ok, code = mod.audit(GOOD_AD, "search-ad")
    assert code == 0
    bad, code = mod.audit(BAD_AD, "search-ad")
    failed = {c["check"] for c in bad["checks"] if not c["pass"]}
    assert "no_bang_spam" in failed and "word_budget" in failed


def test_moments_line_limit():
    text = "\n".join(f"第{i}行卖点" for i in range(1, 9))
    report, code = mod.audit(text, "moments")
    failed = {c["check"] for c in report["checks"] if not c["pass"]}
    assert "line_limit" in failed and code == 1


def test_unknown_channel_usage_error():
    report, code = mod.audit("x", "weibo-timeline")
    assert code == 2 and "known" in report


def test_main_json(capsys):
    assert mod.main(["--text", GOOD_AD, "--channel", "search-ad"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "pass"
