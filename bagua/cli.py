"""bagua 终端展示层（Rich + input），调用 service 层完成起卦。"""

from __future__ import annotations

import sys
from typing import Literal

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from bagua.args import parse_cli_args
from bagua.config import CONFIG_PATH, load_config, save_config
from bagua.headless import dispatch_headless
from bagua.records import save_record
from bagua.data import YAO_POSITIONS, YAO_VALUE_NAMES
from bagua.divination import coin_tosses_to_display, parse_coin_input, simulate_coin_toss
from bagua.models import DivinationRecord, UserConfig, UserContext, YaoInfo
from bagua.models import HexagramInfo
from bagua.service import perform_divination
from bagua.timezone import (
    TIMEZONE_PRESETS,
    detect_system_timezone_name,
    format_datetime_with_tz,
    get_timezone,
    is_tzdata_available,
    label_for_timezone,
    now_in_timezone,
    parse_datetime_input,
    validate_timezone_name,
)

console = Console()


# ---------------------------------------------------------------------------
# 运行时与环境
# ---------------------------------------------------------------------------

def ensure_runtime() -> None:
    if is_tzdata_available():
        return
    console.print(
        Panel(
            "[yellow]未检测到 IANA 时区数据库（tzdata）。[/yellow]\n"
            "程序将使用预设地区的[bold]固定 UTC 偏移[/bold]作为回退，可正常运行。\n\n"
            "建议安装完整时区支持：\n"
            "  [cyan]pip install tzdata[/cyan]\n"
            "或重新安装依赖：\n"
            "  [cyan]pip install -r requirements.txt[/cyan]",
            title="[bold]时区提示[/bold]",
            border_style="yellow",
            box=box.ROUNDED,
        )
    )


def show_disclaimer() -> None:
    console.print(
        Panel(
            "[dim]本工具仅供娱乐与文化学习参考，不构成任何决策依据。[/dim]",
            title="[bold]bagua[/bold] · 易经八卦占卜",
            border_style="dim",
            box=box.ROUNDED,
        )
    )


# ---------------------------------------------------------------------------
# 用户输入
# ---------------------------------------------------------------------------

def select_timezone(current: str) -> tuple[str, str]:
    console.print("\n[bold]请选择时区 / 地区：[/bold]")
    for i, (tz_name, label) in enumerate(TIMEZONE_PRESETS, start=1):
        mark = " [green]← 当前[/green]" if tz_name == current else ""
        console.print(f"  [cyan]{i:>2}[/cyan]  {label}  [dim]({tz_name})[/dim]{mark}")
    console.print("  [cyan] 0[/cyan]  手动输入 IANA 时区名称（如 Europe/Berlin）")
    if not is_tzdata_available():
        console.print("  [dim]当前为固定偏移模式，自定义时区仅支持列表内预设[/dim]")
    console.print()

    while True:
        choice = console.input(f"请输入选项 [默认 {current}，直接回车沿用]: ").strip()
        if not choice:
            return current, label_for_timezone(current)
        if choice == "0":
            raw = console.input("IANA 时区名称: ").strip()
            if validate_timezone_name(raw):
                return raw, label_for_timezone(raw)
            console.print("[red]无效时区，请重试[/red]")
            continue
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(TIMEZONE_PRESETS):
                return TIMEZONE_PRESETS[idx - 1]
        console.print("[red]无效选项[/red]")


def _prompt_with_default(label: str, default: str, hint: str = "") -> str:
    hint_text = f" [dim]({hint})[/dim]" if hint else ""
    default_hint = f" [dim][{default}][/dim]" if default else ""
    raw = console.input(f"[bold]{label}[/bold]{hint_text}{default_hint}: ").strip()
    return raw if raw else default


def setup_user_context(config: UserConfig) -> tuple[UserContext, UserConfig]:
    tz = get_timezone(config.timezone, config.region_label)

    if CONFIG_PATH.exists() and any([config.question, config.bazi, config.birth_datetime]):
        console.print()
        console.print(
            Panel(
                f"时区：{config.region_label} ({config.timezone})\n"
                f"出生时间：{config.birth_datetime or '（未设置）'}\n"
                f"生辰八字：{config.bazi or '（未设置）'}\n"
                f"默认问题：{config.question or '（未设置）'}",
                title="[bold]已保存的用户信息[/bold]",
                border_style="cyan",
                box=box.ROUNDED,
            )
        )
        use_saved = console.input("使用已保存信息？[Y/n]: ").strip().lower()
        if use_saved in ("", "y", "yes"):
            return (
                UserContext(
                    question=config.question,
                    bazi=config.bazi,
                    birth_datetime=config.birth_datetime,
                    tz=tz,
                    coin_mode=config.coin_mode,
                ),
                config,
            )

    console.print("\n[bold]设置用户信息[/bold] [dim]（可直接回车跳过或沿用默认值）[/dim]")

    if console.input(f"修改时区？当前 {config.region_label} [y/N]: ").strip().lower() in ("y", "yes"):
        tz_name, region_label = select_timezone(config.timezone)
        config.timezone = tz_name
        config.region_label = region_label
        tz = get_timezone(tz_name, region_label)

    config.birth_datetime = _prompt_with_default(
        "出生日期时间",
        config.birth_datetime,
        f"本地时间，{config.region_label}，如 1990-01-01 08:00",
    )
    config.bazi = _prompt_with_default("生辰八字", config.bazi, "可选")
    config.question = _prompt_with_default("占卜问题", config.question, "可留空")

    return (
        UserContext(
            question=config.question,
            bazi=config.bazi,
            birth_datetime=config.birth_datetime,
            tz=tz,
            coin_mode=config.coin_mode,
        ),
        config,
    )


