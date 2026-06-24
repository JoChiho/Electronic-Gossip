"""卦象构建纯逻辑。"""

from __future__ import annotations

from bagua.data import HEXAGRAM_NAMES, TRIGRAMS
from bagua.models import HexagramInfo, YaoInfo


def _lines_to_trigram(lines: tuple[int, int, int]) -> dict:
    for tri in TRIGRAMS:
        if tri["lines"] == lines:
            return tri
    raise ValueError(f"无效三爻: {lines}")


def _yao_value_to_line(value: int) -> tuple[bool, bool]:
    if value == 6:
        return False, True
    if value == 7:
        return True, False
    if value == 8:
        return False, False
    if value == 9:
        return True, True
    raise ValueError(f"无效爻值: {value}")


def build_hexagram(yao_values: list[int]) -> HexagramInfo:
    if len(yao_values) != 6:
        raise ValueError("需要恰好六个爻值")

    yaos: list[YaoInfo] = []
    binary: list[int] = []
    changing: list[int] = []

    for i, val in enumerate(yao_values, start=1):
        is_yang, is_changing = _yao_value_to_line(val)
        yaos.append(YaoInfo(position=i, value=val, is_yang=is_yang, is_changing=is_changing))
        binary.append(1 if is_yang else 0)
        if is_changing:
            changing.append(i)

    lower = _lines_to_trigram(tuple(binary[0:3]))
    upper = _lines_to_trigram(tuple(binary[3:6]))
    name = HEXAGRAM_NAMES[TRIGRAMS.index(upper)][TRIGRAMS.index(lower)]

    hexagram = HexagramInfo(
        name=name,
        upper_trigram=upper,
        lower_trigram=lower,
        yaos=yaos,
        changing_positions=changing,
    )

    if changing:
        changed_binary = []
        for y in yaos:
            if y.is_changing:
                changed_binary.append(0 if y.is_yang else 1)
            else:
                changed_binary.append(1 if y.is_yang else 0)
        changed_lower = _lines_to_trigram(tuple(changed_binary[0:3]))
        changed_upper = _lines_to_trigram(tuple(changed_binary[3:6]))
        changed_name = HEXAGRAM_NAMES[TRIGRAMS.index(changed_upper)][TRIGRAMS.index(changed_lower)]
        hexagram.changed_hexagram = HexagramInfo(
            name=changed_name,
            upper_trigram=changed_upper,
            lower_trigram=changed_lower,
            yaos=yaos,
            changing_positions=[],
        )

    return hexagram


def hexagram_to_dict(hexagram: HexagramInfo) -> dict:
    data = {
        "name": hexagram.name,
        "upper_trigram": hexagram.upper_trigram["name"],
        "lower_trigram": hexagram.lower_trigram["name"],
        "changing_positions": hexagram.changing_positions,
        "yaos": [
            {
                "position": y.position,
                "value": y.value,
                "label": y.label,
                "is_yang": y.is_yang,
                "is_changing": y.is_changing,
            }
            for y in hexagram.yaos
        ],
    }
    if hexagram.changed_hexagram:
        data["changed_hexagram"] = {
            "name": hexagram.changed_hexagram.name,
            "upper_trigram": hexagram.changed_hexagram.upper_trigram["name"],
            "lower_trigram": hexagram.changed_hexagram.lower_trigram["name"],
        }
    return data