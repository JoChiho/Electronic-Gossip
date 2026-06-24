"""bagua Tkinter 图形界面。"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

from bagua.bazi import compute_bazi
from bagua.clipboard import copy_to_clipboard
from bagua.config import CONFIG_PATH, load_config, save_config
from bagua.gui_canvas import HexagramCanvas
from bagua.gui_theme import FONT_MONO, FONT_UI, THEME, apply_theme, style_text_widget
from bagua.records import delete_record, list_records, load_record_json, save_record
from bagua.divination import tosses_to_yao_value
from bagua.gui_display import format_hexagram_display
from bagua.models import DivinationRecord, UserConfig, UserContext
from bagua.service import perform_divination
from bagua.timezone import (
    TIMEZONE_PRESETS,
    detect_system_timezone_name,
    get_timezone,
    label_for_timezone,
    parse_datetime_input,
)

APP_TITLE = "bagua"
APP_SUBTITLE = "易经八卦占卜 · AI 解读助手"
DISCLAIMER = "仅供娱乐与文化学习参考，不构成任何决策依据。"


class BaguaGuiApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"{APP_TITLE} · 易经八卦占卜")
        self.minsize(900, 760)
        self.geometry("960x820")

        self._config = load_config()
        self._last_result = None
        self._coin_vars: list[list[tk.StringVar]] = []
        self._autosave_job: str | None = None
        self._loading_form = False

        apply_theme(self)
        self._build_widgets()
        self._load_form_from_config()
        self._bind_autosave()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_header(self, parent: ttk.Frame) -> None:
        header = tk.Frame(parent, bg=THEME["header_to"], height=88)
        header.pack(fill=tk.X, pady=(0, 12))
        header.pack_propagate(False)

        accent = tk.Frame(header, bg=THEME["accent"], width=4)
        accent.pack(side=tk.LEFT, fill=tk.Y)

        text_col = tk.Frame(header, bg=THEME["header_to"])
        text_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(16, 12), pady=14)

        tk.Label(
            text_col,
            text=APP_TITLE,
            bg=THEME["header_to"],
            fg=THEME["accent"],
            font=("Microsoft YaHei UI", 22, "bold"),
        ).pack(anchor=tk.W)
        tk.Label(
            text_col,
            text=APP_SUBTITLE,
            bg=THEME["header_to"],
            fg=THEME["text_muted"],
            font=("Microsoft YaHei UI", 10),
        ).pack(anchor=tk.W, pady=(2, 0))
        tk.Label(
            text_col,
            text=DISCLAIMER,
            bg=THEME["header_to"],
            fg=THEME["text_muted"],
            font=("Microsoft YaHei UI", 8),
        ).pack(anchor=tk.W, pady=(6, 0))

        sym = tk.Label(
            header,
            text="☰\n☷",
            bg=THEME["header_to"],
            fg=THEME["accent_dim"],
            font=("Segoe UI Symbol", 20),
            justify=tk.CENTER,
        )
        sym.pack(side=tk.RIGHT, padx=20)

    def _section(self, parent: ttk.Frame, title: str) -> ttk.LabelFrame:
        frame = ttk.LabelFrame(parent, text=f"  {title}  ", style="Section.TLabelframe", padding=14)
        frame.pack(fill=tk.X, pady=(0, 10))
        return frame

    def _build_widgets(self) -> None:
        outer = ttk.Frame(self, padding=16)
        outer.pack(fill=tk.BOTH, expand=True)

        self._build_header(outer)

        body = ttk.Frame(outer)
        body.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(body)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        right = ttk.Frame(body)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))

        scroll_canvas = tk.Canvas(
            left, highlightthickness=0, bg=THEME["bg"], borderwidth=0,
        )
        scrollbar = ttk.Scrollbar(left, orient=tk.VERTICAL, command=scroll_canvas.yview)
        scroll_frame = ttk.Frame(scroll_canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all")),
        )
        scroll_canvas.create_window((0, 0), window=scroll_frame, anchor=tk.NW)
        scroll_canvas.configure(yscrollcommand=scrollbar.set)
        scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._build_user_section(scroll_frame)
        self._build_method_section(scroll_frame)

        self.options_container = ttk.Frame(scroll_frame)
        self.options_container.pack(fill=tk.X, pady=(0, 4))
        self._build_coin_section(self.options_container)
        self._build_time_section(self.options_container)

        self._build_action_section(scroll_frame)

        self._build_result_section(right)
        self._build_prompt_section(right)

        self.status_var = tk.StringVar(value="就绪 · 设定将自动保存")
        ttk.Label(self, textvariable=self.status_var, style="Status.TLabel", anchor=tk.W).pack(
            fill=tk.X, side=tk.BOTTOM
        )

        self._on_method_changed()
        self._on_coin_mode_changed()

    def _build_user_section(self, parent: ttk.Frame) -> None:
        frame = self._section(parent, "个人信息")

        ttk.Label(frame, text="占卜问题", style="Field.TLabel").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.question_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.question_var).grid(
            row=0, column=1, columnspan=2, sticky=tk.EW, padx=(10, 0)
        )

        ttk.Label(frame, text="生辰八字", style="Field.TLabel").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.bazi_var = tk.StringVar()
        bazi_row = ttk.Frame(frame, style="Card.TFrame")
        bazi_row.grid(row=1, column=1, columnspan=2, sticky=tk.EW, padx=(10, 0))
        ttk.Entry(bazi_row, textvariable=self.bazi_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(bazi_row, text="自动排盘", command=self._auto_bazi).pack(side=tk.LEFT, padx=(8, 0))

        ttk.Label(frame, text="出生时间", style="Field.TLabel").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.birth_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.birth_var, width=28).grid(
            row=2, column=1, sticky=tk.W, padx=(10, 0)
        )
        ttk.Label(frame, text="如 1990-01-01 08:00", style="Muted.TLabel").grid(
            row=2, column=2, sticky=tk.W, padx=(8, 0)
        )

        ttk.Label(frame, text="时区", style="Field.TLabel").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.tz_display_var = tk.StringVar()
        self.tz_combo = ttk.Combobox(
            frame,
            textvariable=self.tz_display_var,
            values=[label for _, label in TIMEZONE_PRESETS],
            state="readonly",
            width=36,
        )
        self.tz_combo.grid(row=3, column=1, columnspan=2, sticky=tk.W, padx=(10, 0))
        frame.columnconfigure(1, weight=1)

    def _build_method_section(self, parent: ttk.Frame) -> None:
        frame = self._section(parent, "起卦方式")

        self.method_var = tk.StringVar(value="coin")
        methods = [("coin", "铜钱法"), ("time", "时间起卦"), ("random", "随机起卦")]
        method_row = ttk.Frame(frame, style="Card.TFrame")
        method_row.grid(row=0, column=0, columnspan=3, sticky=tk.W)
        for val, label in methods:
            ttk.Radiobutton(
                method_row,
                text=label,
                variable=self.method_var,
                value=val,
                command=self._on_method_changed,
            ).pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(frame, text="铜钱模式", style="Field.TLabel").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.coin_mode_var = tk.StringVar(value="manual")
        coin_row = ttk.Frame(frame, style="Card.TFrame")
        coin_row.grid(row=1, column=1, columnspan=2, sticky=tk.W, padx=(10, 0), pady=(10, 0))
        for val, label in [("manual", "手动（1=阳 2=阴）"), ("auto", "自动模拟")]:
            ttk.Radiobutton(
                coin_row,
                text=label,
                variable=self.coin_mode_var,
                value=val,
                command=self._on_coin_mode_changed,
            ).pack(side=tk.LEFT, padx=(0, 16))

    def _build_coin_section(self, parent: ttk.Frame) -> None:
        self.coin_frame = ttk.LabelFrame(
            parent, text="  铜钱手动输入  ", style="Section.TLabelframe", padding=12
        )
        self.coin_frame.pack(fill=tk.X, pady=(0, 8))

        from bagua.data import YAO_POSITIONS

        self._coin_vars.clear()
        for row, pos_name in enumerate(YAO_POSITIONS):
            ttk.Label(self.coin_frame, text=pos_name, style="Field.TLabel", width=6).grid(
                row=row, column=0, sticky=tk.W, pady=3
            )
            row_vars: list[tk.StringVar] = []
            for col in range(3):
                var = tk.StringVar(value="1")
                row_vars.append(var)
                ttk.Combobox(
                    self.coin_frame,
                    textvariable=var,
                    values=["1", "2"],
                    width=4,
                    state="readonly",
                ).grid(row=row, column=col + 1, padx=5, pady=3)
            self._coin_vars.append(row_vars)

    def _build_time_section(self, parent: ttk.Frame) -> None:
        self.time_frame = ttk.LabelFrame(
            parent, text="  时间起卦  ", style="Section.TLabelframe", padding=12
        )
        self.time_frame.pack(fill=tk.X, pady=(0, 8))

        self.use_now_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            self.time_frame,
            text="使用当前时间",
            variable=self.use_now_var,
            command=self._on_use_now_changed,
        ).grid(row=0, column=0, columnspan=2, sticky=tk.W)

        ttk.Label(self.time_frame, text="历法", style="Field.TLabel").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.calendar_var = tk.StringVar(value="solar")
        cal_row = ttk.Frame(self.time_frame, style="Card.TFrame")
        cal_row.grid(row=1, column=1, columnspan=2, sticky=tk.W, padx=(10, 0), pady=(10, 0))
        ttk.Radiobutton(
            cal_row, text="公历", variable=self.calendar_var, value="solar",
            command=self._on_calendar_changed,
        ).pack(side=tk.LEFT)
        ttk.Radiobutton(
            cal_row, text="农历", variable=self.calendar_var, value="lunar",
            command=self._on_calendar_changed,
        ).pack(side=tk.LEFT, padx=(14, 0))

        ttk.Label(self.time_frame, text="指定时间", style="Field.TLabel").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        self.time_input_var = tk.StringVar()
        self.time_entry = ttk.Entry(self.time_frame, textvariable=self.time_input_var, width=26)
        self.time_entry.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=(10, 0))
        self.time_hint_label = ttk.Label(self.time_frame, text="公历，如 2026-06-24 14:30", style="Muted.TLabel")
        self.time_hint_label.grid(row=2, column=2, sticky=tk.W, padx=(8, 0))

    def _build_action_section(self, parent: ttk.Frame) -> None:
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=(4, 0))
        ttk.Button(frame, text="☯  起  卦", style="Accent.TButton", command=self._on_divinate).pack(
            side=tk.LEFT
        )
        ttk.Label(
            frame,
            text="修改任意选项后将自动保存",
            style="Muted.TLabel",
        ).pack(side=tk.LEFT, padx=(14, 0))

    def _build_result_section(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="  卦象结果  ", style="Section.TLabelframe", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.hexagram_canvas = HexagramCanvas(frame, width=300, height=250)
        self.hexagram_canvas.pack(fill=tk.X, pady=(0, 10))
        self.hexagram_canvas.draw_hexagram(None)

        self.result_text = scrolledtext.ScrolledText(
            frame, height=14, wrap=tk.WORD, font=FONT_MONO,
        )
        style_text_widget(self.result_text, readonly=True)
        self.result_text.pack(fill=tk.BOTH, expand=True)

    def _build_prompt_section(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="  AI 解读提示词  ", style="Section.TLabelframe", padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        self.prompt_text = scrolledtext.ScrolledText(
            frame, height=16, wrap=tk.WORD, font=FONT_UI,
        )
        style_text_widget(self.prompt_text)
        self.prompt_text.pack(fill=tk.BOTH, expand=True)

        btn_row = ttk.Frame(frame)
        btn_row.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(btn_row, text="复制提示词", command=self._copy_prompt).pack(side=tk.LEFT)
        ttk.Button(btn_row, text="保存记录", command=self._save_record).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(btn_row, text="历史记录", style="Ghost.TButton", command=self._show_history).pack(
            side=tk.RIGHT
        )

    def _bind_autosave(self) -> None:
        for var in (
            self.question_var,
            self.bazi_var,
            self.birth_var,
            self.tz_display_var,
            self.method_var,
            self.coin_mode_var,
            self.calendar_var,
            self.time_input_var,
        ):
            var.trace_add("write", lambda *_: self._schedule_save())
        self.use_now_var.trace_add("write", lambda *_: self._schedule_save())
        for row in self._coin_vars:
            for var in row:
                var.trace_add("write", lambda *_: self._schedule_save())
        self.tz_combo.bind("<<ComboboxSelected>>", lambda _e: self._schedule_save())

    def _schedule_save(self) -> None:
        if self._loading_form:
            return
        if self._autosave_job:
            self.after_cancel(self._autosave_job)
        self._autosave_job = self.after(600, self._autosave)

    def _autosave(self) -> None:
        self._autosave_job = None
        self._persist_config_from_form()
        if CONFIG_PATH.exists():
            self.status_var.set(f"已自动保存 · {CONFIG_PATH.name}")

    def _on_method_changed(self) -> None:
        method = self.method_var.get()
        self.coin_frame.pack_forget()
        self.time_frame.pack_forget()
        if method == "coin":
            self.coin_frame.pack(fill=tk.X, pady=(0, 4))
            self._on_coin_mode_changed()
        elif method == "time":
            self.time_frame.pack(fill=tk.X, pady=(0, 4))
        self._schedule_save()

    def _on_coin_mode_changed(self) -> None:
        if self.method_var.get() != "coin":
            return
        manual = self.coin_mode_var.get() == "manual"
        state = "readonly" if manual else "disabled"
        for child in self.coin_frame.winfo_children():
            if isinstance(child, ttk.Combobox):
                child.configure(state=state)
        self._schedule_save()

    def _on_use_now_changed(self) -> None:
        state = "disabled" if self.use_now_var.get() else "normal"
        self.time_entry.configure(state=state)
        self._schedule_save()

    def _on_calendar_changed(self) -> None:
        if self.calendar_var.get() == "lunar":
            self.time_hint_label.configure(text="农历，如 2026-05-10 14:30")
        else:
            self.time_hint_label.configure(text="公历，如 2026-06-24 14:30")
        self._schedule_save()

    def _auto_bazi(self) -> None:
        birth = self.birth_var.get().strip()
        if not birth:
            messagebox.showinfo("提示", "请先填写出生时间")
            return
        iana, region = self._selected_timezone()
        tz = get_timezone(iana, region)
        computed = compute_bazi(birth, tz)
        if not computed:
            messagebox.showwarning("排盘失败", "无法解析出生时间，请检查格式与时区")
            return
        self.bazi_var.set(computed)
        self.status_var.set("已自动排八字")

    def _selected_timezone(self) -> tuple[str, str]:
        label = self.tz_display_var.get()
        for iana, preset_label in TIMEZONE_PRESETS:
            if preset_label == label:
                return iana, preset_label
        return self._config.timezone, self._config.region_label

    def _collect_coin_tosses_state(self) -> list[list[str]]:
        return [[v.get() for v in row] for row in self._coin_vars]

    def _build_context(self) -> UserContext:
        iana, region = self._selected_timezone()
        tz = get_timezone(iana, region)
        return UserContext(
            question=self.question_var.get().strip(),
            bazi=self.bazi_var.get().strip(),
            birth_datetime=self.birth_var.get().strip(),
            tz=tz,
            coin_mode=self.coin_mode_var.get(),
            calendar_mode=self.calendar_var.get(),
            include_hexagram_texts=self._config.include_hexagram_texts,
        )

    def _collect_coin_tosses(self) -> list[list[int]] | None:
        if self.coin_mode_var.get() == "auto":
            return None
        tosses: list[list[int]] = []
        for row_vars in self._coin_vars:
            points = [3 if v.get() == "1" else 2 for v in row_vars]
            tosses_to_yao_value(points)
            tosses.append(points)
        return tosses

    def _set_text_widget(self, widget: scrolledtext.ScrolledText, content: str) -> None:
        widget.configure(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, content)
        if widget is self.result_text:
            widget.configure(state=tk.DISABLED)

    def _on_divinate(self) -> None:
        try:
            ctx = self._build_context()
            method = self.method_var.get()
            coin_tosses = None
            divination_dt = None
            coin_mode = self.coin_mode_var.get()

            if method == "coin":
                coin_tosses = self._collect_coin_tosses()
            elif method == "time":
                lunar_input = None
                if not self.use_now_var.get():
                    raw = self.time_input_var.get().strip()
                    if ctx.calendar_mode == "lunar":
                        from bagua.lunar_util import parse_lunar_datetime_input

                        if parse_lunar_datetime_input(raw) is None:
                            messagebox.showerror("输入错误", "农历时间格式无效，请使用如 2026-05-10 14:30")
                            return
                        lunar_input = raw
                    else:
                        divination_dt = parse_datetime_input(raw, ctx.tz)
                        if divination_dt is None:
                            messagebox.showerror("输入错误", "公历时间格式无效，请使用如 2026-06-24 14:30")
                            return
                if ctx.calendar_mode == "lunar" and lunar_input:
                    ctx = UserContext(
                        question=ctx.question,
                        bazi=ctx.bazi,
                        birth_datetime=ctx.birth_datetime,
                        tz=ctx.tz,
                        coin_mode=ctx.coin_mode,
                        calendar_mode=ctx.calendar_mode,
                        lunar_input=lunar_input,
                        include_hexagram_texts=ctx.include_hexagram_texts,
                    )

            result = perform_divination(
                method,
                ctx,
                coin_tosses=coin_tosses,
                divination_datetime=divination_dt,
                coin_mode=coin_mode,
                auto_bazi=self._config.auto_bazi,
            )
            self._last_result = result

            result_lines = [
                f"起卦时间：{result.divination_time}",
                f"起卦方法：{result.method_desc}",
                "",
                format_hexagram_display(result.hexagram),
            ]
            self._set_text_widget(self.result_text, "\n".join(result_lines))
            self._set_text_widget(self.prompt_text, result.prompt)
            self.hexagram_canvas.draw_hexagram(result.hexagram)

            self._persist_config_from_form()
            if self._config.auto_copy_prompt and copy_to_clipboard(result.prompt):
                self.status_var.set("起卦完成 · 提示词已复制到剪贴板")
            else:
                self.status_var.set("起卦完成")
        except Exception as exc:
            messagebox.showerror("起卦失败", str(exc))
            self.status_var.set("起卦失败")

    def _copy_prompt(self) -> None:
        text = self.prompt_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showinfo("提示", "暂无提示词可复制")
            return
        if copy_to_clipboard(text):
            self.status_var.set("已复制到剪贴板")
        else:
            messagebox.showwarning("复制失败", "无法写入剪贴板，请手动选择文本复制")

    def _save_record(self) -> None:
        if self._last_result is None:
            messagebox.showinfo("提示", "请先起卦")
            return
        ctx = self._build_context()
        record = DivinationRecord(
            question=ctx.question,
            bazi=ctx.bazi,
            birth_datetime=ctx.birth_datetime,
            method=self._last_result.method_desc,
            divination_time=self._last_result.divination_time,
            timezone=ctx.tz.iana_name,
            hexagram=self._last_result.hexagram,
            prompt=self._last_result.prompt,
        )
        path = save_record(record)
        messagebox.showinfo("已保存", f"记录已保存至\n{path}")
        self.status_var.set(f"已保存：{path.name}")

    def _load_coin_tosses_from_config(self, cfg: UserConfig) -> None:
        stored = cfg.coin_tosses or []
        for i, row_vars in enumerate(self._coin_vars):
            row_data = stored[i] if i < len(stored) else ["1", "1", "1"]
            for j, var in enumerate(row_vars):
                val = row_data[j] if j < len(row_data) else "1"
                var.set(val if val in ("1", "2") else "1")

    def _load_form_from_config(self) -> None:
        self._loading_form = True
        try:
            cfg = self._config
            if not cfg.timezone or cfg.timezone == "Asia/Shanghai":
                detected = detect_system_timezone_name()
                if detected != "Asia/Shanghai":
                    cfg.timezone = detected
                    cfg.region_label = label_for_timezone(detected)

            self.question_var.set(cfg.question)
            self.bazi_var.set(cfg.bazi)
            self.birth_var.set(cfg.birth_datetime)
            self.coin_mode_var.set(cfg.coin_mode if cfg.coin_mode in ("manual", "auto") else "manual")
            self.calendar_var.set(cfg.calendar_mode if cfg.calendar_mode in ("solar", "lunar") else "solar")
            self.method_var.set(cfg.last_method if cfg.last_method in ("coin", "time", "random") else "coin")
            self.use_now_var.set(cfg.use_current_time)
            self.time_input_var.set(cfg.time_input)
            self._load_coin_tosses_from_config(cfg)

            labels = [label for _, label in TIMEZONE_PRESETS]
            if cfg.region_label in labels:
                self.tz_display_var.set(cfg.region_label)
            else:
                self.tz_display_var.set(TIMEZONE_PRESETS[0][1])

            self._on_method_changed()
            self._on_use_now_changed()
            self._on_calendar_changed()
        finally:
            self._loading_form = False

    def _persist_config_from_form(self) -> None:
        iana, region = self._selected_timezone()
        self._config = UserConfig(
            timezone=iana,
            region_label=region,
            question=self.question_var.get().strip(),
            bazi=self.bazi_var.get().strip(),
            birth_datetime=self.birth_var.get().strip(),
            coin_mode=self.coin_mode_var.get(),
            calendar_mode=self.calendar_var.get(),
            auto_bazi=self._config.auto_bazi,
            auto_copy_prompt=self._config.auto_copy_prompt,
            include_hexagram_texts=self._config.include_hexagram_texts,
            last_method=self.method_var.get(),
            use_current_time=self.use_now_var.get(),
            time_input=self.time_input_var.get().strip(),
            coin_tosses=self._collect_coin_tosses_state(),
        )
        save_config(self._config)

    def _show_history(self) -> None:
        win = tk.Toplevel(self)
        win.title("历史记录")
        win.geometry("680x420")
        win.configure(bg=THEME["bg"])
        win.transient(self)

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
            self._set_text_widget(self.prompt_text, data.get("prompt", ""))
            self.status_var.set(f"已加载记录：{records[idx].filename}")
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
            self.status_var.set(f"已删除：{rec.filename}")

        btn_row = ttk.Frame(win, padding=12)
        btn_row.pack(fill=tk.X)
        ttk.Button(btn_row, text="查看", command=_view).pack(side=tk.LEFT)
        ttk.Button(btn_row, text="加载提示词", command=_load_prompt).pack(side=tk.LEFT, padx=8)
        ttk.Button(btn_row, text="删除", command=_delete).pack(side=tk.LEFT)
        ttk.Button(btn_row, text="关闭", command=win.destroy).pack(side=tk.RIGHT)

    def _on_close(self) -> None:
        if self._autosave_job:
            self.after_cancel(self._autosave_job)
        self._persist_config_from_form()
        self.destroy()


def main() -> None:
    app = BaguaGuiApp()
    app.mainloop()


if __name__ == "__main__":
    main()