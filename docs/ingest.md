# Ingest

Loads a dataset from a local file or a remote URL into a normalized
`pandas.DataFrame`, regardless of source format.

## Supported formats

| Extension | Backing reader | Notes |
|---|---|---|
| `.csv` | `pandas.read_csv` | Standard comma-separated |
| `.tsv` | `pandas.read_csv(sep="\t")` | Tab-separated |
| `.json` | `json.loads` + `pandas.json_normalize` | Accepts a top-level list of records, or a dict containing `records`/`data`/`items`/`rows`, or a single flat dict (wrapped into one row) |
| `.yaml` / `.yml` | `yaml.safe_load` + `pandas.json_normalize` | Same record-shape rules as JSON |
| `.xlsx` / `.xls` | `pandas.read_excel` | Requires `openpyxl` (installed by default) |
| `.parquet` | `pandas.read_parquet` | Requires a parquet engine available to pandas |

Remote sources: pass an `http://` or `https://` URL instead of a local
path; the file is fetched with a 30-second timeout and dispatched to the
same format handlers based on the URL's extension.

## CLI usage

```bash
dataforge ingest examples/sample_repeaters.csv
dataforge ingest examples/sample_repeaters.csv --rows 10
dataforge ingest https://example.com/data.json
```

**Options:**

| Flag | Default | Description |
|---|---|---|
| `--rows` | `5` | Number of preview rows to print |

`ingest` only previews the data (shape + a `rich` table of the first N
rows) -- it doesn't write any files. Use `dataforge build` to run ingest
as part of the full pipeline and persist outputs.

## Python API

```python
from dataforge.ingest import load_dataset, IngestError

df = load_dataset("examples/sample_repeaters.csv")
print(df.shape)          # (20, 10)
print(df.columns.tolist())

# Remote source
df = load_dataset("https://example.com/dataset.csv")

# Error handling
try:
    load_dataset("missing.csv")
except IngestError as e:
    print(f"Could not load dataset: {e}")
```

`load_dataset(source: str) -> pandas.DataFrame` is the entire public API
of this module. It raises `dataforge.ingest.IngestError` for missing files
or unsupported extensions.

## Working example: mixed JSON shapes

```python
import json
from dataforge.ingest import load_dataset

# All three of these JSON shapes are accepted:
json.dump([{"a": 1}, {"a": 2}], open("list.json", "w"))
json.dump({"records": [{"a": 1}, {"a": 2}]}, open("wrapped.json", "w"))
json.dump({"a": 1, "b": 2}, open("single.json", "w"))

load_dataset("list.json")      # 2 rows
load_dataset("wrapped.json")   # 2 rows
load_dataset("single.json")    # 1 row
```

## See also

- [pandas I/O documentation](https://pandas.pydata.org/docs/user_guide/io.html) -- for reader options beyond what dataforge exposes (custom delimiters, sheet selection, dtype overrides, etc.). If you need fine control pandas doesn't get from `load_dataset`, load the DataFrame yourself and pass it directly to `dataforge.schema.infer_schema` / `dataforge.profile.generate_profile` instead of going through the CLI.
