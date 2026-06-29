"""历史记录管理测试。"""


from bagua.hexagram import build_hexagram
from bagua.models import DivinationRecord
from bagua.records import (
    delete_record,
    export_record_markdown,
    export_records_markdown,
    list_records,
    load_record_json,
    save_record,
    search_records,
)


def _sample_record() -> DivinationRecord:
    h = build_hexagram([7, 7, 7, 7, 7, 7])
    return DivinationRecord(
        question="测试",
        bazi="甲子",
        birth_datetime="1990-01-01",
        method="随机起卦",
        divination_time="2026-01-01 12:00:00",
        timezone="Asia/Shanghai",
        hexagram=h,
        prompt="prompt text",
    )


def test_save_and_list_records(tmp_path, monkeypatch):
    records_dir = tmp_path / "records"
    records_dir.mkdir()
    monkeypatch.setattr("bagua.records.RECORDS_DIR", records_dir)

    path = save_record(_sample_record())
    assert path.exists()

    items = list_records()
    assert len(items) == 1
    assert items[0].hexagram_name == "乾为天"
    assert items[0].question == "测试"


def test_load_and_delete_record(tmp_path, monkeypatch):
    records_dir = tmp_path / "records"
    records_dir.mkdir()
    monkeypatch.setattr("bagua.records.RECORDS_DIR", records_dir)

    path = save_record(_sample_record())
    data = load_record_json(path.name)
    assert data is not None
    assert data["prompt"] == "prompt text"

    deleted = delete_record("1")
    assert deleted is not None
    assert list_records() == []


def test_search_records_by_question(tmp_path, monkeypatch):
    records_dir = tmp_path / "records"
    records_dir.mkdir()
    monkeypatch.setattr("bagua.records.RECORDS_DIR", records_dir)

    save_record(_sample_record())
    assert search_records("测试") == list_records()
    assert search_records("不存在的关键词") == []


def test_export_record_markdown(tmp_path, monkeypatch):
    records_dir = tmp_path / "records"
    records_dir.mkdir()
    monkeypatch.setattr("bagua.records.RECORDS_DIR", records_dir)

    json_path = save_record(_sample_record())
    out = tmp_path / "out.md"
    exported = export_record_markdown(json_path.name, out)
    assert exported == out
    text = out.read_text(encoding="utf-8")
    assert "乾为天" in text
    assert "prompt text" in text


def test_export_records_markdown_batch(tmp_path, monkeypatch):
    records_dir = tmp_path / "records"
    records_dir.mkdir()
    monkeypatch.setattr("bagua.records.RECORDS_DIR", records_dir)

    save_record(_sample_record())
    out = tmp_path / "batch.md"
    exported = export_records_markdown(output_path=out)
    assert exported == out
    assert "共 1 条记录" in out.read_text(encoding="utf-8")