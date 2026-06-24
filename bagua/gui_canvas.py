"""卦象 Canvas 绘制组件。"""

from __future__ import annotations

import tkinter as tk

from bagua.models import HexagramInfo

YANG_COLOR = "#2c3e50"
YIN_COLOR = "#7f8c8d"
CHANGE_COLOR = "#d35400"
BG_COLOR = "#fafafa"


class HexagramCanvas(tk.Canvas):
    """自下而上绘制六爻卦象。"""

    def __init__(self, master, width: int = 280, height: int = 220, **kwargs) -> None:
        super().__init__(
            master,
            width=width,
            height=height,
            bg=BG_COLOR,
            highlightthickness=1,
            highlightbackground="#dddddd",
            **kwargs,
        )
        self._w = width
        self._h = height

    def draw_hexagram(self, hexagram: HexagramInfo | None) -> None:
        self.delete("all")
        if hexagram is None:
            self.create_text(
                self._w // 2,
                self._h // 2,
                text="起卦后显示卦象",
                fill="#999999",
                font=("Microsoft YaHei UI", 10),
            )
            return

        margin_x = 36
        line_w = self._w - margin_x * 2
        gap = self._h / 7
        mid_gap = 18

        self.create_text(
            self._w // 2,
            12,
            text=hexagram.name,
            font=("Microsoft YaHei UI", 11, "bold"),
            fill="#8e44ad",
        )

        for i, yao in enumerate(hexagram.yaos):
            y = self._h - gap * (i + 1.2)
            color = YANG_COLOR if yao.is_yang else YIN_COLOR
            width = 4 if yao.is_yang else 3

            if yao.is_yang:
                self.create_line(
                    margin_x, y, margin_x + line_w, y, fill=color, width=width, capstyle=tk.ROUND
                )
            else:
                half = (line_w - mid_gap) / 2
                self.create_line(
                    margin_x, y, margin_x + half, y, fill=color, width=width, capstyle=tk.ROUND
                )
                self.create_line(
                    margin_x + half + mid_gap,
                    y,
                    margin_x + line_w,
                    y,
                    fill=color,
                    width=width,
                    capstyle=tk.ROUND,
                )

            if yao.is_changing:
                self.create_oval(
                    margin_x + line_w + 8,
                    y - 5,
                    margin_x + line_w + 18,
                    y + 5,
                    outline=CHANGE_COLOR,
                    width=2,
                )

        if hexagram.has_changing and hexagram.changed_hexagram:
            chg = hexagram.changed_hexagram
            self.create_text(
                self._w // 2,
                self._h - 6,
                text=f"之卦：{chg.name}",
                font=("Microsoft YaHei UI", 9),
                fill=CHANGE_COLOR,
            )