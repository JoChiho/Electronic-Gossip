"""跨平台剪贴板复制（含 Windows 优化回退）。"""

from __future__ import annotations

import sys


def copy_to_clipboard(text: str) -> bool:
    """复制文本到系统剪贴板，成功返回 True。"""
    if not text:
        return False
    if _copy_via_tkinter(text):
        return True
    if sys.platform == "win32" and _copy_via_windows_clip(text):
        return True
    return False


def _copy_via_tkinter(text: str) -> bool:
    try:
        import tkinter as tk

        root = tk.Tk()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update_idletasks()
        root.update()
        root.destroy()
        return True
    except Exception:
        return False


def _copy_via_windows_clip(text: str) -> bool:
    """Windows：通过 clip 命令写入剪贴板。"""
    try:
        import subprocess

        proc = subprocess.run(
            ["clip"],
            input=text,
            text=True,
            encoding="utf-8",
            check=True,
            capture_output=True,
        )
        return proc.returncode == 0
    except Exception:
        return False