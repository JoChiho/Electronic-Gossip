"""非交互 CLI 测试。"""

from bagua.args import parse_cli_args
from bagua.headless import run_headless_divination, run_list_records


def test_headless_random_output(capsys):
    args = parse_cli_args([
        "--method", "random",
        "--question", "测试",
        "--output", "prompt",
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