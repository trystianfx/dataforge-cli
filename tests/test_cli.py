"""CLI-level regression tests using typer.testing.CliRunner.

These specifically guard against two bugs found via a --help completeness
audit (see issues #2 and #3):
  - #2: `build --schema-engine` silently accepted invalid values instead
    of raising an error like `schema --engine` did.
  - #3: the entire CLI crashed at startup on Typer < 0.19.0 because
    `--kind`/`--chart-kind` used typing.Literal, which Typer didn't
    support as a CLI parameter type until 0.19.0. Fixed by switching to
    plain `str` options with manual validation (consistent with how
    `--engine` and `--layout` already worked).
"""
from pathlib import Path

from typer.testing import CliRunner

from dataforge.cli import app

runner = CliRunner()
SAMPLE = Path(__file__).parent.parent / "examples" / "sample_repeaters.csv"


def test_help_does_not_crash():
    """Regression test for #3: the CLI must start regardless of whether
    the installed Typer version supports typing.Literal parameter types.
    """
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for cmd in ("ingest", "schema", "profile", "chart", "build", "wp-push"):
        assert cmd in result.output


def test_build_rejects_invalid_schema_engine(tmp_path):
    """Regression test for #2."""
    result = runner.invoke(
        app,
        ["build", str(SAMPLE), "--out-dir", str(tmp_path / "out"), "--schema-engine", "frictionles"],
    )
    assert result.exit_code != 0


def test_build_accepts_valid_schema_engine(tmp_path):
    result = runner.invoke(
        app,
        ["build", str(SAMPLE), "--out-dir", str(tmp_path / "out"), "--schema-engine", "heuristic"],
    )
    assert result.exit_code == 0
    assert (tmp_path / "out" / "index.html").exists()


def test_chart_rejects_invalid_kind(tmp_path):
    result = runner.invoke(
        app,
        ["chart", str(SAMPLE), "--x", "city", "--kind", "not_a_kind", "--out", str(tmp_path / "c.html")],
    )
    assert result.exit_code != 0


def test_chart_accepts_valid_kind(tmp_path):
    result = runner.invoke(
        app,
        ["chart", str(SAMPLE), "--x", "city", "--y", "frequency_mhz", "--kind", "bar",
         "--out", str(tmp_path / "c.html")],
    )
    assert result.exit_code == 0
    assert (tmp_path / "c.html").exists()


def test_build_rejects_invalid_chart_kind(tmp_path):
    result = runner.invoke(
        app,
        ["build", str(SAMPLE), "--out-dir", str(tmp_path / "out"), "--chart-x", "city", "--chart-kind", "bogus"],
    )
    assert result.exit_code != 0


def test_build_rejects_invalid_layout(tmp_path):
    result = runner.invoke(
        app,
        ["build", str(SAMPLE), "--out-dir", str(tmp_path / "out"), "--layout", "bogus"],
    )
    assert result.exit_code != 0


def test_build_accepts_cards_layout(tmp_path):
    result = runner.invoke(
        app,
        ["build", str(SAMPLE), "--out-dir", str(tmp_path / "out"), "--layout", "cards"],
    )
    assert result.exit_code == 0


def test_schema_rejects_invalid_engine():
    result = runner.invoke(app, ["schema", str(SAMPLE), "--engine", "bogus"])
    assert result.exit_code != 0