def select_method() -> Literal["coin", "time", "random"]:
    console.print()
    console.print("[bold]请选择起卦方式：[/bold]")
    console.print("  [cyan]1[/cyan]  铜钱法（推荐）")
    console.print("  [cyan]2[/cyan]  时间起卦（梅花易数）")
    console.print("  [cyan]3[/cyan]  随机起卦（快速模式）")
    console.print()

    mapping = {"1": "coin", "2": "time", "3": "random"}
    while True:
        choice = console.input("请输入选项 [1/2/3]: ").strip()
        if choice in mapping:
            return mapping[choice]  # type: ignore[return-value]
        console.print("[red]无效选项，请输入 1、2 或 3[/red]")


def _select_coin_mode(default: str) -> str:
    console.print("\n[bold]铜钱法投掷方式：[/bold]")
    console.print("  [cyan]1[/cyan]  手动输入（每爻输入三个 1 或 2）")
    console.print("  [cyan]2[/cyan]  自动模拟（程序随机投掷三枚铜钱）")
    default_label = "手动" if default == "manual" else "自动"
    console.print(f"  [dim]直接回车沿用上次选择：{default_label}[/dim]\n")

    mapping = {"1": "manual", "2": "auto", "": default}
    while True:
        choice = console.input("请选择 [1/2]: ").strip()
        if choice in mapping:
            return mapping[choice]
        console.print("[red]无效选项，请输入 1 或 2[/red]")


def collect_coin_tosses(coin_mode: str) -> tuple[list[list[int]], str]:
    """交互收集铜钱投掷结果，返回 (六爻投掷, 实际模式)。"""
    mode = _select_coin_mode(coin_mode)
    tosses: list[list[int]] = []

    console.print("\n[bold cyan]铜钱法起卦[/bold cyan]")
    if mode == "manual":
        console.print("每爻输入三枚硬币：[green]1[/green]=阳面（字）  [yellow]2[/yellow]=阴面（花）")
        console.print("示例：[green]1 2 1[/green]  或  [green]2 2 2[/green]\n")
        for pos in range(1, 7):
            while True:
                raw = console.input(
                    f"[bold]第 {pos} 爻[/bold]（{YAO_POSITIONS[pos - 1]}）[1/2，空格分隔]: "
                ).strip()
                coins = parse_coin_input(raw)
                if coins is None:
                    console.print("[red]格式错误，请输入三个 1 或 2，如：1 2 1[/red]")
                    continue
                tosses.append(coins)
                val = sum(coins)
                console.print(f"  → 爻值 [bold]{val}[/bold]（{YAO_VALUE_NAMES[val]}）\n")
                break
    else:
        console.print("[dim]自动模拟投掷，每爻随机生成结果…[/dim]\n")
        for pos in range(1, 7):
            points = simulate_coin_toss()
            tosses.append(points)
            val = sum(points)
            console.print(
                f"  第 {pos} 爻（{YAO_POSITIONS[pos - 1]}）: {coin_tosses_to_display(points)} "
                f"→ [bold]{val}[/bold]（{YAO_VALUE_NAMES[val]}）"
            )

    return tosses, mode


def collect_divination_params(
    method: str,
    ctx: UserContext,
) -> tuple[list[list[int]] | None, object | None, str]:
    """收集起卦参数，返回 (coin_tosses, divination_datetime, coin_mode)。"""
    coin_tosses: list[list[int]] | None = None
    divination_datetime = None
    coin_mode = ctx.coin_mode

    if method == "coin":
        coin_tosses, coin_mode = collect_coin_tosses(ctx.coin_mode)
    elif method == "time":
        console.print()
        dt_now = now_in_timezone(ctx.tz)
        if console.input("使用当前时间？[Y/n]: ").strip().lower() not in ("n", "no"):
            divination_datetime = dt_now
        else:
            raw = console.input(
                f"请输入时间（如 2026-06-24 14:30，按 {ctx.tz.region_label} 理解）: "
            ).strip()
            divination_datetime = parse_datetime_input(raw, ctx.tz)
            if divination_datetime is None:
                console.print("[yellow]时间格式无效，改用当前时间[/yellow]")
                divination_datetime = dt_now

    return coin_tosses, divination_datetime, coin_mode


# ---------------------------------------------------------------------------
# 展示
# ---------------------------------------------------------------------------

