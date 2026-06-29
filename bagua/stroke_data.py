"""汉字笔画数据（康熙 / 简体）。"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

STROKE_MODES = ("kangxi", "simplified")
STROKE_MODE_LABELS = {
    "kangxi": "康熙字典笔画",
    "simplified": "简体字笔画",
}

_DATA_PATH = Path(__file__).resolve().parent / "data" / "strokes.json"


@lru_cache(maxsize=1)
def _load_stroke_tables() -> dict[str, dict[str, int]]:
    if not _DATA_PATH.exists():
        return {"kangxi": {}, "simplified": {}}
    with _DATA_PATH.open(encoding="utf-8") as f:
        raw = json.load(f)
    return {
        "kangxi": {k: int(v) for k, v in raw.get("kangxi", {}).items()},
        "simplified": {k: int(v) for k, v in raw.get("simplified", {}).items()},
    }


def codepoint_stroke_fallback(char: str) -> int:
    """未收录汉字时以码点回退取数（文档化非笔画真值）。"""
    code = ord(char)
    if 0x4E00 <= code <= 0x9FFF:
        return (code - 0x4E00) % 48 + 1
    return code % 48 + 1


def get_stroke_count(char: str, mode: str = "kangxi") -> tuple[int, str]:
    """
    返回 (笔画数, 来源)。

    来源为 ``dict``（字表命中）或 ``codepoint``（码点回退）。
    """
    if len(char) != 1:
        raise ValueError("笔画查询需要单个汉字")
    if mode not in STROKE_MODES:
        raise ValueError(f"笔画口径须为 {STROKE_MODES}")

    tables = _load_stroke_tables()
    count = tables.get(mode, {}).get(char)
    if count is not None:
        return count, "dict"
    return codepoint_stroke_fallback(char), "codepoint"


def format_stroke_preview(chars: list[str], strokes: list[int], sources: list[str], mode: str) -> str:
    parts: list[str] = []
    mode_label = STROKE_MODE_LABELS.get(mode, mode)
    for ch, n, src in zip(chars, strokes, sources, strict=True):
        tag = "" if src == "dict" else "·码点回退"
        parts.append(f"{ch}={n}{tag}")
    return f"{mode_label}：" + "，".join(parts)