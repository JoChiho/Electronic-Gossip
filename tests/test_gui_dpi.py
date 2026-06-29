"""GUI DPI 辅助测试。"""

from bagua.gui_dpi import detect_ui_scale, enable_windows_dpi_awareness, scaled_font


def test_enable_dpi_does_not_raise():
    enable_windows_dpi_awareness()


def test_scaled_font_minimum_size():
    assert scaled_font("Microsoft YaHei UI", 10, scale=2.0)[1] >= 8


def test_detect_ui_scale_with_tk():
    import tkinter as tk

    from bagua.gui_dpi import enable_windows_dpi_awareness

    enable_windows_dpi_awareness()
    root = tk.Tk()
    root.withdraw()
    try:
        scale = detect_ui_scale(root)
        assert scale >= 1.0
    finally:
        root.destroy()