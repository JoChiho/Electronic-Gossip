"""农历换算测试。"""

from datetime import datetime

import pytest
from bagua.lunar_util import (
    parse_lunar_datetime_input,
    resolve_time_divination_components,
    solar_datetime_to_lunar,
)
from bagua.timezone import get_timezone


def test_parse_lunar_datetime_input():
    assert parse_lunar_datetime_input("2026-05-10 14:30") == (2026, 5, 10, 14, 30)
    assert parse_lunar_datetime_input("bad") is None


def test_solar_to_lunar_components():
    tz = get_timezone("Asia/Shanghai", "中国")
    dt = datetime(2026, 6, 24, 14, 30, tzinfo=tz.tzinfo)
    comp = solar_datetime_to_lunar(dt)
    assert comp.year == 2026
    assert comp.month >= 1
    assert comp.day >= 1
    assert 1 <= comp.hour <= 12


def test_resolve_lunar_input_mode():
    tz = get_timezone("Asia/Shanghai", "中国")
    dt = datetime(2026, 6, 24, 14, 30, tzinfo=tz.tzinfo)
    y, m, d, h, prefix = resolve_time_divination_components(
        dt,
        calendar_mode="lunar",
        lunar_input="2026-05-10 14:30",
    )
    assert y == 2026 and m == 5 and d == 10
    assert "农历" in prefix


def test_resolve_lunar_invalid_input_raises():
    tz = get_timezone("UTC", "UTC")
    dt = datetime(2026, 6, 24, 14, 30, tzinfo=tz.tzinfo)
    with pytest.raises(ValueError):
        resolve_time_divination_components(dt, calendar_mode="lunar", lunar_input="invalid")