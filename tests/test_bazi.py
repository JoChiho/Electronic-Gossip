"""八字排盘测试。"""

from bagua.bazi import compute_bazi, maybe_auto_bazi
from bagua.timezone import get_timezone


def test_compute_bazi_from_birth_datetime():
    tz = get_timezone("Asia/Shanghai", "中国")
    bazi, note = compute_bazi(
        "1990-05-15 08:30", tz, use_true_solar=False,
    )
    assert bazi is not None
    assert "庚午" in bazi
    assert "年" in bazi and "月" in bazi
    assert note == ""


def test_compute_bazi_true_solar_can_shift_time():
    tz = get_timezone("Asia/Shanghai", "中国")
    bazi, note = compute_bazi("1990-05-15 08:30", tz, use_true_solar=True)
    assert bazi is not None
    assert "真太阳时" in note


def test_maybe_auto_bazi_fills_when_empty():
    tz = get_timezone("Asia/Shanghai", "中国")
    result, _note = maybe_auto_bazi(
        "1990-05-15 08:30", "", tz, auto=True, use_true_solar=False,
    )
    assert result.strip()
    kept, _ = maybe_auto_bazi("1990-05-15 08:30", "已有八字", tz, auto=True)
    assert kept == "已有八字"


def test_compute_bazi_invalid_returns_none():
    tz = get_timezone("Asia/Shanghai", "中国")
    bazi, note = compute_bazi("not-a-date", tz)
    assert bazi is None
    assert note == ""