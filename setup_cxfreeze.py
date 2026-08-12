"""cx_Freeze build script for dataforge.

Usage:
    pip install cx_Freeze
    python setup_cxfreeze.py build_exe        # one-folder build -> build/exe.<platform>.<pyver>/
    python setup_cxfreeze.py bdist_msi         # Windows installer (Windows only)
    python setup_cxfreeze.py bdist_mac         # macOS .app bundle (macOS only)
    python setup_cxfreeze.py bdist_dmg         # macOS .dmg image (macOS only)

cx_Freeze cannot produce a single-file executable (see README for a
PyInstaller/Nuitka comparison) -- it always produces a folder containing the
executable plus its dependencies, which must be shipped together.
"""
import sys
from cx_Freeze import Executable, setup

build_exe_options = {
    "packages": ["dataforge", "pandas", "plotly", "jinja2", "yaml", "rich", "typer"],
    "include_files": [("src/dataforge/templates", "lib/dataforge/templates")],
    "excludes": ["tkinter", "test", "unittest"],
    "optimize": 2,
}

bdist_msi_options = {
    "target_name": "dataforge-installer",
}

executables = [
    Executable(
        "dataforge_entry.py",
        target_name="dataforge.exe" if sys.platform == "win32" else "dataforge",
        base="console",
        copyright="Copyright (c) 2026 Trystian FX",
    )
]

setup(
    name="dataforge-cli",
    version="0.1.0",
    description="Ingest, analyze, and publish datasets to HTML/WordPress.",
    options={
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options,
    },
    executables=executables,
)
