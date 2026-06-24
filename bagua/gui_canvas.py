"""卦象 Canvas 绘制组件。"""

from __future__ import annotations

import tkinter as tk

from bagua.gui_theme import THEME
from bagua.models import HexagramInfo

YANG_COLOR = THEME["accent"]
YIN_COLOR = THEME["text_muted"]
CHANGE_COLOR = "#e07b54"
BG_COLOR = THEME["surface_alt"]
BORDER_COLOR = THEME["border"]
TITLE_COLOR = THEME["accent"]


class HexagramCanvas(tk.Canvas):
    """自下而上绘制六爻卦象。"""

    def __init__(self, master, width: int = 280, height: int = 240, **kwargs) -> None:
        super().__init__(
            master,
            width=width,
            height=height,
            bg=BG_COLOR,
            highlightthickness=1,
            highlightbackground=BORDER_COLOR,
            **kwargs,
        )
        self._canvas_w = width
        self._canvas_h = height

    def draw_hexagram(self, hexagram: HexagramInfo | None) -> None:
        self.delete("all")
        self.create_rectangle(
            2, 2, self._canvas_w - 2, self._canvas_h - 2,
            outline=BORDER_COLOR, width=1,
        )
        if hexagram is None:
            self.create_text(
                self._canvas_w // 2,
                self._canvas_h // 2,
                text="☯  起卦后显示卦象",
                fill=THEME["text_muted"],
                font=("Microsoft YaHei UI", 11),
            )
            return

        margin_x = 36
        line_w = self._canvas_w - margin_x * 2
        gap = self._canvas_h / 7
        mid_gap = 18

        self.create_text(
            self._canvas_w // 2,
            16,
            text=hexagram.name,
            font=("Microsoft YaHei UI", 12, "bold"),
            fill=TITLE_COLOR,
        )

        for i, yao in enumerate(hexagram.yaos):
            y = self._canvas_h - gap * (i + 1.2)
            color = YANG_COLOR if yao.is_yang else YIN_COLOR
            line_width = 4 if yao.is_yang else 3

            if yao.is_yang:
                self.create_line(
                    margin_x, y, margin_x + line_w, y,
                    fill=color, width=line_width, capstyle=tk.ROUND,
                )
            else:
                half = (line_w - mid_gap) / 2
                self.create_line(
                    margin_x, y, margin_x + half, y,
                    fill=color, width=line_width, capstyle=tk.ROUND,
                )
                self.create_line(
                    margin_x + half + mid_gap, y, margin_x + line_w, y,
                    fill=color, width=line_width, capstyle=tk.ROUND,
                )

            if yao.is_changing:
                self.create_oval(
                    margin_x + line_w + 8, y - 5,
                    margin_x + line_w + 18, y + 5,
                    outline=CHANGE_COLOR, width=2,
                )

        if hexagram.has_changing and hexagram.changed_hexagram:
            chg = hexagram.changed_hexagram
            self.create_text(
                self._canvas_w // 2,
                self._canvas_h - 8,
                text=f"之卦 · {chg.name}",
                font=("Microsoft YaHei UI", 9),
                fill=CHANGE_COLOR,
            )