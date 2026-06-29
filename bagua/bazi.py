"""生辰八字自动排盘。"""

from __future__ import annotations

from bagua.lunar_util import is_lunar_available
from bagua.timezone import TimezoneInfo, parse_datetime_input
from bagua.true_solar import to_true_solar

try:
    from lunar_python import Solar
except ImportError:  # pragma: no cover
    Solar = None  # type: ignore[misc, assignment]


def compute_bazi(
    birth_datetime: str,
    tz: TimezoneInfo,
    *,
    longitude: float | None = None,
    use_true_solar: bool = True,
) -> tuple[str | None, str]:
    """
    根据公历出生时间（配合出生时区）自动排八字。

    返回 (八字字符串, 真太阳时说明)。解析失败时返回 (None, "")。
    八字用于 AI 提示词参考，不参与卦象演算。
    """
    if not birth_datetime.strip():
        return None, ""
    if not is_lunar_available() or Solar is None:
        return None, ""

    dt = parse_datetime_input(birth_datetime, tz)
    if dt is None:
        return None, ""

    calc_dt, note = to_true_solar(dt, tz, longitude, enabled=use_true_solar)
    solar = Solar.fromYmdHms(
        calc_dt.year, calc_dt.month, calc_dt.day, calc_dt.hour, calc_dt.minute, calc_dt.second,
    )
    ec = solar.getLunar().getEightChar()
    return f"{ec.getYear()}年 {ec.getMonth()}月 {ec.getDay()}日 {ec.getTime()}时", note


def maybe_auto_bazi(
    birth_datetime: str,
    bazi: str,
    tz: TimezoneInfo,
    *,
    auto: bool = True,
    longitude: float | None = None,
    use_true_solar: bool = True,
) -> tuple[str, str]:
    """若启用自动排盘且八字为空，则从出生时间生成八字。返回 (八字, 真太阳时说明)。"""
    if bazi.strip() or not auto:
        return bazi, ""
    computed, note = compute_bazi(
        birth_datetime, tz, longitude=longitude, use_true_solar=use_true_solar,
    )
    return computed or bazi, note