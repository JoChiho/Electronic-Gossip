"""GUI Canvas 组件测试。"""

import pytest

pytest.importorskip("tkinter")
import tkinter as tk
from tkinter import ttk

from bagua.gui_canvas import HexagramCanvas
from bagua.hexagram import build_hexagram


def test_hexagram_canvas_pack_does_not_break_tk_path():
    """回归：不得覆盖 Widget._w（Tcl 窗口路径），否则 pack 会失败。"""
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk 运行环境不可用（无 DISPLAY）")
    try:
        row = ttk.Frame(root)
        canvas = HexagramCanvas(row, width=280, height=220)
        assert isinstance(canvas._w, str)
        canvas.pack(side=tk.LEFT, padx=(0, 12))
        canvas.draw_hexagram(build_hexagram([7, 7, 7, 7, 7, 7]))
        assert canvas._canvas_w == 280
    finally:
        root.destroy()