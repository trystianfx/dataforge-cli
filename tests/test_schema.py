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
    assert schema["row_count"] == 6
