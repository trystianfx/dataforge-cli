from pathlib import Path

from dataforge.export import to_csv, dict_to_json, dict_to_yaml
from dataforge.ingest import load_dataset

SAMPLE = Path(__file__).parent.parent / "examples" / "sample_repeaters.csv"


def test_export_round_trip(tmp_path):
    df = load_dataset(str(SAMPLE))

    csv_out = to_csv(df, tmp_path / "out.csv")
    assert csv_out.exists()

    json_out = dict_to_json({"a": 1, "b": [1, 2, 3]}, tmp_path / "out.json")
    assert json_out.exists()

    yaml_out = dict_to_yaml({"a": 1, "b": [1, 2, 3]}, tmp_path / "out.yaml")
    assert yaml_out.exists()
