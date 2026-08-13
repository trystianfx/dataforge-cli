import pytest

from dataforge.charts import ChartError, VALID_CHART_KINDS, build_chart_html
from dataforge.ingest import load_dataset
from pathlib import Path

SAMPLE = Path(__file__).parent.parent / "examples" / "sample_repeaters.csv"


@pytest.mark.parametrize("kind", VALID_CHART_KINDS)
def test_build_chart_html_all_kinds(kind):
    df = load_dataset(str(SAMPLE))
    y = "frequency_mhz" if kind in ("bar", "line", "scatter", "pie", "box") else None
    html = build_chart_html(df, x="city", y=y, kind=kind)
    assert "<div" in html
    assert "plotly" in html.lower()


def test_build_chart_html_invalid_column_raises():
    df = load_dataset(str(SAMPLE))
    with pytest.raises(ChartError):
        build_chart_html(df, x="not_a_real_column", kind="bar")


def test_build_chart_html_invalid_kind_raises():
    df = load_dataset(str(SAMPLE))
    with pytest.raises(ChartError):
        build_chart_html(df, x="city", kind="not_a_real_kind")


def test_build_chart_html_offline_embed_is_larger():
    df = load_dataset(str(SAMPLE))
    cdn_html = build_chart_html(df, x="city", y="frequency_mhz", include_plotlyjs="cdn")
    offline_html = build_chart_html(df, x="city", y="frequency_mhz", include_plotlyjs=True)
    assert len(offline_html) > len(cdn_html)
