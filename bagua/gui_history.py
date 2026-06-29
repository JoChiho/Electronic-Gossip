"""GUI 历史记录窗口。"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from typing import TYPE_CHECKING, Protocol

from bagua.gui_theme import FONT_UI, THEME, style_text_widget
from bagua.records import delete_record, list_records, load_record_json

if TYPE_CHECKING:

    class HistoryHost(Protocol):
        prompt_text: scrolledtext.ScrolledText
        status_var: tk.StringVar

        def _set_text_widget(self, widget: scrolledtext.ScrolledText, content: str) -> None: ...


def open_history_window(app: HistoryHost, parent: tk.Misc) -> None:
    win = tk.Toplevel(parent)
    win.title("历史记录")
    win.geometry("680x420")
    win.configure(bg=THEME["bg"])
    win.transient(parent)  # type: ignore[call-overload]

    records = list_records()
    frame = ttk.Frame(win, padding=12)
    frame.pack(fill=tk.BOTH, expand=True)

    listbox = tk.Listbox(
        frame,
        font=FONT_UI,
        bg=THEME["input_bg"],
        fg=THEME["text"],
        selectbackground=THEME["accent_dim"],
        selectforeground=THEME["text"],
        highlightthickness=0,
        borderwidth=0,
    )
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=listbox.yview)
    scroll.pack(side=tk.LEFT, fill=tk.Y)
    listbox.configure(yscrollcommand=scroll.set)

    for i, rec in enumerate(records, start=1):
        label = f"{i}. {rec.saved_at}  {rec.hexagram_name}  {rec.question or '（无问题）'}"
        listbox.insert(tk.END, label)

    if not records:
        listbox.insert(tk.END, "（暂无记录）")

    def _selected_index() -> int | None:
        sel = listbox.curselection()
        if not sel or not records:
            return None
        return sel[0]

    def _view() -> None:
        idx = _selected_index()
        if idx is None:
            return
        data = load_record_json(records[idx].filename)
        if not data:
            messagebox.showerror("错误", "无法读取记录")
            return
        detail = tk.Toplevel(win)
        detail.title(records[idx].filename)
        detail.geometry("720x520")
        detail.configure(bg=THEME["bg"])
        text = scrolledtext.ScrolledText(detail, wrap=tk.WORD, font=FONT_UI)
        style_text_widget(text)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.insert(tk.END, data.get("prompt", ""))
        text.configure(state=tk.DISABLED)

    def _load_prompt() -> None:
        idx = _selected_index()
        if idx is None:
            return
        data = load_record_json(records[idx].filename)
        if not data:
            messagebox.showerror("错误", "无法读取记录")
            return
        app._set_text_widget(app.prompt_text, data.get("prompt", ""))
        app.status_var.set(f"已加载记录：{records[idx].filename}")
        win.destroy()

    def _delete() -> None:
        idx = _selected_index()
        if idx is None:
            return
        rec = records[idx]
        if not messagebox.askyesno("确认删除", f"删除 {rec.filename}？"):
            return
        delete_record(rec.filename)
        listbox.delete(0, tk.END)
        records[:] = list_records()
        for i, item in enumerate(records, start=1):
            listbox.insert(
                tk.END,
                f"{i}. {item.saved_at}  {item.hexagram_name}  {item.question or '（无问题）'}",
            )
        if not records:
            listbox.insert(tk.END, "（暂无记录）")
        app.status_var.set(f"已删除：{rec.filename}")

    btn_row = ttk.Frame(win, padding=12)
    btn_row.pack(fill=tk.X)
    ttk.Button(btn_row, text="查看", command=_view).pack(side=tk.LEFT)
    ttk.Button(btn_row, text="加载提示词", command=_load_prompt).pack(side=tk.LEFT, padx=8)
    ttk.Button(btn_row, text="删除", command=_delete).pack(side=tk.LEFT)
    ttk.Button(btn_row, text="关闭", command=win.destroy).pack(side=tk.RIGHT)