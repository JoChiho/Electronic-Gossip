"""CLI 引导模块测试。"""

from bagua.cli_guide import METHOD_LABELS, show_quick_start, show_step


def test_method_labels_complete():
    assert set(METHOD_LABELS) == {"coin", "time", "random"}


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