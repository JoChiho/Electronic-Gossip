#!/usr/bin/env python3
"""校验版本号与 CHANGELOG 是否一致，供发版前检查。"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = ROOT / "CHANGELOG.md"


def _read_version() -> str:
    from bagua import __version__

    return __version__


def _changelog_top_version() -> str | None:
    if not CHANGELOG.is_file():
        return None
    text = CHANGELOG.read_text(encoding="utf-8")
    match = re.search(r"^## \[(\d+\.\d+\.\d+)\]", text, re.MULTILINE)
    return match.group(1) if match else None


def main() -> int:
    version = _read_version()
    changelog_version = _changelog_top_version()

    errors: list[str] = []
    if not CHANGELOG.is_file():
        errors.append(f"缺少 {CHANGELOG.relative_to(ROOT)}")
    elif changelog_version is None:
        errors.append("CHANGELOG.md 未找到 ## [X.Y.Z] 格式版本标题")
    elif changelog_version != version:
        errors.append(
            f"版本不一致：bagua.__version__={version}，CHANGELOG 最新={changelog_version}"
        )

    if errors:
        for msg in errors:
            print(f"check_release: {msg}", file=sys.stderr)
        return 1

    print(f"check_release: OK v{version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())