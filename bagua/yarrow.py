"""大衍筮法（蓍草法）模拟纯逻辑。"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING

from bagua.data import METHOD_LABELS, YAO_POSITIONS, YAO_VALUE_NAMES

if TYPE_CHECKING:
    from _random import Random

DAYAN_START_STALKS = 49
DAYAN_VALID_REMAINDERS = frozenset({24, 28, 32, 36})
YAO_FROM_REMAINDER = {24: 6, 28: 7, 32: 8, 36: 9}


@dataclass(frozen=True)
class YarrowChangeRecord:
    change_no: int
    stalks_before: int
    left: int
    right: int
    hung: int
    left_remainder: int
    right_remainder: int
    removed: int
    stalks_after: int


@dataclass(frozen=True)
class YarrowYaoRecord:
    position: int
    changes: tuple[YarrowChangeRecord, ...]
    remaining: int
    value: int


def _remainder_mod4(n: int) -> int:
    r = n % 4
    return 4 if r == 0 else r


def dayan_single_change(
    stalk_count: int,
    rng: Random,
    *,
    change_no: int = 1,
) -> tuple[int, YarrowChangeRecord]:
    """分二、挂一、揲四、归奇，返回余蓍数与步骤记录。"""
    if stalk_count < 2:
        raise ValueError(f"揲筮需要至少 2 茎蓍草，当前 {stalk_count}")

    left = rng.randint(1, stalk_count - 1)
    right = stalk_count - left
    hung = 1
    left_rem = _remainder_mod4(left)
    right_rem = _remainder_mod4(right - hung)
    removed = hung + left_rem + right_rem
    remaining = stalk_count - removed

    record = YarrowChangeRecord(
        change_no=change_no,
        stalks_before=stalk_count,
        left=left,
        right=right,
        hung=hung,
        left_remainder=left_rem,
        right_remainder=right_rem,
        removed=removed,
        stalks_after=remaining,
    )
    return remaining, record


def dayan_one_yao(
    rng: Random,
    *,
    position: int,
) -> tuple[int, YarrowYaoRecord]:
    """三变得一爻，起算 49 茎（大衍之数五十，其用四十有九）。"""
    stalks = DAYAN_START_STALKS
    changes: list[YarrowChangeRecord] = []
    for change_no in range(1, 4):
        stalks, record = dayan_single_change(stalks, rng, change_no=change_no)
        changes.append(record)

    if stalks not in DAYAN_VALID_REMAINDERS:
        raise ValueError(f"三变后蓍数异常：{stalks}，期望 24/28/32/36")
    value = YAO_FROM_REMAINDER[stalks]
    yao_record = YarrowYaoRecord(
        position=position,
        changes=tuple(changes),
        remaining=stalks,
        value=value,
    )
    return value, yao_record


def format_yarrow_log(records: list[YarrowYaoRecord]) -> str:
    lines: list[str] = ["【大衍演卦过程】", "大衍之数五十，其用四十有九。"]
    for yao in records:
        pos_name = YAO_POSITIONS[yao.position - 1]
        lines.append(f"\n第{yao.position}爻（{pos_name}）")
        for ch in yao.changes:
            lines.append(
                f"  变{ch.change_no}：{ch.stalks_before}茎 "
                f"→ 分 {ch.left}+{ch.right}，挂一，归奇 {ch.removed} "
                f"→ 余 {ch.stalks_after}"
            )
        lines.append(
            f"  三变余 {yao.remaining} 茎 → 爻值 {yao.value}（{YAO_VALUE_NAMES[yao.value]}）"
        )
    return "\n".join(lines)


def divinate_yarrow(
    rng: Random | None = None,
    *,
    record_steps: bool = False,
) -> tuple[list[int], str, str | None]:
    """
    模拟大衍筮法起六爻。

    返回 (六爻值, method_desc, 可选步骤日志)。
    """
    r = rng or random.Random()
    yao_records: list[YarrowYaoRecord] = []
    values: list[int] = []
    for pos in range(1, 7):
        value, record = dayan_one_yao(r, position=pos)
        values.append(value)
        yao_records.append(record)

    summary = " ".join(f"{v}({YAO_VALUE_NAMES[v]})" for v in values)
    method_desc = f"{METHOD_LABELS['yarrow']}（大衍筮法模拟，非实体蓍草；六爻：{summary}）"
    step_log = format_yarrow_log(yao_records) if record_steps else None
    return values, method_desc, step_log