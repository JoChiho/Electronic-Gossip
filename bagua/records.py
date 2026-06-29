"""占卜历史记录管理。"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from bagua.config import RECORDS_DIR
from bagua.hexagram import hexagram_to_dict
from bagua.models import DivinationRecord
from bagua.record_markdown import record_to_markdown, records_to_markdown

__all__ = [
    "RecordSummary",
    "delete_record",
    "export_record_markdown",
    "export_records_markdown",
    "list_records",
    "load_record_json",
    "save_record",
    "search_records",
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


def _text_matches(haystack: str, needle: str) -> bool:
    return needle.casefold() in haystack.casefold()


def summary_matches_query(summary: RecordSummary, query: str) -> bool:
    q = query.strip()
    if not q:
        return True
    for value in (
        summary.filename,
        summary.saved_at,
        summary.question,
        summary.method,
        summary.hexagram_name,
        summary.divination_time,
    ):
        if _text_matches(str(value), q):
            return True
    return False


def data_matches_query(data: dict, query: str) -> bool:
    q = query.strip()
    if not q:
        return True
    for key in (
        "question",
        "method",
        "bazi",
        "birth_datetime",
        "divination_time",
        "prompt",
        "timezone",
        "saved_at",
    ):
        if _text_matches(str(data.get(key, "")), q):
            return True
    hexagram = data.get("hexagram") or {}
    if _text_matches(str(hexagram.get("name", "")), q):
        return True
    return False


def search_records(query: str) -> list[RecordSummary]:
    """按关键词搜索记录（问题、卦名、方法、八字、提示词等）。"""
    q = query.strip()
    if not q:
        return list_records()
    results: list[RecordSummary] = []
    for rec in list_records():
        if summary_matches_query(rec, q):
            results.append(rec)
            continue
        data = load_record_json(rec.filename)
        if data and data_matches_query(data, q):
            results.append(rec)
    return results


def _summaries_for_export(
    *,
    query: str | None = None,
    identifiers: list[str] | None = None,
) -> list[RecordSummary]:
    if identifiers:
        summaries: list[RecordSummary] = []
        all_records = {r.filename: r for r in list_records()}
        for ident in identifiers:
            path = resolve_record_path(ident)
            if path is None:
                continue
            rec = all_records.get(path.name)
            if rec is not None:
                summaries.append(rec)
        return summaries
    if query and query.strip():
        return search_records(query)
    return list_records()


def export_record_markdown(
    identifier: str,
    output_path: Path | None = None,
) -> Path | None:
    """导出单条记录为 Markdown 文件。"""
    path = resolve_record_path(identifier)
    if path is None:
        return None
    data = load_record_json(identifier)
    if data is None:
        return None
    out = output_path or path.with_suffix(".md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(record_to_markdown(data), encoding="utf-8")
    return out


def export_records_markdown(
    *,
    query: str | None = None,
    identifiers: list[str] | None = None,
    output_path: Path | None = None,
) -> Path | None:
    """批量导出记录为 Markdown；无记录时返回 None。"""
    summaries = _summaries_for_export(query=query, identifiers=identifiers)
    if not summaries:
        return None
    payload: list[dict] = []
    for rec in summaries:
        data = load_record_json(rec.filename)
        if data:
            payload.append(data)
    if not payload:
        return None
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = output_path or (RECORDS_DIR / f"bagua_export_{ts}.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(records_to_markdown(payload), encoding="utf-8")
    return out