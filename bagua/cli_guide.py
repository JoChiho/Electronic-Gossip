"""CLI 交互引导文案与步骤提示（纯文本行布局，避免窄终端表格重叠）。"""

from __future__ import annotations

from rich import box
from rich.console import Console
from rich.panel import Panel

TOTAL_STEPS = 4


def _panel(console: Console, body: str, title: str, border_style: str = "blue") -> None:
    """按终端宽度渲染面板，防止窄窗口文字挤压重叠。"""
    term_w = console.width or 78
    panel_w = max(28, min(term_w - 2, 76))
    console.print(
        Panel(
            body,
            title=title,
            border_style=border_style,
            box=box.ROUNDED,
            width=panel_w,
            expand=False,
        )
    )


def show_quick_start(console: Console, *, first_run: bool = False) -> None:
    lines = [
        "本次流程（约 1-2 分钟）",
        "  1. 确认个人信息（问题、八字、时区）",
        "  2. 选择起卦方式并完成起卦",
        "  3. 查看卦象与变爻",
        "  4. 复制 AI 提示词，粘贴到大模型解读",
        "",
        "输入习惯",
        "  - 直接回车 = 沿用默认值",
        "  - Y / n 回答问题，不区分大小写",
        "",
        "下次更快（无需逐步问答）",
        '  bagua -m random -q "工作运势" --copy',
        "  bagua --list-records",
    ]
    if first_run:
        lines.insert(0, "【首次使用】建议先完整走一遍交互流程。")
        lines.append("")
        lines.append("个人信息将保存至 ~/.bagua/config.json")

    _panel(console, "\n".join(lines), "[bold]使用引导[/bold]", "blue")


def show_step(console: Console, step: int, title: str) -> None:
    console.print()
    console.print(f"[bold blue]步骤 {step}/{TOTAL_STEPS}[/bold blue]  [bold]{title}[/bold]")
    console.print("[dim]" + "-" * 40 + "[/dim]")


def show_user_fields_help(console: Console) -> None:
    console.print("[bold]各字段说明[/bold]")
    console.print("  [cyan]占卜问题[/cyan]")
    console.print("    你想问的事，如工作、感情、决策（可留空）")
    console.print("  [cyan]生辰八字[/cyan]")
    console.print("    辅助 AI 解读（可留空；填写出生时间后可自动排盘）")
    console.print("  [cyan]出生时间[/cyan]")
    console.print("    公历本地时间，如 1990-01-01 08:00")
    console.print("  [cyan]时区[/cyan]")
    console.print("    影响起卦时间与出生时间的标注")
    console.print()


def show_calendar_mode_guide(console: Console) -> None:
    body = (
        "1  公历起卦\n"
        "   以公历年月日时起卦（默认）\n"
        "\n"
        "2  农历起卦\n"
        "   梅花易数农历模式：\n"
        "   - 使用当前时间时，自动换算为农历\n"
        "   - 手动输入时，按农历数字填写（如 2026-05-10 14:30）"
    )
    _panel(console, body, "[bold]历法选择[/bold]", "cyan")


def show_method_guide(console: Console) -> None:
    body = (
        "1  铜钱法\n"
        "   三枚铜钱掷六次，可手动输入或自动模拟\n"
        "   适合：想要参与感、传统体验\n"
        "\n"
        "2  时间起卦\n"
        "   梅花易数，以年月日时推算卦象\n"
        "   适合：有明确起卦时刻\n"
        "\n"
        "3  随机起卦\n"
        "   一键生成六爻\n"
        "   适合：快速摸鱼、日常灵感\n"
        "\n"
        "4  数字起卦\n"
        "   梅花报数，输入 2～3 个正整数\n"
        "   适合：心中已有数字、测数起卦\n"
        "\n"
        "5  手动选卦\n"
        "   直接选上卦、下卦与动爻（可无）\n"
        "   适合：已知卦象、教学对照\n"
        "\n"
        "6  蓍草法\n"
        "   大衍筮法程序模拟（非实体蓍草）\n"
        "   适合：体验传统演卦流程\n"
        "\n"
        "7  汉字起卦\n"
        "   梅花字课，以汉字笔画起卦\n"
        "   适合：测字、一字一词问事"
    )
    _panel(console, body, "[bold]起卦方式说明[/bold]", "cyan")
    console.print()


def show_coin_value_legend(console: Console) -> None:
    body = (
        "输入规则\n"
        "  1 = 阳面（字）\n"
        "  2 = 阴面（花）\n"
        "  每爻输入三个数字，空格分隔\n"
        "  示例：1 2 1\n"
        "\n"
        "爻值对照\n"
        "  6 = 老阴（变爻）\n"
        "  7 = 少阳\n"
        "  8 = 少阴\n"
        "  9 = 老阳（变爻）"
    )
    _panel(console, body, "[bold]铜钱输入说明[/bold]", "cyan")


def show_time_guide(console: Console, region_label: str, current_time: str) -> None:
    body = (
        f"当前时区：{region_label}\n"
        f"当前时间：\n  {current_time}\n"
        "\n"
        "选 Y = 使用当前时间起卦\n"
        "选 n = 自行输入，格式如 2026-06-24 14:30"
    )
    _panel(console, body, "[bold]时间起卦说明[/bold]", "cyan")


