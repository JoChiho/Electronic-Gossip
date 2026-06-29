#!/usr/bin/env python3
"""从 open-iching 数据集生成 bagua/yao_texts_data.py（运行一次即可）。"""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path

from bagua.data import HEXAGRAM_NAMES, TRIGRAMS

SOURCE_URL = (
    "https://raw.githubusercontent.com/john-walks-slow/open-iching/main/iching/iching.json"
)
OUTPUT = Path(__file__).resolve().parents[1] / "bagua" / "yao_texts_data.py"


def _trigram_index(lines: tuple[int, ...]) -> int:
    for i, tri in enumerate(TRIGRAMS):
        if tri["lines"] == lines:
            return i
    raise ValueError(f"未知三爻: {lines}")


def _hexagram_name_from_array(bits: list[int]) -> str:
    lower = tuple(bits[0:3])
    upper = tuple(bits[3:6])
    return HEXAGRAM_NAMES[_trigram_index(upper)][_trigram_index(lower)]


def main() -> None:
    raw = urllib.request.urlopen(SOURCE_URL, timeout=60).read()
    items = json.loads(raw.decode("utf-8"))
    mapping: dict[str, list[str]] = {}
    for item in items:
        name = _hexagram_name_from_array(item["array"])
        lines = [
            line["scripture"].strip()
            for line in item["lines"]
            if line["id"] <= 6
        ]
        if len(lines) != 6:
            raise ValueError(f"{name} 爻辞数量异常: {len(lines)}")
        mapping[name] = lines

    expected = {HEXAGRAM_NAMES[u][l] for u in range(8) for l in range(8)}
    missing = expected - set(mapping.keys())
    if missing:
        raise SystemExit(f"缺少卦名: {sorted(missing)}")

    lines_out = [
        '"""六十四卦爻辞全文（《周易》经传，自下而上初爻→上爻）。"""',
        "",
        "from __future__ import annotations",
        "",
        "# 数据来源：open-iching (MIT) https://github.com/john-walks-slow/open-iching",
        "YAO_TEXTS: dict[str, tuple[str, str, str, str, str, str]] = {",
    ]
    for upper in range(8):
        for lower in range(8):
            name = HEXAGRAM_NAMES[upper][lower]
            texts = mapping[name]
            escaped = [t.replace("\\", "\\\\").replace('"', '\\"') for t in texts]
            inner = ", ".join(f'"{t}"' for t in escaped)
            lines_out.append(f'    "{name}": ({inner}),')
    lines_out.append("}")
    lines_out.append("")

    OUTPUT.write_text("\n".join(lines_out), encoding="utf-8")
    print(f"Wrote {len(mapping)} hexagrams -> {OUTPUT}")


if __name__ == "__main__":
    main()