"""八字排盘测试。"""

from bagua.bazi import compute_bazi, maybe_auto_bazi
from bagua.timezone import get_timezone


def test_compute_bazi_from_birth_datetime():
    tz = get_timezone("Asia/Shanghai", "中国")
    bazi = compute_bazi("1990-05-15 08:30", tz)
    assert bazi is not None
    assert "庚午" in bazi
    assert "年" in bazi and "月" in bazi


def test_maybe_auto_bazi_fills_when_empty():
    tz = get_timezone("Asia/Shanghai", "中国")
    result = maybe_auto_bazi("1990-05-15 08:30", "", tz, auto=True)
    assert result.strip()
    assert maybe_auto_bazi("1990-05-15 08:30", "已有八字", tz, auto=True) == "已有八字"


def test_compute_bazi_invalid_returns_none():
    tz = get_timezone("Asia/Shanghai", "中国")
    assert compute_bazi("not-a-date", tz) is None