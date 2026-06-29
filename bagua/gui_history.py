"""GUI 历史记录窗口。"""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from typing import TYPE_CHECKING, Protocol

from bagua.gui_theme import FONT_SUBTITLE, FONT_UI, THEME, style_text_widget
from bagua.records import (
    RecordSummary,
    delete_record,
    export_record_markdown,
    export_records_markdown,
    list_records,
    load_record_json,
    search_records,
)

if TYPE_CHECKING:

    class HistoryHost(Protocol):
        prompt_text: scrolledtext.ScrolledText
        status_var: tk.StringVar

        def _set_text_widget(self, widget: scrolledtext.ScrolledText, content: str) -> None: ...


def _format_list_label(index: int, rec: RecordSummary) -> str:
    q = rec.question or "（无问题）"
    if len(q) > 24:
        q = q[:23] + "…"
    return f"{index}. {rec.saved_at}  {rec.hexagram_name}  {q}"


def open_history_window(app: HistoryHost, parent: tk.Misc) -> None:
    win = tk.Toplevel(parent)
    win.title("历史记录")
    win.geometry("760x520")
    win.configure(bg=THEME["bg"])
    win.transient(parent)  # type: ignore[call-overload]

    all_records: list[RecordSummary] = list_records()
    visible_records: list[RecordSummary] = list(all_records)

    root_frame = ttk.Frame(win, padding=12)
    root_frame.pack(fill=tk.BOTH, expand=True)

    search_row = ttk.Frame(root_frame)
    search_row.pack(fill=tk.X, pady=(0, 10))
    ttk.Label(search_row, text="搜索", style="Field.TLabel").pack(side=tk.LEFT)
    search_var = tk.StringVar()
    search_entry = ttk.Entry(search_row, textvariable=search_var, width=36)
    search_entry.pack(side=tk.LEFT, padx=(8, 8))
    count_var = tk.StringVar(value=f"共 {len(all_records)} 条")
    ttk.Label(search_row, textvariable=count_var, style="Muted.TLabel").pack(side=tk.LEFT)

    body = ttk.Frame(root_frame)
    body.pack(fill=tk.BOTH, expand=True)

    listbox = tk.Listbox(
        body,
        font=FONT_UI,
        bg=THEME["input_bg"],
        fg=THEME["text"],
        selectbackground=THEME["accent_dim"],
        selectforeground=THEME["text"],
        highlightthickness=0,
        borderwidth=0,
    )
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scroll = ttk.Scrollbar(body, orient=tk.VERTICAL, command=listbox.yview)
    scroll.pack(side=tk.LEFT, fill=tk.Y)
    listbox.configure(yscrollcommand=scroll.set)

    def _repopulate_list(records: list[RecordSummary]) -> None:
        listbox.delete(0, tk.END)
        visible_records.clear()
        visible_records.extend(records)
        if not records:
            listbox.insert(tk.END, "（无匹配记录）" if search_var.get().strip() else "（暂无记录）")
            count_var.set("共 0 条")
            return
        for i, rec in enumerate(records, start=1):
            listbox.insert(tk.END, _format_list_label(i, rec))
        count_var.set(f"共 {len(records)} 条")

    def _apply_search() -> None:
        query = search_var.get().strip()
        if query:
            _repopulate_list(search_records(query))
        else:
            all_records[:] = list_records()
            _repopulate_list(all_records)

    def _clear_search() -> None:
        search_var.set("")
        _apply_search()

    ttk.Button(search_row, text="搜索", command=_apply_search).pack(side=tk.LEFT, padx=(0, 4))
    ttk.Button(search_row, text="重置", style="Ghost.TButton", command=_clear_search).pack(side=tk.LEFT)
    search_entry.bind("<Return>", lambda _e: _apply_search())

    _repopulate_list(all_records)

    def _selected_index() -> int | None:
        sel = listbox.curselection()
        if not sel or not visible_records:
            return None
        return sel[0]

    def _view() -> None:
        idx = _selected_index()
        if idx is None:
            messagebox.showinfo("提示", "请先选择一条记录")
            return
        data = load_record_json(visible_records[idx].filename)
        if not data:
            messagebox.showerror("错误", "无法读取记录")
            return
        detail = tk.Toplevel(win)
        detail.title(visible_records[idx].filename)
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
            messagebox.showinfo("提示", "请先选择一条记录")
            return
        data = load_record_json(visible_records[idx].filename)
        if not data:
            messagebox.showerror("错误", "无法读取记录")
            return
        app._set_text_widget(app.prompt_text, data.get("prompt", ""))
        app.status_var.set(f"已加载记录：{visible_records[idx].filename}")
        win.destroy()

    def _export_selected() -> None:
        idx = _selected_index()
        if idx is None:
            messagebox.showinfo("提示", "请先选择要导出的记录")
            return
        rec = visible_records[idx]
        default_name = rec.filename.replace(".json", ".md")
        path = filedialog.asksaveasfilename(
            parent=win,
            title="导出 Markdown",
            defaultextension=".md",
            initialfile=default_name,
            filetypes=[("Markdown", "*.md"), ("所有文件", "*.*")],
        )
        if not path:
            return
        out = export_record_markdown(rec.filename, path)
        if out is None:
            messagebox.showerror("导出失败", "无法导出所选记录")
            return
        app.status_var.set(f"已导出：{out}")
        messagebox.showinfo("导出成功", f"已保存至\n{out}")

    def _export_visible() -> None:
        if not visible_records:
            messagebox.showinfo("提示", "当前列表无记录可导出")
            return
        query = search_var.get().strip()
        default_name = "bagua_export.md" if not query else f"bagua_export_{query[:12]}.md"
        path = filedialog.asksaveasfilename(
            parent=win,
            title="批量导出 Markdown",
            defaultextension=".md",
            initialfile=default_name,
            filetypes=[("Markdown", "*.md"), ("所有文件", "*.*")],
        )
        if not path:
            return
        filenames = [r.filename for r in visible_records]
        out = export_records_markdown(identifiers=filenames, output_path=path)
        if out is None:
            messagebox.showerror("导出失败", "无法导出记录")
            return
        app.status_var.set(f"已导出 {len(visible_records)} 条：{out}")
        messagebox.showinfo("导出成功", f"已导出 {len(visible_records)} 条记录至\n{out}")

    def _delete() -> None:
        idx = _selected_index()
        if idx is None:
            messagebox.showinfo("提示", "请先选择一条记录")
            return
        rec = visible_records[idx]
        if not messagebox.askyesno("确认删除", f"删除 {rec.filename}？"):
            return
        delete_record(rec.filename)
        _apply_search()
        all_records[:] = list_records()
        app.status_var.set(f"已删除：{rec.filename}")

    hint = ttk.Label(
        root_frame,
        text="可搜索问题、卦名、方法、八字或提示词关键词",
        style="Muted.TLabel",
        font=FONT_SUBTITLE,
    )
    hint.pack(anchor=tk.W, pady=(8, 0))

    btn_row = ttk.Frame(win, padding=12)
    btn_row.pack(fill=tk.X)
    ttk.Button(btn_row, text="查看", command=_view).pack(side=tk.LEFT)
    ttk.Button(btn_row, text="加载提示词", command=_load_prompt).pack(side=tk.LEFT, padx=(8, 0))
    ttk.Button(btn_row, text="导出所选", command=_export_selected).pack(side=tk.LEFT, padx=(8, 0))
    ttk.Button(btn_row, text="导出列表", style="Accent.TButton", command=_export_visible).pack(
        side=tk.LEFT, padx=(8, 0),
    )
    ttk.Button(btn_row, text="删除", command=_delete).pack(side=tk.LEFT, padx=(8, 0))
    ttk.Button(btn_row, text="关闭", command=win.destroy).pack(side=tk.RIGHT)