"""用户偏好辅助测试。"""

from bagua.user_prefs import (
    METHOD_KEY_TO_NUM,
    normalize_method,
    points_to_stored_coin_tosses,
    stored_coin_tosses_to_points,
)


def test_normalize_method():
    assert normalize_method("time") == "time"
    assert normalize_method("invalid", default="random") == "random"


def test_coin_tosses_roundtrip():
    tosses = [[3, 2, 3], [2, 2, 2], [3, 3, 3], [2, 3, 2], [3, 2, 2], [2, 3, 3]]
    stored = points_to_stored_coin_tosses(tosses)
    assert stored == [["1", "2", "1"], ["2", "2", "2"], ["1", "1", "1"], ["2", "1", "2"], ["1", "2", "2"], ["2", "1", "1"]]
    assert stored_coin_tosses_to_points(stored) == tosses


def test_method_key_mapping():
    assert METHOD_KEY_TO_NUM["coin"] == "1"
    assert METHOD_KEY_TO_NUM["number"] == "4"
    assert METHOD_KEY_TO_NUM["manual"] == "5"
    assert METHOD_KEY_TO_NUM["yarrow"] == "6"
    assert METHOD_KEY_TO_NUM["character"] == "7"