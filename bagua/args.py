"""CLI 参数解析。"""

from __future__ import annotations

import argparse
from dataclasses import dataclass

from bagua.cli_guide import ARGPARSE_EPILOG


@dataclass
class CliArgs:
    interactive: bool = True
    method: str | None = None
    question: str | None = None
    bazi: str | None = None
    birth_datetime: str | None = None
    timezone: str | None = None
    divination_timezone: str | None = None
    coin_mode: str | None = None
    at: str | None = None
    save_record: bool = False
    output: str = "full"
    copy: bool = False
    no_copy: bool = False
    list_records: bool = False
    show_record: str | None = None
    delete_record: str | None = None
    search: str | None = None
    export_record: str | None = None
    export_records: bool = False
    markdown_out: str | None = None
    calendar: str | None = None
    lunar_at: str | None = None
    auto_bazi: bool | None = None
    nums: str | None = None
    upper: int | None = None
    lower: int | None = None
    changing: int | None = None
    yarrow_show_process: bool | None = None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bagua",
        description="易经八卦占卜 CLI — 起卦并生成 AI 解读提示词",
        epilog=ARGPARSE_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-m", "--method",
        choices=["coin", "time", "random", "number", "manual", "yarrow"],
        help="起卦方式（指定后进入非交互模式）",
    )
    parser.add_argument(
        "--nums",
        metavar="NUMS",
        help='数字起卦报数，2～3 个正整数，如 "3 8 5"（省略时读取 config.json）',
    )
    parser.add_argument("--upper", type=int, metavar="N", help="手动选卦上卦序号 1～8（乾1…坤8）")
    parser.add_argument("--lower", type=int, metavar="N", help="手动选卦下卦序号 1～8")
    parser.add_argument(
        "--changing",
        type=int,
        metavar="N",
        help="手动选卦动爻 1～6；0 或省略为无动爻（静卦）",
    )
    parser.add_argument(
        "--yarrow-show-process",
        action="store_true",
        help="蓍草法输出演卦过程（省略时读取 config.json 中的 yarrow_show_process）",
    )
    parser.add_argument("-q", "--question", help="占卜问题")
    parser.add_argument("--bazi", help="生辰八字")
    parser.add_argument("--birth-datetime", help="出生日期时间")
    parser.add_argument("--timezone", help="出生时区 IANA 名，如 Asia/Shanghai")
    parser.add_argument(
        "--divination-timezone",
        help="起卦时区 IANA 名（默认与 --timezone 或 config 相同）",
    )
    parser.add_argument(
        "--coin-mode",
        choices=["manual", "auto"],
        default=None,
        help="铜钱法模式；省略时读取 config.json 中的 coin_mode",
    )
    parser.add_argument("--at", metavar="TIME", help="时间起卦指定时刻（公历），如 2026-06-24 14:30")
    parser.add_argument(
        "--calendar",
        choices=["solar", "lunar"],
        help="时间起卦历法：solar 公历（默认）/ lunar 农历",
    )
    parser.add_argument(
        "--lunar-at",
        metavar="TIME",
        help="农历起卦时刻，如 2026-05-10 14:30（需配合 --calendar lunar）",
    )
    parser.add_argument(
        "--auto-bazi",
        action="store_true",
        help="从出生时间自动排八字（默认开启，可用 --no-auto-bazi 关闭）",
    )
    parser.add_argument(
        "--no-auto-bazi",
        action="store_true",
        help="关闭自动排八字",
    )
    parser.add_argument("--save", action="store_true", help="自动保存占卜记录")
    parser.add_argument(
        "--output",
        choices=["full", "prompt", "hexagram"],
        default="full",
        help="输出内容（非交互模式）",
    )
    parser.add_argument("--copy", action="store_true", help="将提示词复制到剪贴板")
    parser.add_argument(
        "--no-copy",
        action="store_true",
        help="禁止自动复制（覆盖 config 中的 auto_copy_prompt）",
    )
    parser.add_argument("--list-records", action="store_true", help="列出历史占卜记录")
    parser.add_argument("--show-record", metavar="ID", help="查看记录（文件名或序号）")
    parser.add_argument("--delete-record", metavar="ID", help="删除记录（文件名或序号）")
    parser.add_argument(
        "--search",
        metavar="QUERY",
        help="搜索记录（配合 --list-records 或 --export-records）",
    )
    parser.add_argument("--export-record", metavar="ID", help="导出单条记录为 Markdown")
    parser.add_argument(
        "--export-records",
        action="store_true",
        help="导出全部或搜索结果为 Markdown（可用 --search 筛选）",
    )
    parser.add_argument(
        "-o", "--markdown-out",
        metavar="PATH",
        help="Markdown 导出路径（配合 --export-record / --export-records）",
    )
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="强制交互模式",
    )
    return parser


def parse_cli_args(argv: list[str] | None = None) -> CliArgs:
    parser = build_parser()
    ns = parser.parse_args(argv)

    headless_triggers = any([
        ns.method,
        ns.list_records,
        ns.show_record,
        ns.delete_record,
        ns.export_record,
        ns.export_records,
    ])

    return CliArgs(
        interactive=ns.interactive or not headless_triggers,
        method=ns.method,
        question=ns.question,
        bazi=ns.bazi,
        birth_datetime=ns.birth_datetime,
        timezone=ns.timezone,
        divination_timezone=ns.divination_timezone,
        coin_mode=ns.coin_mode,
        no_copy=ns.no_copy,
        at=ns.at,
        save_record=ns.save,
        output=ns.output,
        copy=ns.copy,
        list_records=ns.list_records,
        show_record=ns.show_record,
        delete_record=ns.delete_record,
        search=ns.search,
        export_record=ns.export_record,
        export_records=ns.export_records,
        markdown_out=ns.markdown_out,
        calendar=ns.calendar,
        lunar_at=ns.lunar_at,
        auto_bazi=False if ns.no_auto_bazi else (True if ns.auto_bazi else None),
        nums=ns.nums,
        upper=ns.upper,
        lower=ns.lower,
        changing=ns.changing,
        yarrow_show_process=True if ns.yarrow_show_process else None,
    )