"""打包配置冒烟测试（不执行完整 PyInstaller 构建）。"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_packaging_specs_exist():
    assert (ROOT / "packaging" / "bagua.spec").is_file()
    assert (ROOT / "packaging" / "bagua-gui.spec").is_file()


def test_build_scripts_exist():
    assert (ROOT / "scripts" / "build.ps1").is_file()
    assert (ROOT / "scripts" / "build.sh").is_file()
    assert (ROOT / "scripts" / "bagua_gui_launcher.py").is_file()


def test_spec_references_project_root():
    cli_spec = (ROOT / "packaging" / "bagua.spec").read_text(encoding="utf-8")
    gui_spec = (ROOT / "packaging" / "bagua-gui.spec").read_text(encoding="utf-8")
    assert "SPECPATH" in cli_spec
    assert "bagua.py" in cli_spec
    assert "bagua_gui_launcher.py" in gui_spec