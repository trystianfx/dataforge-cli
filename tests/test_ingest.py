from pathlib import Path

from dataforge.ingest import load_dataset

SAMPLE = Path(__file__).parent.parent / "examples" / "sample_repeaters.csv"


def test_load_csv_shape():
    df = load_dataset(str(SAMPLE))
    assert df.shape[0] == 20
    assert "callsign" in df.columns
    assert set(df["country"].unique()) == {"USA", "Canada", "United Kingdom"}
