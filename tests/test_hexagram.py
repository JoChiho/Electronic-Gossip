"""卦象计算测试。"""

from bagua.divination import parse_coin_input
from bagua.hexagram import build_hexagram


def test_pure_yang_hexagram():
    h = build_hexagram([7, 7, 7, 7, 7, 7])
    assert h.name == "乾为天"
    assert not h.has_changing


def test_changing_lines():
    h = build_hexagram([7, 8, 9, 6, 7, 8])
    assert h.has_changing
    assert h.changed_hexagram is not None
    assert h.changed_hexagram.name == "泽雷随"


def test_changed_hexagram_uses_flipped_yaos():
    h = build_hexagram([7, 8, 9, 6, 7, 8])
    changed = h.changed_hexagram
    assert changed is not None
    assert changed.yaos[2].value == 8 and not changed.yaos[2].is_yang
    assert changed.yaos[3].value == 7 and changed.yaos[3].is_yang
    assert not any(y.is_changing for y in changed.yaos)


def test_coin_input_121():
    assert parse_coin_input("1 2 1") == [3, 2, 3]


def test_coin_input_invalid():
    assert parse_coin_input("1 2") is None
    assert parse_coin_input("a b c") is None