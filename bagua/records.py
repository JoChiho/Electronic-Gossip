"""占卜历史记录管理。"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from bagua.config import RECORDS_DIR
from bagua.hexagram import hexagram_to_dict
from bagua.models import DivinationRecord

__all__ = [
    "RecordSummary",
    "delete_record",
    "list_records",
    "load_record_json",
    "save_record",
]


@dataclass
class RecordSummary:
    filename: str
    path: Path
    saved_at: str
    question: str
    method: str
    hexagram_name: str
    divination_time: str


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


def list_records() -> list[RecordSummary]:
    if not RECORDS_DIR.exists():
        return []
    summaries: list[RecordSummary] = []
    for path in sorted(RECORDS_DIR.glob("bagua_*.json"), reverse=True):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            hexagram = data.get("hexagram", {})
            summaries.append(
                RecordSummary(
                    filename=path.name,
                    path=path,
                    saved_at=data.get("saved_at", ""),
                    question=data.get("question", ""),
                    method=data.get("method", ""),
                    hexagram_name=hexagram.get("name", ""),
                    divination_time=data.get("divination_time", ""),
                )
            )
        except (json.JSONDecodeError, OSError):
            continue
    return summaries


def resolve_record_path(identifier: str) -> Path | None:
    """按文件名或序号（1-based）解析记录路径。"""
    if not identifier:
        return None
    if identifier.isdigit():
        records = list_records()
        idx = int(identifier)
        if 1 <= idx <= len(records):
            return records[idx - 1].path
        return None
    name = identifier if identifier.endswith(".json") else f"{identifier}.json"
    path = RECORDS_DIR / name
    return path if path.exists() else None


def load_record_json(identifier: str) -> dict | None:
    path = resolve_record_path(identifier)
    if path is None:
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def delete_record(identifier: str) -> Path | None:
    path = resolve_record_path(identifier)
    if path is None:
        return None
    path.unlink(missing_ok=True)
    return path