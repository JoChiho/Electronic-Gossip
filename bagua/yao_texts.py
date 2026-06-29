"""六十四卦爻辞查询 API。"""

from __future__ import annotations

from bagua.data import YAO_POSITIONS
from bagua.yao_texts_data import YAO_TEXTS


def get_yao_text(hexagram_name: str, position: int) -> str | None:
    """返回指定卦第 position 爻（1–6）的爻辞原文。"""
    if position < 1 or position > 6:
        return None
    texts = YAO_TEXTS.get(hexagram_name)
    if not texts:
        return None
    return texts[position - 1]


def get_hexagram_yao_texts(hexagram_name: str) -> tuple[str, ...] | None:
    return YAO_TEXTS.get(hexagram_name)


def format_yao_texts_block(
    hexagram_name: str,
    *,
    highlight_positions: set[int] | None = None,
    only_highlight: bool = False,
) -> list[str]:
    """
    格式化爻辞块。

    only_highlight=True 时仅输出 highlight_positions 中的爻辞；
    否则输出六爻全文，高亮变爻。
    """
    texts = YAO_TEXTS.get(hexagram_name)
    if not texts:
        return []
    highlights = highlight_positions or set()
    lines = ["  爻辞（《周易》原文）："]
    for i, text in enumerate(texts, start=1):
        if only_highlight and i not in highlights:
            continue
        pos_name = YAO_POSITIONS[i - 1]
        mark = " ★" if i in highlights else ""
        lines.append(f"    {pos_name}{mark}：{text}")
    if only_highlight and not any(i in highlights for i in range(1, 7)):
        return []
    return lines