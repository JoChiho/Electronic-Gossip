"""农历与历法换算（基于 lunar-python，纯逻辑层）。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

try:
    from lunar_python import Lunar, Solar
except ImportError:  # pragma: no cover - 测试环境会安装依赖
    Lunar = None  # type: ignore[misc, assignment]
    Solar = None  # type: ignore[misc, assignment]

CalendarMode = str  # "solar" | "lunar"


@dataclass(frozen=True)
class LunarComponents:
    """梅花易数起卦用的农历数字分量。"""

    year: int
    month: int
    day: int
    hour: int
    label: str
    is_leap_month: bool = False


def is_lunar_available() -> bool:
    return Lunar is not None and Solar is not None


def _require_lunar() -> None:
    if not is_lunar_available():
        raise RuntimeError("农历功能需要安装 lunar-python：pip install lunar-python")


def solar_datetime_to_lunar(dt: datetime) -> LunarComponents:
    """将公历时刻转为农历分量（含时辰序号 1–12）。"""
    _require_lunar()
    local = dt
    solar = Solar.fromYmdHms(
        local.year, local.month, local.day, local.hour, local.minute, local.second
    )
    lunar = solar.getLunar()
    month = lunar.getMonth()
    return LunarComponents(
        year=lunar.getYear(),
        month=abs(month),
        day=lunar.getDay(),
        hour=lunar.getTimeZhiIndex() + 1,
        label=lunar.toString(),
        is_leap_month=month < 0,
    )


def lunar_datetime_to_components(
    year: int,
    month: int,
    day: int,
    hour: int = 0,
    minute: int = 0,
) -> LunarComponents:
    """由农历年月日时分构建分量。"""
    _require_lunar()
    lunar = Lunar.fromYmdHms(year, month, day, hour, minute, 0)
    m = lunar.getMonth()
    return LunarComponents(
        year=lunar.getYear(),
        month=abs(m),
        day=lunar.getDay(),
        hour=lunar.getTimeZhiIndex() + 1,
        label=lunar.toString(),
        is_leap_month=m < 0,
    )


def parse_lunar_datetime_input(raw: str) -> tuple[int, int, int, int, int] | None:
    """
    解析农历日期时间字符串，返回 (年, 月, 日, 时, 分)。
    支持格式：YYYY-MM-DD HH:MM、YYYY-MM-DD、YYYY/MM/DD HH:MM
    """
    raw = raw.strip()
    if not raw:
        return None
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M", "%Y-%m-%d"):
        try:
            naive = datetime.strptime(raw, fmt)
            return naive.year, naive.month, naive.day, naive.hour, naive.minute
        except ValueError:
            continue
    return None


def resolve_time_divination_components(
    dt: datetime,
    *,
    calendar_mode: CalendarMode = "solar",
    lunar_input: str | None = None,
) -> tuple[int, int, int, int, str]:
    """
    解析时间起卦用的年月日时数字与描述前缀。

    Returns:
        (year, month, day, hour, detail_prefix)
    """
    if calendar_mode == "lunar":
        _require_lunar()
        if lunar_input:
            parsed = parse_lunar_datetime_input(lunar_input)
            if parsed is None:
                raise ValueError("农历时间格式无效，请使用如 2026-05-10 14:30")
            y, m, d, h, mi = parsed
            comp = lunar_datetime_to_components(y, m, d, h, mi)
        else:
            comp = solar_datetime_to_lunar(dt)
        leap = "（闰月）" if comp.is_leap_month else ""
        prefix = f"农历{comp.label}{leap}"
        return comp.year, comp.month, comp.day, comp.hour, prefix

    year, month, day = dt.year, dt.month, dt.day
    hour = (dt.hour // 2) % 12 + 1
    prefix = f"公历{dt.strftime('%Y-%m-%d %H:%M')}"
    return year, month, day, hour, prefix