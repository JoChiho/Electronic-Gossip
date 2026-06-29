"""起卦服务层：CLI / GUI 共用统一入口。"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from bagua.bazi import maybe_auto_bazi
from bagua.divination import divinate_by_random, divinate_by_time, divinate_coin
from bagua.hexagram import build_hexagram
from bagua.models import DivinationMethod, DivinationResult, UserContext
from bagua.prompt import generate_ai_prompt
from bagua.timezone import format_datetime_with_tz, now_in_timezone

if TYPE_CHECKING:
    from _random import Random


def perform_divination(
    method: DivinationMethod,
    context: UserContext,
    *,
    coin_tosses: list[list[int]] | None = None,
    divination_datetime: datetime | None = None,
    coin_mode: str = "manual",
    auto_bazi: bool = True,
    rng: Random | None = None,
) -> DivinationResult:
    """
    执行完整起卦流程并生成 AI 提示词。

    Args:
        method: 起卦方式 coin / time / random
        context: 用户上下文（问题、八字、时区等）
        coin_tosses: 铜钱法六爻投掷结果，每爻三个点数（2 或 3）
        divination_datetime: 时间起卦指定时刻；None 则用当前时区时间
        coin_mode: manual 需 coin_tosses；auto 自动模拟
        rng: 可选随机数生成器（便于测试）
    """
    dt_now = now_in_timezone(context.tz)
    prompt_context = context
    if auto_bazi and not context.bazi.strip() and context.birth_datetime.strip():
        bazi = maybe_auto_bazi(
            context.birth_datetime,
            context.bazi,
            context.tz,
            auto=True,
        )
        if bazi.strip():
            prompt_context = UserContext(
                question=context.question,
                bazi=bazi,
                birth_datetime=context.birth_datetime,
                tz=context.tz,
                coin_mode=context.coin_mode,
                calendar_mode=context.calendar_mode,
                lunar_input=context.lunar_input,
                include_hexagram_texts=context.include_hexagram_texts,
            )

    if method == "coin":
        values, method_desc = divinate_coin(
            coin_tosses=coin_tosses,
            coin_mode=coin_mode,
            rng=rng,
        )
        divination_time = format_datetime_with_tz(dt_now, context.tz)
    elif method == "time":
        dt = divination_datetime or dt_now
        values, method_desc = divinate_by_time(
            dt,
            calendar_mode=context.calendar_mode,
            lunar_input=context.lunar_input,
        )
        divination_time = format_datetime_with_tz(dt, context.tz)
        if context.calendar_mode == "lunar" and context.lunar_input:
            divination_time = f"{divination_time}（农历输入：{context.lunar_input}）"
    elif method == "random":
        values, method_desc = divinate_by_random(rng)
        divination_time = format_datetime_with_tz(dt_now, context.tz)
    else:
        raise ValueError(f"未知起卦方式: {method}")

    hexagram = build_hexagram(values)
    prompt = generate_ai_prompt(prompt_context, method_desc, divination_time, hexagram)

    return DivinationResult(
        yao_values=values,
        hexagram=hexagram,
        method_desc=method_desc,
        divination_time=divination_time,
        prompt=prompt,
    )