def _yao_line_display(yao: YaoInfo) -> Text:
    line = Text("━━━━━━" if yao.is_yang else "──────", style="bold white" if yao.is_yang else "white")
    if yao.is_changing:
        mark = Text(" ○ 变", style="bold yellow") if yao.is_yang else Text(" × 变", style="bold yellow")
        line.append(mark)
    return line


def display_hexagram(hexagram: HexagramInfo, title: str = "卦象") -> None:
    upper, lower = hexagram.upper_trigram, hexagram.lower_trigram
    console.print()
    console.print(
        Panel(
            f"[bold magenta]{hexagram.name}[/bold magenta]",
            title=f"[bold]{title}[/bold]",
            border_style="magenta",
            box=box.ROUNDED,
        )
    )
    tri_table = Table(show_header=False, box=None, padding=(0, 2))
    tri_table.add_column("位置", style="dim")
    tri_table.add_column("卦象")
    tri_table.add_row("上卦", f"{upper['symbol']} [bold]{upper['name']}[/bold]")
    tri_table.add_row("下卦", f"{lower['symbol']} [bold]{lower['name']}[/bold]")
    console.print(tri_table)
    console.print()

    yao_table = Table(title="六爻（自下而上）", box=box.SIMPLE_HEAD, show_lines=True)
    yao_table.add_column("爻位", style="cyan", justify="center")
    yao_table.add_column("爻值", justify="center")
    yao_table.add_column("性质", justify="center")
    yao_table.add_column("图形", justify="left")
    for yao in hexagram.yaos:
        yao_table.add_row(yao.position_name, str(yao.value), yao.label, _yao_line_display(yao))
    console.print(yao_table)

    if hexagram.has_changing and hexagram.changed_hexagram:
        chg = hexagram.changed_hexagram
        console.print()
        console.print(
            f"[yellow]变爻[/yellow]：第 {', '.join(str(p) for p in hexagram.changing_positions)} 爻 "
            f"→ 之卦 [bold]{chg.name}[/bold] "
            f"（{chg.upper_trigram['symbol']}{chg.upper_trigram['name']} / "
            f"{chg.lower_trigram['symbol']}{chg.lower_trigram['name']}）"
        )


def display_prompt(prompt: str) -> None:
    console.print()
    console.print(Rule("[bold green]AI 解读提示词（可直接复制）[/bold green]", style="green"))
    console.print()
    border = "═" * 42
    console.print(f"[dim]{border}[/dim]")
    console.print(prompt)
    console.print(f"[dim]{border}[/dim]")
    console.print()
    console.print("[dim]提示：选中上方文本区域，复制后粘贴至任意大模型对话框即可。[/dim]")


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def run_interactive() -> None:
    show_disclaimer()
    ensure_runtime()

    config = load_config()
    if not CONFIG_PATH.exists():
        detected = detect_system_timezone_name()
        config.timezone = detected
        config.region_label = label_for_timezone(detected)

    ctx, config = setup_user_context(config)
    method = select_method()

    coin_tosses, divination_dt, coin_mode = collect_divination_params(method, ctx)

    if method == "time" and divination_dt is not None:
        console.print(f"\n[dim]{format_datetime_with_tz(divination_dt, ctx.tz)}[/dim]")

    result = perform_divination(
        method,
        ctx,
        coin_tosses=coin_tosses,
        divination_datetime=divination_dt,
        coin_mode=coin_mode if method == "coin" else ctx.coin_mode,
    )

    if method == "time":
        console.print(f"\n[dim]{result.method_desc}[/dim]")
    elif method == "random":
        console.print("\n[dim]已随机生成六爻[/dim]")

    config.coin_mode = coin_mode if method == "coin" else ctx.coin_mode
    config.question = ctx.question
    config.bazi = ctx.bazi
    config.birth_datetime = ctx.birth_datetime
    config.timezone = ctx.tz.iana_name
    config.region_label = ctx.tz.region_label
    save_config(config)
    console.print(f"\n[dim]用户偏好已保存至 {CONFIG_PATH}[/dim]")

    display_hexagram(result.hexagram)
    display_prompt(result.prompt)

    console.print()
    if console.input("是否保存本次占卜记录？[y/N]: ").strip().lower() in ("y", "yes"):
        record = DivinationRecord(
            question=ctx.question,
            bazi=ctx.bazi,
            birth_datetime=ctx.birth_datetime,
            method=result.method_desc,
            divination_time=result.divination_time,
            timezone=ctx.tz.iana_name,
            hexagram=result.hexagram,
            prompt=result.prompt,
        )
        path = save_record(record)
        console.print(f"[green]已保存至 {path}[/green]")

    console.print()
    console.print(Rule(style="dim"))
    console.print("[dim]感谢使用 bagua。愿君子以自强不息。[/dim]")


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_cli_args(argv)
        if not args.interactive:
            return dispatch_headless(args)
        run_interactive()
        return 0
    except KeyboardInterrupt:
        console.print("\n[dim]已取消。[/dim]")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())