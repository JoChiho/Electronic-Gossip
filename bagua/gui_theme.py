"""GUI 视觉主题（深色雅致 · 易经风格）。"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

THEME = {
    "bg": "#141820",
    "surface": "#1e2430",
    "surface_alt": "#252d3d",
    "border": "#3a4458",
    "text": "#e8e4dc",
    "text_muted": "#9aa3b2",
    "accent": "#c9a227",
    "accent_hover": "#dbb84a",
    "accent_dim": "#8a7420",
    "success": "#5cb87a",
    "danger": "#d45d5d",
    "input_bg": "#2a3242",
    "header_from": "#1a2030",
    "header_to": "#252d42",
}

FONT_UI = ("Microsoft YaHei UI", 10)
FONT_TITLE = ("Microsoft YaHei UI", 18, "bold")
FONT_SUBTITLE = ("Microsoft YaHei UI", 9)
FONT_MONO = ("Consolas", 10)
FONT_SECTION = ("Microsoft YaHei UI", 11, "bold")


def apply_theme(root: tk.Tk) -> ttk.Style:
    root.configure(bg=THEME["bg"])
    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")

    style.configure(".", background=THEME["bg"], foreground=THEME["text"], font=FONT_UI)
    style.configure("TFrame", background=THEME["bg"])
    style.configure("Card.TFrame", background=THEME["surface"])
    style.configure("Surface.TFrame", background=THEME["surface_alt"])

    style.configure(
        "Title.TLabel",
        background=THEME["header_to"],
        foreground=THEME["accent"],
        font=FONT_TITLE,
    )
    style.configure(
        "Subtitle.TLabel",
        background=THEME["header_to"],
        foreground=THEME["text_muted"],
        font=FONT_SUBTITLE,
    )
    style.configure(
        "Muted.TLabel",
        background=THEME["surface"],
        foreground=THEME["text_muted"],
        font=FONT_SUBTITLE,
    )
    style.configure(
        "Field.TLabel",
        background=THEME["surface"],
        foreground=THEME["text"],
        font=FONT_UI,
    )
    style.configure(
        "Section.TLabelframe",
        background=THEME["surface"],
        bordercolor=THEME["border"],
        relief="flat",
    )
    style.configure(
        "Section.TLabelframe.Label",
        background=THEME["surface"],
        foreground=THEME["accent"],
        font=FONT_SECTION,
    )
    style.configure(
        "TEntry",
        fieldbackground=THEME["input_bg"],
        foreground=THEME["text"],
        insertcolor=THEME["text"],
        bordercolor=THEME["border"],
        lightcolor=THEME["border"],
        darkcolor=THEME["border"],
    )
    style.configure(
        "TCombobox",
        fieldbackground=THEME["input_bg"],
        foreground=THEME["text"],
        arrowcolor=THEME["accent"],
        bordercolor=THEME["border"],
    )
    style.map("TCombobox", fieldbackground=[("readonly", THEME["input_bg"])])
    style.configure(
        "TRadiobutton",
        background=THEME["surface"],
        foreground=THEME["text"],
    )
    style.map(
        "TRadiobutton",
        background=[("active", THEME["surface"])],
        foreground=[("active", THEME["accent"])],
    )
    style.configure(
        "TCheckbutton",
        background=THEME["surface"],
        foreground=THEME["text"],
    )
    style.configure(
        "TButton",
        background=THEME["surface_alt"],
        foreground=THEME["text"],
        bordercolor=THEME["border"],
        padding=(12, 7),
    )
    style.map(
        "TButton",
        background=[("active", THEME["border"])],
        foreground=[("active", THEME["text"])],
    )
    style.configure(
        "Accent.TButton",
        background=THEME["accent_dim"],
        foreground=THEME["text"],
        font=("Microsoft YaHei UI", 11, "bold"),
        padding=(20, 10),
    )
    style.map(
        "Accent.TButton",
        background=[("active", THEME["accent"])],
        foreground=[("active", THEME["bg"])],
    )
    style.configure(
        "Ghost.TButton",
        background=THEME["surface"],
        foreground=THEME["text_muted"],
        padding=(10, 6),
    )
    style.configure(
        "Status.TLabel",
        background=THEME["surface_alt"],
        foreground=THEME["text_muted"],
        font=FONT_SUBTITLE,
        padding=(10, 6),
    )
    style.configure(
        "Vertical.TScrollbar",
        background=THEME["surface_alt"],
        troughcolor=THEME["bg"],
        bordercolor=THEME["bg"],
        arrowcolor=THEME["accent"],
    )
    return style


def style_text_widget(widget: tk.Text, *, readonly: bool = False) -> None:
    widget.configure(
        bg=THEME["input_bg"],
        fg=THEME["text"],
        insertbackground=THEME["text"],
        selectbackground=THEME["accent_dim"],
        selectforeground=THEME["text"],
        relief="flat",
        highlightthickness=1,
        highlightbackground=THEME["border"],
        highlightcolor=THEME["accent"],
    )
    if readonly:
        widget.configure(state=tk.DISABLED)