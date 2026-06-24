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
from bagua.cli_guide import (
    METHOD_LABELS,
    show_coin_value_legend,
    show_completion_guide,
    show_method_guide,
    show_pre_result_summary,
    show_quick_start,
    show_random_guide,
    show_step,
    show_time_guide,
    show_user_fields_help,
)
from bagua.config import CONFIG_PATH, load_config, save_config
from bagua.data import YAO_POSITIONS, YAO_VALUE_NAMES
from bagua.divination import coin_tosses_to_display, parse_coin_input, simulate_coin_toss
from bagua.headless import dispatch_headless
from bagua.models import DivinationRecord, UserConfig, UserContext, YaoInfo
from bagua.models import HexagramInfo
from bagua.records import save_record
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
    console.print("\n[bold]请选择时区 / 地区[/bold] [dim]（决定起卦时间的标注）[/dim]")
    for i, (tz_name, label) in enumerate(TIMEZONE_PRESETS, start=1):
        mark = " [green]← 当前[/green]" if tz_name == current else ""
        console.print(f"  [cyan]{i:>2}[/cyan]  {label}  [dim]({tz_name})[/dim]{mark}")
    console.print("  [cyan] 0[/cyan]  手动输入 IANA 时区名称（如 Europe/Berlin）")
    if not is_tzdata_available():
        console.print("  [dim]当前为固定偏移模式，自定义时区仅支持列表内预设[/dim]")
    console.print("  [dim]直接回车 = 保持当前时区[/dim]\n")

    while True:
        choice = console.input(f"请输入选项 [当前 {current}]: ").strip()
        if not choice:
            return current, label_for_timezone(current)
        if choice == "0":
            raw = console.input("IANA 时区名称: ").strip()
            if validate_timezone_name(raw):
                return raw, label_for_timezone(raw)
            console.print("[red]无效时区。请输入列表中的名称，或安装 tzdata 后重试。[/red]")
            continue
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(TIMEZONE_PRESETS):
                return TIMEZONE_PRESETS[idx - 1]
        console.print("[red]无效选项。请输入列表中的数字，或直接回车。[/red]")


def _prompt_with_default(label: str, default: str, hint: str = "") -> str:
    hint_text = f" [dim]{hint}[/dim]" if hint else ""
    if default:
        console.print(f"[bold]{label}[/bold]{hint_text}")
        raw = console.input(f"  直接回车沿用 [dim]{default}[/dim]，或输入新值: ").strip()
    else:
        raw = console.input(f"[bold]{label}[/bold]{hint_text}: ").strip()
    return raw if raw else default


def setup_user_context(config: UserConfig) -> tuple[UserContext, UserConfig]:
    show_step(console, 1, "个人信息")
    tz = get_timezone(config.timezone, config.region_label)

    if CONFIG_PATH.exists() and any([config.question, config.bazi, config.birth_datetime]):
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
        console.print("[dim]直接回车 = 沿用以上信息；输入 n = 重新填写[/dim]")
        use_saved = console.input("使用已保存信息？[Y/n]: ").strip().lower()
        if use_saved in ("", "y", "yes"):
            console.print("[green]✓[/green] 已沿用保存的信息")
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

    show_user_fields_help(console)

    if console.input(f"需要修改时区？当前 [bold]{config.region_label}[/bold] [y/N]: ").strip().lower() in ("y", "yes"):
        tz_name, region_label = select_timezone(config.timezone)
        config.timezone = tz_name
        config.region_label = region_label
        tz = get_timezone(tz_name, region_label)

    config.birth_datetime = _prompt_with_default(
        "出生日期时间",
        config.birth_datetime,
        "可选 · 格式 1990-01-01 08:00",
    )
    config.bazi = _prompt_with_default("生辰八字", config.bazi, "可选 · 如 庚午年 辛巳月 甲子日")
    config.question = _prompt_with_default("占卜问题", config.question, "建议填写 · 如「近期是否该跳槽」")

    console.print("[green]✓[/green] 个人信息已确认")
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
    show_step(console, 2, "选择起卦方式")
    show_method_guide(console)
    console.print("[dim]请输入数字 1–3，然后回车确认[/dim]\n")

    mapping = {"1": "coin", "2": "time", "3": "random"}
    while True:
        choice = console.input("你的选择 [1/2/3]: ").strip()
        if choice in mapping:
            console.print(f"[green]✓[/green] 已选择：{METHOD_LABELS[mapping[choice]]}")
            return mapping[choice]  # type: ignore[return-value]
        console.print("[red]请输入 1、2 或 3。[/red]")


def _select_coin_mode(default: str) -> str:
    console.print("\n[bold]铜钱法 · 投掷方式[/bold]")
    console.print("  [cyan]1[/cyan]  手动输入 — 自己掷币，每爻输入三个 1 或 2")
    console.print("  [cyan]2[/cyan]  自动模拟 — 程序代掷，适合快速出卦")
    default_label = "手动" if default == "manual" else "自动"
    console.print(f"  [dim]直接回车 = 沿用上次：{default_label}[/dim]\n")

    mapping = {"1": "manual", "2": "auto", "": default}
    while True:
        choice = console.input("请选择 [1/2]: ").strip()
        if choice in mapping:
            label = "手动输入" if mapping[choice] == "manual" else "自动模拟"
            console.print(f"[green]✓[/green] {label}")
            return mapping[choice]
        console.print("[red]请输入 1、2，或直接回车。[/red]")


