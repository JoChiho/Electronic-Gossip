"""非交互模式与 config 偏好联动测试。"""

from bagua.args import parse_cli_args
from bagua.config import save_config
from bagua.headless import _should_copy, run_headless_divination
from bagua.models import UserConfig


def test_should_copy_respects_config_and_flags():
    cfg = UserConfig(auto_copy_prompt=True)
    args = parse_cli_args(["--method", "random"])
    assert _should_copy(args, cfg) is True

    args_no = parse_cli_args(["--method", "random", "--no-copy"])
    assert _should_copy(args_no, cfg) is False

    args_force = parse_cli_args(["--method", "random", "--copy"])
    assert _should_copy(args_force, cfg) is True


def test_headless_uses_saved_coin_tosses(tmp_path, monkeypatch, capsys):
    config_file = tmp_path / "config.json"
    monkeypatch.setattr("bagua.config.CONFIG_PATH", config_file)
    monkeypatch.setattr("bagua.config.BAGUA_DIR", tmp_path)

    save_config(
        UserConfig(
            coin_mode="manual",
            coin_tosses=[["1", "1", "1"], ["1", "2", "2"], ["2", "2", "2"], ["1", "2", "1"], ["2", "1", "1"], ["1", "1", "2"]],
            auto_copy_prompt=False,
        )
    )

    args = parse_cli_args(["--method", "coin", "--coin-mode", "manual", "--output", "prompt", "--no-copy"])
    code = run_headless_divination(args)
    assert code == 0
    assert "用户问题" in capsys.readouterr().out