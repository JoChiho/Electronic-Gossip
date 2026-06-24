"""跨平台剪贴板复制（含 Windows 优化回退）。"""

from __future__ import annotations

import sys


def copy_to_clipboard(text: str) -> bool:
    """复制文本到系统剪贴板，成功返回 True。"""
    if not text:
        return False
    if sys.platform == "win32":
        if _copy_via_win32(text):
            return True
        if _copy_via_windows_clip(text):
            return True
    if _copy_via_tkinter(text):
        return True
    return False


def _copy_via_win32(text: str) -> bool:
    """Windows：通过 Win32 API 写入剪贴板（CLI 环境更稳定）。"""
    if sys.platform != "win32":
        return False
    try:
        import ctypes

        CF_UNICODETEXT = 13
        GMEM_MOVEABLE = 0x0002
        kernel32 = ctypes.windll.kernel32
        user32 = ctypes.windll.user32

        kernel32.GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]
        kernel32.GlobalAlloc.restype = ctypes.c_void_p
        kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
        kernel32.GlobalLock.restype = ctypes.c_void_p
        kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
        kernel32.GlobalFree.argtypes = [ctypes.c_void_p]
        user32.OpenClipboard.argtypes = [ctypes.c_void_p]
        user32.OpenClipboard.restype = ctypes.c_bool
        user32.EmptyClipboard.restype = ctypes.c_bool
        user32.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]
        user32.SetClipboardData.restype = ctypes.c_void_p
        user32.CloseClipboard.restype = ctypes.c_bool

        if not user32.OpenClipboard(None):
            return False
        try:
            user32.EmptyClipboard()
            encoded = text.encode("utf-16-le") + b"\x00\x00"
            h_global = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(encoded))
            if not h_global:
                return False
            p_global = kernel32.GlobalLock(h_global)
            if not p_global:
                kernel32.GlobalFree(h_global)
                return False
            ctypes.memmove(p_global, encoded, len(encoded))
            kernel32.GlobalUnlock(h_global)
            if not user32.SetClipboardData(CF_UNICODETEXT, h_global):
                kernel32.GlobalFree(h_global)
                return False
        finally:
            user32.CloseClipboard()
        return True
    except Exception:
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