def show_random_guide(console: Console) -> None:
    body = (
        "将随机生成六个爻值并立即出卦。\n"
        "这是最快的起卦方式，适合日常快速占卜。"
    )
    _panel(console, body, "[bold]随机起卦[/bold]", "cyan")


def show_character_guide(console: Console) -> None:
    body = (
        "梅花字课：以汉字笔画数起卦（默认康熙字典笔画）。\n"
        "\n"
        "策略\n"
        "  auto      1字拆两数 / 2字 / 3字+ 自动选择\n"
        "  first_two 前两字笔画→上下卦\n"
        "  first_three 前三字笔画→上下卦与动爻\n"
        "  total     总笔画→上卦，字数→下卦\n"
        "\n"
        "未收录字以码点回退取数（method_desc 会标注）。"
    )
    _panel(console, body, "[bold]汉字起卦说明[/bold]", "cyan")


def show_yarrow_guide(console: Console) -> None:
    body = (
        "大衍之数五十，其用四十有九。\n"
        "每爻三变：分二、挂一、揲四、归奇；三变余 24/28/32/36 → 爻值 6/7/8/9。\n"
        "\n"
        "本程序为算法模拟，非实体蓍草演算；概率遵循大衍筮法（非三钱法）。"
    )
    _panel(console, body, "[bold]蓍草法（大衍模拟）[/bold]", "cyan")


def show_manual_guide(console: Console) -> None:
    body = (
        "八卦序号（上卦 / 下卦）\n"
        "  1乾  2兑  3离  4震  5巽  6坎  7艮  8坤\n"
        "\n"
        "动爻可选 1～6（初爻至上爻），留空或 0 表示无动爻（全静卦）"
    )
    _panel(console, body, "[bold]手动选卦说明[/bold]", "cyan")


def show_number_guide(console: Console) -> None:
    body = (
        "梅花报数起卦\n"
        "  输入 2 个正整数：上卦＝第一数 mod 8，下卦＝第二数 mod 8，\n"
        "  动爻＝(第一数+第二数) mod 6（余 0 取上爻 6）\n"
        "\n"
        "  输入 3 个正整数：上卦、下卦同上，动爻＝第三数 mod 6\n"
        "\n"
        "示例：3 8 5  或  3,8,5"
    )
    _panel(console, body, "[bold]数字起卦说明[/bold]", "cyan")


def show_pre_result_summary(
    console: Console,
    method_label: str,
    question: str,
    tz_label: str,
) -> None:
    q = question.strip() or "（未指定，AI 将做综合解读）"
    body = (
        f"起卦方式：{method_label}\n"
        f"占卜问题：{q}\n"
        f"时区：{tz_label}\n"
        "\n"
        "正在生成卦象与 AI 提示词..."
    )
    _panel(console, body, "[bold]即将起卦[/bold]", "green")


def show_completion_guide(console: Console, *, auto_copied: bool) -> None:
    if auto_copied:
        lines = [
            "提示词已自动复制到剪贴板。",
            "  1. 打开 ChatGPT / Claude / 其他大模型",
            "  2. 直接 Ctrl+V 粘贴并发送",
            "  3. 输入 y 可保存本次占卜记录",
        ]
    else:
        lines = [
            "自动复制未成功，请手动操作：",
            "  1. 用鼠标选中上方 AI 提示词区域",
            "  2. Ctrl+C 复制，粘贴到大模型",
            "  3. 输入 y 可保存本次占卜记录",
            "",
            "也可使用：bagua -m random -q \"问题\" --copy",
        ]
    _panel(console, "\n".join(lines), "[bold]下一步[/bold]", "green")


METHOD_LABELS = {
    "coin": "铜钱法",
    "time": "时间起卦",
    "random": "随机起卦",
    "number": "数字起卦",
    "manual": "手动选卦",
    "yarrow": "蓍草法",
    "character": "汉字起卦",
}

ARGPARSE_EPILOG = """
示例：
  bagua                              # 交互模式（逐步引导）
  bagua -m random -q "工作运势"      # 快速随机起卦
  bagua -m random -q "问题"          # 非交互（默认按 config 自动复制）
  bagua -m random -q "问题" --no-copy # 禁止自动复制
  bagua -m time --at "2026-06-24 14:30"
  bagua -m time --calendar lunar --lunar-at "2026-05-10 14:30"
  bagua -m number --nums "3 8 5" -q "此事如何"
  bagua -m manual --upper 1 --lower 8 --changing 3
  bagua -m manual --upper 1 --lower 1 --changing 0
  bagua -m yarrow --yarrow-show-process
  bagua -m character --chars "问事" --stroke-mode kangxi
  bagua --list-records               # 查看历史记录
  bagua --list-records --search 工作 # 搜索历史记录
  bagua --show-record 1              # 查看第 1 条记录
  bagua --export-record 1 -o out.md  # 导出单条为 Markdown
  bagua --export-records -o all.md   # 导出全部记录
  bagua --export-records --search 跳槽 -o job.md

交互模式输入提示：
  回车    沿用默认值
  1 / 2   铜钱每枚：1=阳面，2=阴面
  Y / n   确认类问题
"""