"""GUI 偏好设置对话框。"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import TYPE_CHECKING

from bagua.config import save_config
from bagua.gui_theme import FONT_UI, THEME
from bagua.true_solar import default_longitude

if TYPE_CHECKING:
    from bagua.gui_app import BaguaGuiApp


def show_settings_dialog(app: BaguaGuiApp) -> None:
    win = tk.Toplevel(app)
    win.title("偏好设置")
    win.configure(bg=THEME["bg"])
    win.geometry("480x460")
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
    true_solar_birth_var = tk.BooleanVar(value=app._config.use_true_solar_birth)
    true_solar_div_var = tk.BooleanVar(value=app._config.use_true_solar_divination)

    ttk.Checkbutton(frame, text="自动排八字（出生时间已填且八字为空时）", variable=auto_bazi_var).pack(
        anchor=tk.W, pady=4
    )
    ttk.Checkbutton(frame, text="起卦后自动复制 AI 提示词到剪贴板", variable=auto_copy_var).pack(
        anchor=tk.W, pady=4
    )
    ttk.Checkbutton(frame, text="AI 提示词附带卦辞摘要", variable=hex_text_var).pack(
        anchor=tk.W, pady=4
    )

    ttk.Label(frame, text="真太阳时", style="Field.TLabel").pack(anchor=tk.W, pady=(10, 4))
    ttk.Checkbutton(
        frame,
        text="八字排盘使用出生地真太阳时（仅影响八字，不影响卦象演算）",
        variable=true_solar_birth_var,
    ).pack(anchor=tk.W, pady=2)
    ttk.Checkbutton(
        frame,
        text="时间起卦使用起卦地真太阳时 + 节气历换算",
        variable=true_solar_div_var,
    ).pack(anchor=tk.W, pady=2)

    def _lon_row(parent: ttk.Frame, label: str, var: tk.StringVar, preset: float) -> None:
        row = ttk.Frame(parent)
        row.pack(fill=tk.X, pady=4)
        ttk.Label(row, text=label, style="Field.TLabel", width=16).pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=var, width=10).pack(side=tk.LEFT)
        ttk.Label(row, text=f"留空默认 {preset:.1f}°", style="Muted.TLabel").pack(side=tk.LEFT, padx=(8, 0))

    birth_lon_var = tk.StringVar(
        value="" if app._config.birth_longitude is None else f"{app._config.birth_longitude:.2f}",
    )
    div_lon_var = tk.StringVar(
        value=(
            ""
            if app._config.divination_longitude is None
            else f"{app._config.divination_longitude:.2f}"
        ),
    )
    _lon_row(frame, "出生经度（东经°）", birth_lon_var, default_longitude(app._config.timezone))
    div_iana = app._config.divination_timezone or app._config.timezone
    _lon_row(frame, "起卦经度（东经°）", div_lon_var, default_longitude(div_iana))

    ttk.Label(
        frame,
        text="出生时区与起卦时区在表单中分别设置；经度请填所在地，勿混用。",
        style="Muted.TLabel",
        wraplength=420,
        font=FONT_UI,
    ).pack(anchor=tk.W, pady=(12, 0))

    btn_row = ttk.Frame(frame)
    btn_row.pack(fill=tk.X, pady=(20, 0))

    def _parse_longitude(raw: str) -> float | None:
        raw = raw.strip()
        if not raw:
            return None
        try:
            return float(raw)
        except ValueError:
            return None

    def _save() -> None:
        birth_lon = _parse_longitude(birth_lon_var.get())
        div_lon = _parse_longitude(div_lon_var.get())
        if birth_lon_var.get().strip() and birth_lon is None:
            messagebox.showerror("输入错误", "出生经度请填写数字")
            return
        if div_lon_var.get().strip() and div_lon is None:
            messagebox.showerror("输入错误", "起卦经度请填写数字")
            return
        app._config.auto_bazi = auto_bazi_var.get()
        app._config.auto_copy_prompt = auto_copy_var.get()
        app._config.include_hexagram_texts = hex_text_var.get()
        app._config.use_true_solar_birth = true_solar_birth_var.get()
        app._config.use_true_solar_divination = true_solar_div_var.get()
        app._config.birth_longitude = birth_lon
        app._config.divination_longitude = div_lon
        app._persist_config_from_form()
        save_config(app._config)
        app.status_var.set("偏好设置已保存")
        win.destroy()

    ttk.Button(btn_row, text="保存", style="Accent.TButton", command=_save).pack(side=tk.RIGHT)
    ttk.Button(btn_row, text="取消", command=win.destroy).pack(side=tk.RIGHT, padx=(0, 8))