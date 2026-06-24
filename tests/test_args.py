"""CLI 参数解析测试。"""

from bagua.args import parse_cli_args


def test_default_interactive():
    args = parse_cli_args([])
    assert args.interactive is True
    assert args.method is None


def test_headless_random():
    args = parse_cli_args(["--method", "random", "-q", "工作"])
    assert args.interactive is False
    assert args.method == "random"
    assert args.question == "工作"


def test_list_records_flag():
    args = parse_cli_args(["--list-records"])
    assert args.interactive is False
    assert args.list_records is True


def test_force_interactive():
    args = parse_cli_args(["--method", "random", "--interactive"])
    assert args.interactive is True