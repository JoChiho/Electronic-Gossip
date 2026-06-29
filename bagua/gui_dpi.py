"""Windows 高 DPI 适配（须在创建 Tk 窗口之前调用 enable）。"""

from __future__ import annotations

import sys
import tkinter as tk


def enable_windows_dpi_awareness() -> None:
    """声明进程 DPI 感知，避免系统位图放大导致文字/按钮锯齿模糊。"""
    if sys.platform != "win32":
        return
    try:
        import ctypes

        # 2 = Per-Monitor DPI Aware (V2 效果，Win10 1703+)
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except (AttributeError, OSError):
        try:
            import ctypes

            ctypes.windll.user32.SetProcessDPIAware()
        except (AttributeError, OSError):
            pass


def detect_ui_scale(root: tk.Tk) -> float:
    """根据屏幕 DPI 估算 UI 缩放系数（96 DPI = 1.0）。"""
    try:
        px_per_inch = float(root.winfo_fpixels("1i"))
        if px_per_inch <= 0:
            return 1.0
        return max(1.0, round(px_per_inch / 96.0, 2))
    except tk.TclError:
        return 1.0


def configure_root_dpi(root: tk.Tk) -> float:
    """
    在根窗口创建后配置 Tk scaling，使控件按 DPI 清晰渲染。

    Returns:
        建议用于字号的缩放系数
    """
    scale = detect_ui_scale(root)
    if sys.platform == "win32" and abs(scale - 1.0) > 0.05:
        try:
            root.tk.call("tk", "scaling", scale)
        except tk.TclError:
            pass
    return scale


def scaled_font(
    family: str,
    size: int,
    *styles: str,
    scale: float = 1.0,
) -> tuple[str, int] | tuple[str, int, str]:
    """按 DPI 缩放字号，保证高分辨率屏上可读且清晰。"""
    scaled_size = max(8, int(round(size * scale)))
    if styles:
        return (family, scaled_size, *styles)
    return (family, scaled_size)