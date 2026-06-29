"""汉字起卦测试。"""

from bagua.character import (
    CHARACTER_STRATEGIES,
    character_to_numbers,
    divinate_by_character,
    extract_han_chars,
    parse_character_input,
)
from bagua.hexagram import build_hexagram
from bagua.stroke_data import get_stroke_count


def test_extract_han_chars():
    assert extract_han_chars("问 事！") == ["问", "事"]
    assert parse_character_input("hello") is None


def test_kangxi_stroke_counts():
    assert get_stroke_count("乾", "kangxi") == (11, "dict")
    assert get_stroke_count("坤", "kangxi") == (8, "dict")
    assert get_stroke_count("水", "kangxi") == (4, "dict")
    assert get_stroke_count("火", "kangxi") == (4, "dict")


def test_simplified_stroke_differs_for_li():
    kangxi = get_stroke_count("离", "kangxi")[0]
    simp = get_stroke_count("离", "simplified")[0]
    assert kangxi == 19
    assert simp == 10


def test_character_single_char_qian():
    n1, n2, n3, chars, strokes, _sources, note = character_to_numbers("乾", strategy="auto")
    assert chars == ["乾"]
    assert strokes == [11]
    assert n1 == 11 and n2 == 12 and n3 is None
    assert "单字" in note

    values, desc = divinate_by_character("乾")
    assert values == [7, 8, 8, 7, 6, 7]
    assert build_hexagram(values).name == "火雷噬嗑"
    assert "乾=11" in desc


def test_character_first_two_shui_huo():
    values, desc = divinate_by_character("水火", strategy="first_two")
    assert values == [7, 6, 8, 7, 8, 8]
    assert build_hexagram(values).name == "震为雷"
    assert "水=4" in desc and "火=4" in desc


def test_character_first_three_wen_shi_ren():
    values, desc = divinate_by_character("问事人", strategy="first_three")
    assert values == [8, 6, 8, 7, 8, 7]
    assert build_hexagram(values).name == "火地晋"
    assert "问=11" in desc and "事=8" in desc and "人=2" in desc


def test_character_total_strategy():
    n1, n2, n3, chars, strokes, _s, note = character_to_numbers(
        "水火", strategy="total",
    )
    assert n1 == sum(strokes)
    assert n2 == len(chars)
    assert n3 is None
    assert "总笔画" in note


def test_character_strategies_defined():
    assert "auto" in CHARACTER_STRATEGIES
    assert "total" in CHARACTER_STRATEGIES