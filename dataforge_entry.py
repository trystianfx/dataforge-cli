"""Standalone entry point for freezing dataforge into an executable.

PyInstaller, Nuitka, and cx_Freeze all work best against a plain script
(rather than the `console_scripts` entry point used by pip installs), so
this thin wrapper just imports and runs the Typer app. Build tools should
target this file, not `src/dataforge/cli.py` directly.
"""
from dataforge.cli import app

if __name__ == "__main__":
    app()
