"""非交互 CLI 测试。"""

from bagua.args import parse_cli_args
from bagua.headless import run_export_record, run_export_records, run_headless_divination, run_list_records


def test_headless_random_output(capsys):
    args = parse_cli_args([
        "--method", "random",
        "--question", "测试",
        "--output", "prompt",
        "--no-copy",
    ])
    code = run_headless_divination(args)
    assert code == 0
    captured = capsys.readouterr()
    assert "用户问题" in captured.out
    assert "测试" in captured.out


def test_headless_list_empty(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("bagua.records.RECORDS_DIR", tmp_path / "records")
    code = run_list_records()
    assert code == 0
    assert "暂无" in capsys.readouterr().out


def test_headless_export_record(tmp_path, monkeypatch, capsys):
    from bagua.records import save_record
    from tests.test_records import _sample_record

    records_dir = tmp_path / "records"
    records_dir.mkdir()
    monkeypatch.setattr("bagua.records.RECORDS_DIR", records_dir)
    save_record(_sample_record())

    out = tmp_path / "one.md"
    code = run_export_record("1", output=str(out))
    assert code == 0
    assert out.exists()
    assert "已导出" in capsys.readouterr().out


def test_headless_export_records_with_search(tmp_path, monkeypatch, capsys):
    from bagua.records import save_record
    from tests.test_records import _sample_record

    records_dir = tmp_path / "records"
    records_dir.mkdir()
    monkeypatch.setattr("bagua.records.RECORDS_DIR", records_dir)
    save_record(_sample_record())

    out = tmp_path / "filtered.md"
    code = run_export_records(search="测试", output=str(out))
    assert code == 0
    assert out.exists()