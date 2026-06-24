"""领域数据模型。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from bagua.data import YAO_POSITIONS, YAO_VALUE_NAMES
from bagua.timezone import TimezoneInfo

DivinationMethod = Literal["coin", "time", "random"]
CoinMode = Literal["manual", "auto"]


@dataclass
class UserConfig:
    timezone: str = "Asia/Shanghai"
    region_label: str = "中国（北京时间 UTC+8）"
    question: str = ""
    bazi: str = ""
    birth_datetime: str = ""
    coin_mode: str = "manual"


@dataclass
class UserContext:
    question: str
    bazi: str
    birth_datetime: str
    tz: TimezoneInfo
    coin_mode: str


@dataclass
class YaoInfo:
    position: int
    value: int
    is_yang: bool
    is_changing: bool

    @property
    def label(self) -> str:
        return YAO_VALUE_NAMES[self.value]

    @property
    def position_name(self) -> str:
        return YAO_POSITIONS[self.position - 1]


@dataclass
class HexagramInfo:
    name: str
    upper_trigram: dict
    lower_trigram: dict
    yaos: list[YaoInfo]
    changing_positions: list[int] = field(default_factory=list)
    changed_hexagram: HexagramInfo | None = None

    @property
    def has_changing(self) -> bool:
        return bool(self.changing_positions)


@dataclass
class DivinationRecord:
    question: str
    bazi: str
    birth_datetime: str
    method: str
    divination_time: str
    timezone: str
    hexagram: HexagramInfo
    prompt: str


@dataclass
class DivinationResult:
    """起卦服务层统一返回结构。"""

    yao_values: list[int]
    hexagram: HexagramInfo
    method_desc: str
    divination_time: str
    prompt: str