"""大衍蓍草法测试。"""

import random
from collections import Counter

from bagua.yarrow import (
    DAYAN_START_STALKS,
    dayan_one_yao,
    dayan_single_change,
    divinate_yarrow,
)


def test_dayan_single_change_removes_valid_amount():
    rng = random.Random(0)
    remaining, record = dayan_single_change(DAYAN_START_STALKS, rng)
    assert 5 <= record.removed <= 9
    assert remaining == DAYAN_START_STALKS - record.removed
    assert record.left + record.right == DAYAN_START_STALKS


def test_dayan_one_yao_valid_value():
    rng = random.Random(42)
    value, record = dayan_one_yao(rng, position=1)
    assert value in (6, 7, 8, 9)
    assert record.remaining in (24, 28, 32, 36)
    assert record.remaining // 4 == value
    assert len(record.changes) == 3


def test_divinate_yarrow_reproducible_with_seed():
    rng1 = random.Random(99)
    rng2 = random.Random(99)
    values1, _, _ = divinate_yarrow(rng1)
    values2, _, _ = divinate_yarrow(rng2)
    assert values1 == values2
    assert len(values1) == 6
    assert all(v in (6, 7, 8, 9) for v in values1)


def test_divinate_yarrow_step_log():
    rng = random.Random(7)
    _, desc, log = divinate_yarrow(rng, record_steps=True)
    assert log is not None
    assert "大衍演卦过程" in log
    assert "第1爻" in log
    assert "第6爻" in log
    assert "蓍草法" in desc
    assert "模拟" in desc


def test_yarrow_distribution_matches_dayan_theory():
    """大衍筮法理论概率：6→1/16，7→5/16，8→7/16，9→3/16（与三钱法不同）。"""
    rng = random.Random(2026)
    counts: Counter[int] = Counter()
    trials = 24_000
    for _ in range(trials):
        values, _, _ = divinate_yarrow(rng)
        counts.update(values)

    total = trials * 6
    expected_ratios = {6: 1 / 16, 7: 5 / 16, 8: 7 / 16, 9: 3 / 16}
    for value, expected in expected_ratios.items():
        ratio = counts[value] / total
        assert abs(ratio - expected) < 0.015, f"爻值{value} 占比 {ratio:.3f} 偏离大衍预期 {expected:.4f}"