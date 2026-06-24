"""用户配置与占卜记录持久化。"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from bagua.hexagram import hexagram_to_dict
from bagua.models import DivinationRecord, UserConfig

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


def save_record(record: DivinationRecord) -> Path:
    RECORDS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = RECORDS_DIR / f"bagua_{ts}.json"
    payload = {
        "question": record.question,
        "bazi": record.bazi,
        "birth_datetime": record.birth_datetime,
        "method": record.method,
        "divination_time": record.divination_time,
        "timezone": record.timezone,
        "hexagram": hexagram_to_dict(record.hexagram),
        "prompt": record.prompt,
        "saved_at": datetime.now().isoformat(timespec="seconds"),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path