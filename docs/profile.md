# Profile

Analyzes a dataset and produces summary statistics: shape, missingness,
duplicate rows, and per-column descriptive stats for numeric columns.

## CLI usage

```bash
dataforge profile examples/sample_repeaters.csv
dataforge profile examples/sample_repeaters.csv --out output/profile.json
dataforge profile examples/sample_repeaters.csv --out output/profile.yaml --dataset-name repeaters
```

**Options:**

| Flag | Default | Description |
|---|---|---|
| `--out` | stdout | Output file; `.yaml`/`.yml` writes YAML, anything else writes JSON |
| `--dataset-name` | filename stem | Name embedded in the output |

## Python API

```python
from dataforge.ingest import load_dataset
from dataforge.profile import generate_profile

df = load_dataset("examples/sample_repeaters.csv")
profile = generate_profile(df, dataset_name="repeaters")

profile["rows"]                 # 20
profile["columns"]              # 10
profile["duplicate_rows"]       # 0
profile["memory_usage_bytes"]   # e.g. 9607
profile["per_column"]["tone_hz"]
# {'missing': 2, 'missing_pct': 10.0, 'unique': 11,
#  'stats': {'count': 18.0, 'mean': ..., 'std': ..., 'min': ..., 'max': ...}}
```

`generate_profile` only computes `stats` for numeric columns; string/object
columns get `missing`, `missing_pct`, and `unique` only.

## Optional: full interactive report (ydata-profiling)

For a much richer, browsable HTML report (distributions, correlations,
data-quality alerts) instead of the lightweight JSON summary above:

```bash
pip install dataforge-cli[profiling]
```

```python
from dataforge.ingest import load_dataset
from dataforge.profile import generate_ydata_report_html

df = load_dataset("examples/sample_repeaters.csv")
html = generate_ydata_report_html(df, dataset_name="repeaters")
open("output/repeaters_full_report.html", "w").write(html)
```

There is no CLI flag for this yet (see the Roadmap in the main README) --
call `generate_ydata_report_html` directly as shown above until that
lands.

## Working example: flagging high-missingness columns

```python
from dataforge.ingest import load_dataset
from dataforge.profile import generate_profile

df = load_dataset("examples/sample_repeaters.csv")
profile = generate_profile(df)

flagged = {
    col: stats["missing_pct"]
    for col, stats in profile["per_column"].items()
    if stats["missing_pct"] > 5
}
print(flagged)   # {'tone_hz': 10.0}
```

## See also

- [ydata-profiling docs](https://docs.profiling.ydata.ai/) -- for report customization (minimal mode, sensitive-data redaction, comparison reports between two datasets) beyond the single `generate_ydata_report_html` call dataforge wraps.
