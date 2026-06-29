"""GUI 视觉主题（深色雅致 · 易经风格）。"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from bagua.gui_dpi import scaled_font

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

FONT_FAMILY = "Microsoft YaHei UI"
FONT_MONO_FAMILY = "Consolas"

# 默认字号（96 DPI）；高 DPI 下由 apply_theme(scale=...) 覆盖
FONT_UI = (FONT_FAMILY, 10)
FONT_TITLE = (FONT_FAMILY, 18, "bold")
FONT_HEADER = (FONT_FAMILY, 22, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 9)
FONT_MONO = (FONT_MONO_FAMILY, 10)
FONT_SECTION = (FONT_FAMILY, 11, "bold")
FONT_ACCENT_BTN = (FONT_FAMILY, 11, "bold")
FONT_HEADER = (FONT_FAMILY, 22, "bold")
FONT_SYMBOL = ("Segoe UI Symbol", 18)
FONT_CANVAS_TITLE = (FONT_FAMILY, 12, "bold")
FONT_CANVAS_BODY = (FONT_FAMILY, 11)
FONT_CANVAS_HINT = (FONT_FAMILY, 9)
FONT_PROMPT = (FONT_MONO_FAMILY, 10)


def _build_fonts(scale: float = 1.0) -> dict[str, tuple]:
    return {
        "ui": scaled_font(FONT_FAMILY, 10, scale=scale),
        "title": scaled_font(FONT_FAMILY, 18, "bold", scale=scale),
        "header": scaled_font(FONT_FAMILY, 22, "bold", scale=scale),
        "subtitle": scaled_font(FONT_FAMILY, 9, scale=scale),
        "mono": scaled_font(FONT_MONO_FAMILY, 10, scale=scale),
        "section": scaled_font(FONT_FAMILY, 11, "bold", scale=scale),
        "accent_btn": scaled_font(FONT_FAMILY, 11, "bold", scale=scale),
        "canvas_title": scaled_font(FONT_FAMILY, 12, "bold", scale=scale),
        "canvas_body": scaled_font(FONT_FAMILY, 11, scale=scale),
        "canvas_hint": scaled_font(FONT_FAMILY, 9, scale=scale),
        "symbol": scaled_font("Segoe UI Symbol", 18, scale=scale),
        "prompt": scaled_font(FONT_MONO_FAMILY, 10, scale=scale),
    }


def apply_theme(root: tk.Tk, *, scale: float = 1.0) -> ttk.Style:
    global FONT_UI, FONT_TITLE, FONT_HEADER, FONT_SUBTITLE, FONT_MONO, FONT_SECTION
    global FONT_ACCENT_BTN, FONT_SYMBOL, FONT_CANVAS_TITLE, FONT_CANVAS_BODY, FONT_CANVAS_HINT
    global FONT_PROMPT

    fonts = _build_fonts(scale)
    FONT_UI = fonts["ui"]
    FONT_TITLE = fonts["title"]
    FONT_HEADER = fonts["header"]
    FONT_SUBTITLE = fonts["subtitle"]
    FONT_MONO = fonts["mono"]
    FONT_SECTION = fonts["section"]
    FONT_ACCENT_BTN = fonts["accent_btn"]
    FONT_SYMBOL = fonts["symbol"]
    FONT_CANVAS_TITLE = fonts["canvas_title"]
    FONT_CANVAS_BODY = fonts["canvas_body"]
    FONT_CANVAS_HINT = fonts["canvas_hint"]
    FONT_PROMPT = fonts["prompt"]

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
        padding=(4, 6),
    )
    style.configure(
        "TCombobox",
        fieldbackground=THEME["input_bg"],
        foreground=THEME["text"],
        arrowcolor=THEME["accent"],
        bordercolor=THEME["border"],
        padding=(4, 6),
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
        padding=(14, 8),
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
        font=FONT_ACCENT_BTN,
        padding=(22, 11),
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
        padding=(12, 7),
    )
    style.configure(
        "Toolbar.TFrame",
        background=THEME["surface_alt"],
    )
    style.configure(
        "PromptCard.TLabelframe",
        background=THEME["surface"],
        bordercolor=THEME["accent_dim"],
        relief="flat",
    )
    style.configure(
        "PromptCard.TLabelframe.Label",
        background=THEME["surface"],
        foreground=THEME["accent"],
        font=FONT_SECTION,
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


def bind_readonly_text(widget: tk.Text) -> None:
    """只读但允许选择与 Ctrl+C / Ctrl+A。"""

    def _on_key(event: tk.Event) -> str | None:
        ctrl = bool(event.state & 0x4)
        if ctrl and event.keysym.lower() in ("c", "a", "insert"):
            return None
        if event.keysym in (
            "Left", "Right", "Up", "Down", "Home", "End",
            "Prior", "Next", "Shift_L", "Shift_R", "Control_L", "Control_R",
        ):
            return None
        return "break"

    widget.bind("<Key>", _on_key)


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