"""卦象 Canvas 绘制组件。"""

from __future__ import annotations

import tkinter as tk

from bagua.gui_theme import FONT_CANVAS_BODY, FONT_CANVAS_HINT, FONT_CANVAS_TITLE, THEME
from bagua.models import HexagramInfo

YANG_COLOR = THEME["accent"]
YIN_COLOR = THEME["text_muted"]
CHANGE_COLOR = "#e07b54"
BG_COLOR = THEME["surface_alt"]
BORDER_COLOR = THEME["border"]
TITLE_COLOR = THEME["accent"]


class HexagramCanvas(tk.Canvas):
    """自下而上绘制六爻卦象。"""

    def __init__(
        self,
        master,
        width: int = 280,
        height: int = 240,
        *,
        ui_scale: float = 1.0,
        **kwargs,
    ) -> None:
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
        self._ui_scale = ui_scale

    def draw_hexagram(self, hexagram: HexagramInfo | None) -> None:
        self.delete("all")
        border_w = max(1, int(round(self._ui_scale)))
        self.create_rectangle(
            2, 2, self._canvas_w - 2, self._canvas_h - 2,
            outline=BORDER_COLOR, width=border_w,
        )
        if hexagram is None:
            self.create_text(
                self._canvas_w // 2,
                self._canvas_h // 2,
                text="☯  起卦后显示卦象",
                fill=THEME["text_muted"],
                font=FONT_CANVAS_BODY,
            )
            return

        margin_x = int(36 * self._ui_scale)
        line_w = self._canvas_w - margin_x * 2
        gap = self._canvas_h / 7
        mid_gap = int(18 * self._ui_scale)

        self.create_text(
            self._canvas_w // 2,
            int(16 * self._ui_scale),
            text=hexagram.name,
            font=FONT_CANVAS_TITLE,
            fill=TITLE_COLOR,
        )

        for i, yao in enumerate(hexagram.yaos):
            y = self._canvas_h - gap * (i + 1.2)
            color = YANG_COLOR if yao.is_yang else YIN_COLOR
            line_width = max(2, int(round((4 if yao.is_yang else 3) * self._ui_scale)))

            if yao.is_yang:
                self.create_line(
                    margin_x, y, margin_x + line_w, y,
                    fill=color, width=line_width, capstyle=tk.ROUND,
                    smooth=True,
                )
            else:
                half = (line_w - mid_gap) / 2
                self.create_line(
                    margin_x, y, margin_x + half, y,
                    fill=color, width=line_width, capstyle=tk.ROUND,
                    smooth=True,
                )
                self.create_line(
                    margin_x + half + mid_gap, y, margin_x + line_w, y,
                    fill=color, width=line_width, capstyle=tk.ROUND,
                    smooth=True,
                )

            if yao.is_changing:
                r = int(5 * self._ui_scale)
                self.create_oval(
                    margin_x + line_w + int(8 * self._ui_scale), y - r,
                    margin_x + line_w + int(18 * self._ui_scale), y + r,
                    outline=CHANGE_COLOR, width=border_w,
                )

        if hexagram.has_changing and hexagram.changed_hexagram:
            chg = hexagram.changed_hexagram
            self.create_text(
                self._canvas_w // 2,
                self._canvas_h - int(8 * self._ui_scale),
                text=f"之卦 · {chg.name}",
                font=FONT_CANVAS_HINT,
                fill=CHANGE_COLOR,
            )