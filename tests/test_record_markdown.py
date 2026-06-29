"""Markdown 导出格式测试。"""

from bagua.hexagram import build_hexagram
from bagua.record_markdown import record_to_markdown, records_to_markdown


def _sample_data() -> dict:
    h = build_hexagram([7, 8, 9, 6, 7, 8])
    return {
        "saved_at": "2026-06-29T12:00:00",
        "divination_time": "2026-06-29 12:00",
        "method": "随机起卦",
        "timezone": "Asia/Shanghai",
        "question": "工作运势",
        "bazi": "庚午",
        "birth_datetime": "1990-01-01 08:00",
        "hexagram": {
            "name": h.name,
            "upper_trigram": h.upper_trigram["name"],
            "lower_trigram": h.lower_trigram["name"],
            "changing_positions": h.changing_positions,
            "yaos": [
                {
                    "position": y.position,
                    "label": y.label,
                    "is_yang": y.is_yang,
                    "is_changing": y.is_changing,
                }
                for y in h.yaos
            ],
            "changed_hexagram": {
                "name": h.changed_hexagram.name,
                "upper_trigram": h.changed_hexagram.upper_trigram["name"],
                "lower_trigram": h.changed_hexagram.lower_trigram["name"],
            }
            if h.changed_hexagram
            else None,
        },
        "prompt": "AI 提示词正文",
    }


def test_record_to_markdown_contains_sections():
    md = record_to_markdown(_sample_data())
    assert "# 占卜记录" in md
    assert "## 概览" in md
    assert "## 卦象" in md
    assert "## AI 解读提示词" in md
    assert "工作运势" in md
    assert "AI 提示词正文" in md


def test_records_to_markdown_batch():
    md = records_to_markdown([_sample_data(), _sample_data()])
    assert "共 2 条记录" in md
    assert md.count("# 占卜记录") == 2