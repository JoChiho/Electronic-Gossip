"""CLI 参数解析。"""

from __future__ import annotations

import argparse
from dataclasses import dataclass


@dataclass
class CliArgs:
    interactive: bool = True
    method: str | None = None
    question: str | None = None
    bazi: str | None = None
    birth_datetime: str | None = None
    timezone: str | None = None
    coin_mode: str = "auto"
    at: str | None = None
    save_record: bool = False
    output: str = "full"
    copy: bool = False
    list_records: bool = False
    show_record: str | None = None
    delete_record: str | None = None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bagua",
        description="易经八卦占卜 CLI — 起卦并生成 AI 解读提示词",
    )
    parser.add_argument(
        "-m", "--method",
        choices=["coin", "time", "random"],
        help="起卦方式（指定后进入非交互模式）",
    )
    parser.add_argument("-q", "--question", help="占卜问题")
    parser.add_argument("--bazi", help="生辰八字")
    parser.add_argument("--birth-datetime", help="出生日期时间")
    parser.add_argument("--timezone", help="IANA 时区名，如 Asia/Shanghai")
    parser.add_argument(
        "--coin-mode",
        choices=["manual", "auto"],
        default="auto",
        help="铜钱法模式（非交互默认 auto）",
    )
    parser.add_argument("--at", metavar="TIME", help="时间起卦指定时刻，如 2026-06-24 14:30")
    parser.add_argument("--save", action="store_true", help="自动保存占卜记录")
    parser.add_argument(
        "--output",
        choices=["full", "prompt", "hexagram"],
        default="full",
        help="输出内容（非交互模式）",
    )
    parser.add_argument("--copy", action="store_true", help="将提示词复制到剪贴板")
    parser.add_argument("--list-records", action="store_true", help="列出历史占卜记录")
    parser.add_argument("--show-record", metavar="ID", help="查看记录（文件名或序号）")
    parser.add_argument("--delete-record", metavar="ID", help="删除记录（文件名或序号）")
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
    ])

    return CliArgs(
        interactive=ns.interactive or not headless_triggers,
        method=ns.method,
        question=ns.question,
        bazi=ns.bazi,
        birth_datetime=ns.birth_datetime,
        timezone=ns.timezone,
        coin_mode=ns.coin_mode,
        at=ns.at,
        save_record=ns.save,
        output=ns.output,
        copy=ns.copy,
        list_records=ns.list_records,
        show_record=ns.show_record,
        delete_record=ns.delete_record,
    )