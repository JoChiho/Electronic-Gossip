"""发版校验脚本测试。"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_changelog_exists():
    assert (ROOT / "CHANGELOG.md").is_file()


def test_check_release_passes():
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_release.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout