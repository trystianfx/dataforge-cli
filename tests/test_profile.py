from pathlib import Path

import pytest

from dataforge.ingest import load_dataset
from dataforge.profile import generate_profile, generate_ydata_report_html

SAMPLE = Path(__file__).parent.parent / "examples" / "sample_repeaters.csv"


def test_generate_profile_shape():
    df = load_dataset(str(SAMPLE))
    profile = generate_profile(df, dataset_name="repeaters")
    assert profile["rows"] == len(df)
    assert profile["columns"] == len(df.columns)
    assert profile["duplicate_rows"] == 0


def test_generate_profile_missingness():
    df = load_dataset(str(SAMPLE))
    profile = generate_profile(df, dataset_name="repeaters")
    assert "tone_hz" in profile["per_column"]
    assert profile["per_column"]["tone_hz"]["missing"] >= 1


def test_generate_profile_numeric_stats_present():
    df = load_dataset(str(SAMPLE))
    profile = generate_profile(df, dataset_name="repeaters")
    assert "stats" in profile["per_column"]["frequency_mhz"]
    assert "mean" in profile["per_column"]["frequency_mhz"]["stats"]


def test_generate_profile_non_numeric_has_no_stats():
    df = load_dataset(str(SAMPLE))
    profile = generate_profile(df, dataset_name="repeaters")
    assert "stats" not in profile["per_column"]["callsign"]


def test_ydata_report_html():
    """If ydata-profiling IS installed (the [profiling] extra), verify it
    actually produces an HTML report. If it is NOT installed, verify the
    ImportError message is helpful rather than a bare traceback.
    """
    df = load_dataset(str(SAMPLE))
    try:
        import ydata_profiling  # noqa: F401
    except ImportError:
        with pytest.raises(ImportError, match="dataforge-cli\\[profiling\\]"):
            generate_ydata_report_html(df, dataset_name="repeaters")
    else:
        html = generate_ydata_report_html(df, dataset_name="repeaters")
        assert "<html" in html.lower()
