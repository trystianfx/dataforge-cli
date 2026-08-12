from pathlib import Path

from dataforge.ingest import load_dataset
from dataforge.schema import infer_schema

SAMPLE = Path(__file__).parent.parent / "examples" / "sample_repeaters.csv"


def test_infer_schema_types():
    df = load_dataset(str(SAMPLE))
    schema = infer_schema(df, dataset_name="repeaters")

    fields = {f["name"]: f for f in schema["fields"]}
    assert fields["frequency_mhz"]["type"] == "number"
    assert fields["callsign"]["type"] in ("string", "categorical")
    assert fields["tone_hz"]["nullable"] is True
    assert schema["row_count"] == 20


def test_frictionless_engine_optional():
    """Schema inference via Frictionless is opt-in; skip cleanly if the
    `frictionless` extra isn't installed rather than failing the suite.
    """
    frictionless = __import__("pytest").importorskip("frictionless")
    from dataforge.schema_frictionless import infer_schema_frictionless

    result = infer_schema_frictionless(str(SAMPLE), dataset_name="repeaters")
    assert result["engine"] == "frictionless"
    assert result["column_count"] == 10
    field_names = {f["name"] for f in result["fields"]}
    assert "callsign" in field_names
