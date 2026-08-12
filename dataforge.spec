# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for dataforge.
# Build with:  pyinstaller dataforge.spec
#
# A .spec file is used (instead of a bare `pyinstaller dataforge_entry.py`
# call) so the Jinja2 templates directory is reliably bundled -- PyInstaller
# cannot discover non-.py data files like *.j2 templates on its own.

block_cipher = None

a = Analysis(
    ["dataforge_entry.py"],
    pathex=["src"],
    binaries=[],
    datas=[("src/dataforge/templates", "dataforge/templates")],
    hiddenimports=["dataforge.cli"],
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter"],
    noarchive=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="dataforge",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
)