def collect_coin_tosses(coin_mode: str) -> tuple[list[list[int]], str]:
    mode = _select_coin_mode(coin_mode)
    tosses: list[list[int]] = []

    console.print()
    if mode == "manual":
        show_coin_value_legend(console)
        console.print()
        for pos in range(1, 7):
            while True:
                console.print(f"[dim]进度 {pos}/6[/dim]")
                raw = console.input(
                    f"[bold]第 {pos} 爻[/bold]（{YAO_POSITIONS[pos - 1]}）输入三个 1 或 2: "
                ).strip()
                coins = parse_coin_input(raw)
                if coins is None:
                    console.print(
                        "[red]格式不对。[/red] 需要恰好三个数字，用空格隔开，"
                        "例如 [bold]1 2 1[/bold]（1=阳面，2=阴面）"
                    )
                    continue
                tosses.append(coins)
                val = sum(coins)
                console.print(
                    f"  [green]✓[/green] {coin_tosses_to_display(coins)} "
                    f"→ 爻值 [bold]{val}[/bold]（{YAO_VALUE_NAMES[val]}）\n"
                )
                break
    else:
        console.print("[dim]自动模拟中，共六爻…[/dim]\n")
        for pos in range(1, 7):
            points = simulate_coin_toss()
            tosses.append(points)
            val = sum(points)
            console.print(
                f"  [{pos}/6] {YAO_POSITIONS[pos - 1]}: {coin_tosses_to_display(points)} "
                f"→ [bold]{val}[/bold]（{YAO_VALUE_NAMES[val]}）"
            )

    return tosses, mode


def collect_divination_params(
    method: str,
    ctx: UserContext,
) -> tuple[list[list[int]] | None, object | None, str]:
    show_step(console, 3, "起卦操作")

    coin_tosses: list[list[int]] | None = None
    divination_datetime = None
    coin_mode = ctx.coin_mode

    if method == "coin":
        coin_tosses, coin_mode = collect_coin_tosses(ctx.coin_mode)
    elif method == "time":
        dt_now = now_in_timezone(ctx.tz)
        show_time_guide(console, ctx.tz.region_label, format_datetime_with_tz(dt_now, ctx.tz))
        console.print()
        if console.input("使用当前时间起卦？[Y/n]: ").strip().lower() not in ("n", "no"):
            divination_datetime = dt_now
            console.print("[green]✓[/green] 将使用当前时间")
        else:
            raw = console.input("请输入时间（如 2026-06-24 14:30）: ").strip()
            divination_datetime = parse_datetime_input(raw, ctx.tz)
            if divination_datetime is None:
                console.print("[yellow]时间格式无效，已自动改用当前时间[/yellow]")
                divination_datetime = dt_now
            else:
                console.print(f"[green]✓[/green] 将使用 {format_datetime_with_tz(divination_datetime, ctx.tz)}")
    elif method == "random":
        show_random_guide(console)
        console.print("[green]✓[/green] 准备随机起卦")

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
    console.print("[dim]六爻自下而上阅读；带「变」的为变爻，会影响之卦。[/dim]")
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
    console.print(Rule("[bold green]步骤 4/4 · AI 解读提示词[/bold green]", style="green"))
    console.print("[dim]用鼠标拖选下方文本 → Ctrl+C 复制 → 粘贴到大模型[/dim]")
    console.print()
    border = "═" * 42
    console.print(f"[dim]{border}[/dim]")
    console.print(prompt)
    console.print(f"[dim]{border}[/dim]")


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def run_interactive() -> None:
    show_disclaimer()
    ensure_runtime()

    config = load_config()
    first_run = not CONFIG_PATH.exists()
    if first_run:
        detected = detect_system_timezone_name()
        config.timezone = detected
        config.region_label = label_for_timezone(detected)

    show_quick_start(console, first_run=first_run)

    ctx, config = setup_user_context(config)
    method = select_method()

    coin_tosses, divination_dt, coin_mode = collect_divination_params(method, ctx)

    show_pre_result_summary(
        console,
        METHOD_LABELS[method],
        ctx.question,
        ctx.tz.region_label,
    )

    result = perform_divination(
        method,
        ctx,
        coin_tosses=coin_tosses,
        divination_datetime=divination_dt,
        coin_mode=coin_mode if method == "coin" else ctx.coin_mode,
    )

    if method == "time":
        console.print(f"\n[dim]{result.method_desc}[/dim]")

    config.coin_mode = coin_mode if method == "coin" else ctx.coin_mode
    config.question = ctx.question
    config.bazi = ctx.bazi
    config.birth_datetime = ctx.birth_datetime
    config.timezone = ctx.tz.iana_name
    config.region_label = ctx.tz.region_label
    save_config(config)
    console.print(f"\n[dim]偏好已保存至 {CONFIG_PATH}[/dim]")

    show_step(console, 4, "查看结果")
    display_hexagram(result.hexagram)
    display_prompt(result.prompt)
    show_completion_guide(console)

    console.print()
    console.print("[dim]是否保存本次占卜？输入 y 保存，直接回车跳过[/dim]")
    if console.input("保存记录？[y/N]: ").strip().lower() in ("y", "yes"):
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
        console.print(f"[green]✓ 已保存至 {path}[/green]")
        console.print("[dim]日后可用 bagua --list-records 查看[/dim]")

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
        console.print("\n[dim]已取消。下次可直接运行 bagua 继续，或使用 bagua -m random 快速起卦。[/dim]")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())