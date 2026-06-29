"""GUI 主题工具测试。"""

import pytest

pytest.importorskip("tkinter")
import tkinter as tk

from bagua.gui_theme import bind_readonly_text


def test_bind_readonly_text_blocks_typing_allows_ctrl_c():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk 运行环境不可用")
    root.withdraw()
    text = tk.Text(root)
    bind_readonly_text(text)
    text.insert("1.0", "hello")
    assert text.bind("<Key>") is not None
    root.destroy()