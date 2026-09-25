import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import editor  # noqa: E402

CJK_SAMPLE = "第一句。第二句！第三句？"


def test_chinese_sentence_split():
    result = editor.edit_text(CJK_SAMPLE)
    assert result["total_sentences"] == 3, result


def test_reports_char_count_and_word_count_separately():
    result = editor.edit_text(CJK_SAMPLE)
    assert result["char_count"] == len(CJK_SAMPLE)
    assert result["word_count"] != len(CJK_SAMPLE)


def test_english_sentence_split_still_works():
    result = editor.edit_text("First sentence. Second one. Third.")
    assert result["total_sentences"] == 3, result
