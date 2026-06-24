"""用户配置持久化。"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from bagua.models import UserConfig

BAGUA_DIR = Path.home() / ".bagua"
CONFIG_PATH = BAGUA_DIR / "config.json"
RECORDS_DIR = BAGUA_DIR / "records"


def load_config() -> UserConfig:
    if not CONFIG_PATH.exists():
        return UserConfig()
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        known = {f.name for f in UserConfig.__dataclass_fields__.values()}
        return UserConfig(**{k: v for k, v in data.items() if k in known})
    except (json.JSONDecodeError, TypeError):
        return UserConfig()


def save_config(config: UserConfig) -> None:
    BAGUA_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(
        json.dumps(asdict(config), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# 向后兼容：记录保存已迁至 records 模块
from bagua.records import save_record as save_record  # noqa: E402, F401