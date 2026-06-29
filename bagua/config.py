"""用户配置持久化。"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from bagua.models import UserConfig, UserContext
from bagua.timezone import get_timezone, label_for_timezone

BAGUA_DIR = Path.home() / ".bagua"
CONFIG_PATH = BAGUA_DIR / "config.json"
RECORDS_DIR = BAGUA_DIR / "records"


def normalize_config_data(data: dict) -> dict:
    """旧版 config 字段迁移。"""
    data = dict(data)
    if data.get("longitude") is not None and data.get("divination_longitude") is None:
        data["divination_longitude"] = data["longitude"]
    if "use_true_solar" in data:
        data.setdefault("use_true_solar_divination", data["use_true_solar"])
        data.setdefault("use_true_solar_birth", data["use_true_solar"])
    data.pop("longitude", None)
    data.pop("use_true_solar", None)
    data.setdefault("divination_timezone", data.get("timezone", "Asia/Shanghai"))
    data.setdefault("divination_region_label", data.get("region_label", ""))
    return data


def get_birth_timezone(config: UserConfig):
    return get_timezone(config.timezone, config.region_label)


def get_divination_timezone(config: UserConfig):
    iana = config.divination_timezone or config.timezone
    label = config.divination_region_label or config.region_label
    return get_timezone(iana, label)


def build_user_context(
    config: UserConfig,
    *,
    question: str | None = None,
    bazi: str | None = None,
    birth_datetime: str | None = None,
    coin_mode: str | None = None,
    calendar_mode: str | None = None,
    lunar_input: str | None = None,
) -> UserContext:
    return UserContext(
        question=question if question is not None else config.question,
        bazi=bazi if bazi is not None else config.bazi,
        birth_datetime=(
            birth_datetime if birth_datetime is not None else config.birth_datetime
        ),
        birth_tz=get_birth_timezone(config),
        divination_tz=get_divination_timezone(config),
        coin_mode=coin_mode if coin_mode is not None else config.coin_mode,
        calendar_mode=calendar_mode if calendar_mode is not None else config.calendar_mode,
        lunar_input=lunar_input,
        include_hexagram_texts=config.include_hexagram_texts,
        birth_longitude=config.birth_longitude,
        divination_longitude=config.divination_longitude,
        use_true_solar_birth=config.use_true_solar_birth,
        use_true_solar_divination=config.use_true_solar_divination,
    )


def load_config() -> UserConfig:
    if not CONFIG_PATH.exists():
        return UserConfig()
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        data = normalize_config_data(data)
        known = {f.name for f in UserConfig.__dataclass_fields__.values()}
        cfg = UserConfig(**{k: v for k, v in data.items() if k in known})
        if not cfg.divination_timezone:
            cfg.divination_timezone = cfg.timezone
        if not cfg.divination_region_label:
            cfg.divination_region_label = cfg.region_label
        return cfg
    except (json.JSONDecodeError, TypeError):
        return UserConfig()


def save_config(config: UserConfig) -> None:
    BAGUA_DIR.mkdir(parents=True, exist_ok=True)
    if not config.divination_timezone:
        config.divination_timezone = config.timezone
    if not config.divination_region_label:
        config.divination_region_label = config.region_label
    CONFIG_PATH.write_text(
        json.dumps(asdict(config), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def sync_divination_timezone_labels(config: UserConfig) -> None:
    if config.divination_timezone and not config.divination_region_label:
        config.divination_region_label = label_for_timezone(config.divination_timezone)


# 向后兼容：记录保存已迁至 records 模块
from bagua.records import save_record as save_record  # noqa: E402, F401