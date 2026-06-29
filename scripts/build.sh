#!/usr/bin/env bash
# bagua 打包脚本（macOS / Linux）— 主要验证构建流程；正式发布以 Windows exe 为主
set -euo pipefail
cd "$(dirname "$0")/.."

CLEAN=0
SKIP_TEST=0
for arg in "$@"; do
  case "$arg" in
    --clean) CLEAN=1 ;;
    --skip-test) SKIP_TEST=1 ;;
  esac
done

VERSION=$(python -c "from bagua import __version__; print(__version__)")
echo "bagua v${VERSION} 打包开始"

if [[ "$CLEAN" == "1" ]]; then
  rm -rf build dist
  echo "已清理 build/ dist/"
fi

if [[ "$SKIP_TEST" == "0" ]]; then
  python scripts/check_release.py
  python -m ruff check bagua tests scripts
  python -m mypy bagua
  python -m pytest tests/ -q
fi

pip install -q -r requirements-build.txt
pip install -q -e .

echo "构建 bagua (CLI)..."
pyinstaller packaging/bagua.spec --noconfirm --clean

echo "构建 bagua-gui (GUI)..."
pyinstaller packaging/bagua-gui.spec --noconfirm --clean

echo ""
echo "打包完成 v${VERSION}"
ls -la dist/