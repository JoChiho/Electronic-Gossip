"""生辰八字自动排盘。"""

from __future__ import annotations

from bagua.lunar_util import is_lunar_available
from bagua.timezone import TimezoneInfo, parse_datetime_input

try:
    from lunar_python import Solar
except ImportError:  # pragma: no cover
    Solar = None  # type: ignore[misc, assignment]


def compute_bazi(birth_datetime: str, tz: TimezoneInfo) -> str | None:
    """
    根据公历出生时间（配合用户时区）自动排八字。

    返回如「庚午年 辛巳月 庚辰日 庚辰时」，解析失败返回 None。
    """
    if not birth_datetime.strip():
        return None
    if not is_lunar_available() or Solar is None:
        return None

    dt = parse_datetime_input(birth_datetime, tz)
    if dt is None:
        return None

    solar = Solar.fromYmdHms(
        dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second
    )
    ec = solar.getLunar().getEightChar()
    return f"{ec.getYear()}年 {ec.getMonth()}月 {ec.getDay()}日 {ec.getTime()}时"


def maybe_auto_bazi(
    birth_datetime: str,
    bazi: str,
    tz: TimezoneInfo,
    *,
    auto: bool = True,
) -> str:
    """若启用自动排盘且八字为空，则从出生时间生成八字。"""
    if bazi.strip() or not auto:
        return bazi
    computed = compute_bazi(birth_datetime, tz)
    return computed or bazi