# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec：bagua-gui（无控制台窗口）。"""

import os

from PyInstaller.utils.hooks import collect_all, collect_submodules

ROOT = os.path.abspath(os.path.join(SPECPATH, ".."))
block_cipher = None

hiddenimports = collect_submodules("bagua") + collect_submodules("rich")
datas = []

for pkg in ("tzdata", "lunar_python"):
    try:
        ret = collect_all(pkg)
        datas += ret[0]
        hiddenimports += ret[1]
    except Exception:
        pass

a = Analysis(
    [os.path.join(ROOT, "scripts", "bagua_gui_launcher.py")],
    pathex=[ROOT],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="bagua-gui",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)