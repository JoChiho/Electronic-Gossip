"""CLI 交互引导文案与步骤提示。"""

from __future__ import annotations

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

TOTAL_STEPS = 4


def show_quick_start(console: Console, *, first_run: bool = False) -> None:
    """启动时展示流程概览与快捷用法。"""
    lines = [
        "[bold]本次流程[/bold]（约 1–2 分钟）",
        "  [cyan]①[/cyan] 确认个人信息（问题、八字、时区）",
        "  [cyan]②[/cyan] 选择起卦方式并完成起卦",
        "  [cyan]③[/cyan] 查看卦象与变爻",
        "  [cyan]④[/cyan] 复制 AI 提示词，粘贴到大模型解读",
        "",
        "[bold]输入习惯[/bold]",
        "  · 直接 [green]回车[/green] = 沿用括号中的默认值",
        "  · [green]Y[/green] / [green]n[/green] 回答问题，不区分大小写",
        "",
        "[bold]下次更快[/bold]（无需逐步问答）",
        '  [dim]bagua -m random -q "工作运势" --copy[/dim]',
        "  [dim]bagua --list-records[/dim]",
    ]
    if first_run:
        lines.insert(0, "[yellow]首次使用[/yellow]，建议先完整走一遍交互流程。")
        lines.append("")
        lines.append(f"[dim]个人信息将保存至 ~/.bagua/config.json，下次可一键沿用。[/dim]")

    console.print(
        Panel(
            "\n".join(lines),
            title="[bold]使用引导[/bold]",
            border_style="blue",
            box=box.ROUNDED,
        )
    )


def show_step(console: Console, step: int, title: str) -> None:
    console.print()
    console.print(f"[bold blue]步骤 {step}/{TOTAL_STEPS}[/bold blue]  [bold]{title}[/bold]")
    console.print("[dim]" + "─" * 48 + "[/dim]")


def show_user_fields_help(console: Console) -> None:
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("字段", style="cyan", no_wrap=True)
    table.add_column("说明")
    table.add_row("占卜问题", "你想问的事，如工作、感情、决策（可留空）")
    table.add_row("生辰八字", "辅助 AI 解读，可留空")
    table.add_row("出生时间", "公历本地时间，配合上方时区理解")
    table.add_row("时区", "影响起卦时间与出生时间的标注")
    console.print(table)
    console.print()


def show_method_guide(console: Console) -> None:
    table = Table(title="起卦方式说明", box=box.SIMPLE, show_lines=True)
    table.add_column("选项", style="cyan", justify="center")
    table.add_column("方式", style="bold")
    table.add_column("说明")
    table.add_column("适合场景")
    table.add_row("1", "铜钱法", "三枚铜钱掷六次，可手动输入或自动模拟", "想要参与感、传统体验")
    table.add_row("2", "时间起卦", "梅花易数，以年月日时推算卦象", "有明确起卦时刻")
    table.add_row("3", "随机起卦", "一键生成六爻", "快速摸鱼、日常灵感")
    console.print(table)
    console.print()


def show_coin_value_legend(console: Console) -> None:
    console.print(
        Panel(
            "[green]1[/green] = 阳面（字）    [yellow]2[/yellow] = 阴面（花）\n"
            "每爻输入三个数字，空格分隔，例如：[bold]1 2 1[/bold]\n\n"
            "爻值对照：\n"
            "  [bold]6[/bold] 老阴（变爻）  [bold]7[/bold] 少阳\n"
            "  [bold]8[/bold] 少阴          [bold]9[/bold] 老阳（变爻）",
            title="铜钱输入说明",
            border_style="cyan",
            box=box.ROUNDED,
        )
    )


def show_time_guide(console: Console, region_label: str, current_time: str) -> None:
    console.print(
        Panel(
            f"当前时区：[bold]{region_label}[/bold]\n"
            f"当前时间：[bold]{current_time}[/bold]\n\n"
            "选择「使用当前时间」将以上时刻起卦；\n"
            "也可自行输入，格式如 [cyan]2026-06-24 14:30[/cyan]",
            title="时间起卦说明",
            border_style="cyan",
            box=box.ROUNDED,
        )
    )


def show_random_guide(console: Console) -> None:
    console.print(
        Panel(
            "将随机生成六个爻值并立即出卦。\n"
            "这是最快的起卦方式，适合没有特定仪式感的日常占卜。",
            title="随机起卦",
            border_style="cyan",
            box=box.ROUNDED,
        )
    )


def show_pre_result_summary(
    console: Console,
    method_label: str,
    question: str,
    tz_label: str,
) -> None:
    q = question.strip() or "（未指定，AI 将做综合解读）"
    console.print(
        Panel(
            f"起卦方式：[bold]{method_label}[/bold]\n"
            f"占卜问题：[bold]{q}[/bold]\n"
            f"时区：[bold]{tz_label}[/bold]\n\n"
            "[dim]正在生成卦象与 AI 提示词…[/dim]",
            title="即将起卦",
            border_style="green",
            box=box.ROUNDED,
        )
    )


def show_completion_guide(console: Console, *, copied_hint: bool = False) -> None:
    lines = [
        "[bold]接下来你可以：[/bold]",
        "  1. 用鼠标选中上方 [green]AI 解读提示词[/green] 区域，Ctrl+C 复制",
        "  2. 粘贴到 ChatGPT / Claude / 其他大模型对话框",
        "  3. 输入 [cyan]y[/cyan] 保存本次占卜记录，便于日后查看",
    ]
    if copied_hint:
        lines.append("")
        lines.append("下次可用 [dim]bagua -m random -q \"问题\" --copy[/dim] 一步完成")
    console.print(
        Panel(
            "\n".join(lines),
            title="[bold]完成引导[/bold]",
            border_style="green",
            box=box.ROUNDED,
        )
    )


METHOD_LABELS = {
    "coin": "铜钱法",
    "time": "时间起卦",
    "random": "随机起卦",
}

ARGPARSE_EPILOG = """
示例：
  bagua                              # 交互模式（逐步引导）
  bagua -m random -q "工作运势"      # 快速随机起卦
  bagua -m random -q "问题" --copy   # 起卦并复制提示词
  bagua -m time --at "2026-06-24 14:30"
  bagua --list-records               # 查看历史记录
  bagua --show-record 1              # 查看第 1 条记录

交互模式输入提示：
  回车    沿用默认值
  1 / 2   铜钱每枚：1=阳面，2=阴面
  Y / n   确认类问题
"""