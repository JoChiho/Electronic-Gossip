"""CLI 引导模块测试。"""

from bagua.cli_guide import METHOD_LABELS, show_method_guide, show_quick_start, show_step


def test_method_labels_complete():
    assert set(METHOD_LABELS) == {"coin", "time", "random", "number"}


def test_show_quick_start_runs(capsys):
    from rich.console import Console

    c = Console(force_terminal=False, width=120)
    show_quick_start(c, first_run=True)
    out = capsys.readouterr().out
    assert "使用引导" in out or "流程" in out


def test_show_step_runs(capsys):
    from rich.console import Console

    c = Console(force_terminal=False, width=120)
    show_step(c, 1, "测试")
    assert "步骤 1" in capsys.readouterr().out


def test_show_method_guide_no_table(capsys):
    from rich.console import Console

    c = Console(force_terminal=False, width=40, soft_wrap=True)
    show_method_guide(c)
    out = capsys.readouterr().out
    assert "起卦方式说明" in out
    assert "铜钱法" in out
    assert "时间起卦" in out
    assert "随机起卦" in out