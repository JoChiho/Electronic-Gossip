"""GUI 偏好设置对话框。"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

from bagua.config import save_config
from bagua.gui_theme import THEME

if TYPE_CHECKING:
    from bagua.gui_app import BaguaGuiApp


def show_settings_dialog(app: BaguaGuiApp) -> None:
    win = tk.Toplevel(app)
    win.title("偏好设置")
    win.configure(bg=THEME["bg"])
    win.geometry("480x320")
    win.resizable(False, False)
    win.transient(app)
    win.grab_set()

    frame = ttk.Frame(win, padding=16)
    frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(
        frame,
        text="以下选项对 CLI 与 GUI 均生效（保存至 ~/.bagua/config.json）",
        style="Muted.TLabel",
        wraplength=420,
    ).pack(anchor=tk.W, pady=(0, 12))

    auto_bazi_var = tk.BooleanVar(value=app._config.auto_bazi)
    auto_copy_var = tk.BooleanVar(value=app._config.auto_copy_prompt)
    hex_text_var = tk.BooleanVar(value=app._config.include_hexagram_texts)

    ttk.Checkbutton(frame, text="自动排八字（出生时间已填且八字为空时）", variable=auto_bazi_var).pack(
        anchor=tk.W, pady=4
    )
    ttk.Checkbutton(frame, text="起卦后自动复制 AI 提示词到剪贴板", variable=auto_copy_var).pack(
        anchor=tk.W, pady=4
    )
    ttk.Checkbutton(frame, text="AI 提示词附带卦辞摘要与爻辞全文", variable=hex_text_var).pack(
        anchor=tk.W, pady=4
    )

    ttk.Label(
        frame,
        text="出生地点、起卦地点与真太阳时开关请在主界面表单中设置。",
        style="Muted.TLabel",
        wraplength=420,
    ).pack(anchor=tk.W, pady=(16, 0))

    btn_row = ttk.Frame(frame)
    btn_row.pack(fill=tk.X, pady=(24, 0))

    def _save() -> None:
        app._config.auto_bazi = auto_bazi_var.get()
        app._config.auto_copy_prompt = auto_copy_var.get()
        app._config.include_hexagram_texts = hex_text_var.get()
        app._persist_config_from_form()
        save_config(app._config)
        app.status_var.set("偏好设置已保存")
        win.destroy()

    ttk.Button(btn_row, text="保存", style="Accent.TButton", command=_save).pack(side=tk.RIGHT)
    ttk.Button(btn_row, text="取消", command=win.destroy).pack(side=tk.RIGHT, padx=(0, 8))