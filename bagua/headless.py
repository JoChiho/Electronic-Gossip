"""CLI 非交互模式与记录管理命令。"""

from __future__ import annotations

import sys

from rich.console import Console
from rich.table import Table

from bagua.args import CliArgs
from bagua.clipboard import copy_to_clipboard
from bagua.config import load_config, save_config
from bagua.gui_display import format_hexagram_display
from bagua.models import DivinationRecord, UserConfig, UserContext
from bagua.records import delete_record, list_records, load_record_json, save_record
from bagua.service import perform_divination
from bagua.timezone import get_timezone, label_for_timezone, parse_datetime_input

console = Console()


def _config_to_context(config: UserConfig, args: CliArgs) -> UserContext:
    tz_name = args.timezone or config.timezone
    region = label_for_timezone(tz_name)
    if config.timezone == tz_name:
        region = config.region_label
    tz = get_timezone(tz_name, region)
    calendar_mode = args.calendar or config.calendar_mode
    return UserContext(
        question=args.question if args.question is not None else config.question,
        bazi=args.bazi if args.bazi is not None else config.bazi,
        birth_datetime=(
            args.birth_datetime if args.birth_datetime is not None else config.birth_datetime
        ),
        tz=tz,
        coin_mode=args.coin_mode,
        calendar_mode=calendar_mode,
        lunar_input=args.lunar_at,
        include_hexagram_texts=config.include_hexagram_texts,
    )


def _update_config_from_args(config: UserConfig, args: CliArgs, ctx: UserContext) -> UserConfig:
    config.question = ctx.question
    config.bazi = ctx.bazi
    config.birth_datetime = ctx.birth_datetime
    config.timezone = ctx.tz.iana_name
    config.region_label = ctx.tz.region_label
    if args.method == "coin":
        config.coin_mode = args.coin_mode
    if args.calendar:
        config.calendar_mode = args.calendar
    if args.auto_bazi is not None:
        config.auto_bazi = args.auto_bazi
    return config


def run_list_records() -> int:
    records = list_records()
    if not records:
        console.print("[dim]暂无占卜记录。[/dim]")
        return 0

    table = Table(title="占卜历史记录", show_lines=True)
    table.add_column("#", justify="right", style="cyan")
    table.add_column("时间", style="dim")
    table.add_column("卦名")
    table.add_column("问题")
    table.add_column("文件", style="dim")

    for i, rec in enumerate(records, start=1):
        table.add_row(
            str(i),
            rec.saved_at or rec.divination_time,
            rec.hexagram_name,
            rec.question or "（无）",
            rec.filename,
        )
    console.print(table)
    console.print("[dim]查看：bagua --show-record <序号或文件名>[/dim]")
    return 0


def run_show_record(identifier: str) -> int:
    data = load_record_json(identifier)
    if data is None:
        console.print(f"[red]未找到记录：{identifier}[/red]")
        return 1

    console.print(f"[bold]起卦时间[/bold]：{data.get('divination_time', '')}")
    console.print(f"[bold]起卦方法[/bold]：{data.get('method', '')}")
    console.print(f"[bold]问题[/bold]：{data.get('question', '')}")
    hexagram = data.get("hexagram", {})
    console.print(f"[bold]卦名[/bold]：{hexagram.get('name', '')}")
    console.print()
    console.print(data.get("prompt", ""))
    return 0


def run_delete_record(identifier: str) -> int:
    path = delete_record(identifier)
    if path is None:
        console.print(f"[red]未找到记录：{identifier}[/red]")
        return 1
    console.print(f"[green]已删除：{path.name}[/green]")
    return 0


def run_headless_divination(args: CliArgs) -> int:
    if args.method is None:
        console.print("[red]非交互起卦需要 --method[/red]")
        return 1

    config = load_config()
    ctx = _config_to_context(config, args)

    divination_dt = None
    if args.method == "time":
        if ctx.calendar_mode == "lunar" and args.lunar_at:
            from bagua.lunar_util import parse_lunar_datetime_input

            if parse_lunar_datetime_input(args.lunar_at) is None:
                console.print(f"[red]农历时间格式无效：{args.lunar_at}[/red]")
                return 1
        elif args.at:
            divination_dt = parse_datetime_input(args.at, ctx.tz)
            if divination_dt is None:
                console.print(f"[red]时间格式无效：{args.at}[/red]")
                return 1

    auto_bazi = config.auto_bazi if args.auto_bazi is None else args.auto_bazi
    result = perform_divination(
        args.method,
        ctx,
        coin_tosses=None,
        divination_datetime=divination_dt,
        coin_mode=args.coin_mode,
        auto_bazi=auto_bazi,
    )

    config = _update_config_from_args(config, args, ctx)
    save_config(config)

    if args.output == "prompt":
        console.print(result.prompt)
    elif args.output == "hexagram":
        console.print(format_hexagram_display(result.hexagram))
    else:
        console.print(f"起卦时间：{result.divination_time}")
        console.print(f"起卦方法：{result.method_desc}")
        console.print()
        console.print(format_hexagram_display(result.hexagram))
        console.print()
        console.print(result.prompt)

    if args.copy:
        if copy_to_clipboard(result.prompt):
            console.print("\n[green]提示词已复制到剪贴板[/green]", file=sys.stderr)
        else:
            console.print("\n[yellow]剪贴板复制失败[/yellow]", file=sys.stderr)

    if args.save_record:
        path = save_record(
            DivinationRecord(
                question=ctx.question,
                bazi=ctx.bazi,
                birth_datetime=ctx.birth_datetime,
                method=result.method_desc,
                divination_time=result.divination_time,
                timezone=ctx.tz.iana_name,
                hexagram=result.hexagram,
                prompt=result.prompt,
            )
        )
        console.print(f"[green]已保存至 {path}[/green]", file=sys.stderr)

    return 0


def dispatch_headless(args: CliArgs) -> int:
    if args.list_records:
        return run_list_records()
    if args.show_record:
        return run_show_record(args.show_record)
    if args.delete_record:
        return run_delete_record(args.delete_record)
    if args.method:
        return run_headless_divination(args)
    return 1