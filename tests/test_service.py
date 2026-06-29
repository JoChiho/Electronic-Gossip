"""起卦服务层测试。"""

import random
from datetime import datetime

from bagua.config import build_user_context
from bagua.models import UserConfig, UserContext
from bagua.service import perform_divination
from bagua.timezone import get_timezone


def _ctx() -> UserContext:
    cfg = UserConfig(
        question="工作运势",
        bazi="甲子",
        birth_datetime="1990-01-01 08:00",
        timezone="Asia/Shanghai",
        region_label="中国",
    )
    return build_user_context(cfg)


def test_perform_divination_random():
    rng = random.Random(42)
    result = perform_divination("random", _ctx(), rng=rng)
    assert len(result.yao_values) == 6
    assert result.hexagram.name
    assert "随机起卦" in result.method_desc
    assert "工作运势" in result.prompt
    assert "Asia/Shanghai" in result.divination_time


def test_perform_divination_coin_manual():
    tosses = [[3, 3, 3], [3, 2, 2], [2, 2, 2], [3, 3, 2], [2, 3, 3], [3, 2, 3]]
    result = perform_divination("coin", _ctx(), coin_tosses=tosses, coin_mode="manual")
    assert result.yao_values == [9, 7, 6, 8, 8, 8]
    assert "手动投掷" in result.method_desc


def test_perform_divination_coin_auto():
    rng = random.Random(0)
    result = perform_divination("coin", _ctx(), coin_mode="auto", rng=rng)
    assert len(result.yao_values) == 6
    assert "自动模拟" in result.method_desc


def test_perform_divination_time():
    birth_tz = get_timezone("UTC", "UTC")
    div_tz = get_timezone("UTC", "UTC")
    ctx = UserContext(
        question="",
        bazi="",
        birth_datetime="",
        birth_tz=birth_tz,
        divination_tz=div_tz,
        coin_mode="manual",
    )
    dt = datetime(2026, 6, 24, 14, 30, tzinfo=div_tz.tzinfo)
    result = perform_divination("time", ctx, divination_datetime=dt)
    assert result.hexagram.name
    assert "时间起卦" in result.method_desc
    assert "节气历" in result.method_desc
    assert "用户公历" in result.divination_time
    assert "节气历" in result.prompt


def test_birth_and_divination_timezone_split():
    """北京出生、东京起卦：八字与起卦时刻应各用时区。"""
    cfg = UserConfig(
        timezone="Asia/Shanghai",
        region_label="中国（北京时间 UTC+8）",
        divination_timezone="Asia/Tokyo",
        divination_region_label="日本（东京 UTC+9）",
        birth_datetime="1990-01-01 08:00",
        bazi="",
        auto_bazi=True,
    )
    ctx = build_user_context(cfg)
    assert ctx.birth_tz.iana_name == "Asia/Shanghai"
    assert ctx.divination_tz.iana_name == "Asia/Tokyo"

    dt = datetime(2026, 6, 24, 15, 0, tzinfo=ctx.divination_tz.tzinfo)
    result = perform_divination("time", ctx, divination_datetime=dt, auto_bazi=True)
    assert "出生时区" in result.prompt or "Asia/Shanghai" in result.prompt
    assert "Asia/Tokyo" in result.divination_time or "日本" in result.divination_time
    assert result.hexagram.name


def test_perform_divination_auto_bazi():
    cfg = UserConfig(
        question="测试",
        bazi="",
        birth_datetime="1990-05-15 08:30",
        timezone="Asia/Shanghai",
        region_label="中国",
    )
    ctx = build_user_context(cfg)
    result = perform_divination("random", ctx, rng=random.Random(1), auto_bazi=True)
    assert "庚午" in result.prompt


def test_prompt_includes_hexagram_text():
    div_tz = get_timezone("UTC", "UTC")
    ctx = UserContext(
        question="",
        bazi="",
        birth_datetime="",
        birth_tz=div_tz,
        divination_tz=div_tz,
        coin_mode="manual",
        include_hexagram_texts=True,
    )
    dt = datetime(2026, 6, 24, 14, 30, tzinfo=div_tz.tzinfo)
    result = perform_divination("time", ctx, divination_datetime=dt)
    assert "卦辞摘要" in result.prompt