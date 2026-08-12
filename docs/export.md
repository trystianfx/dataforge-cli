# Export

Writes a DataFrame or an arbitrary dict (e.g. an inferred schema or
profile) out as CSV, JSON, YAML, an HTML `<table>` fragment, or a list of
plain-dict records. This module has no CLI command of its own -- it's
called internally by `dataforge build` and is also usable directly as a
library.

## Functions

| Function | Input | Output |
|---|---|---|
| `to_csv(df, out_path)` | DataFrame | Writes a CSV file, returns the `Path` |
| `dict_to_json(data, out_path)` | dict | Writes pretty-printed JSON, returns the `Path` |
| `dict_to_yaml(data, out_path)` | dict | Writes YAML, returns the `Path` |
| `df_to_json_records(df, out_path)` | DataFrame | Writes a JSON array of row-records, returns the `Path` |
| `df_to_html_table(df, table_id=..., max_rows=200)` | DataFrame | Returns an HTML `<table>` string (not written to disk) |
| `df_to_records(df, max_rows=200)` | DataFrame | Returns a `list[dict]`, NaN converted to `None` -- feeds the `cards`/`grid` render layouts |

## Python API

```python
from dataforge.ingest import load_dataset
from dataforge.export import (
    to_csv, dict_to_json, dict_to_yaml, df_to_json_records,
    df_to_html_table, df_to_records,
)

df = load_dataset("examples/sample_repeaters.csv")

to_csv(df, "output/repeaters.csv")
df_to_json_records(df, "output/repeaters.json")

table_html = df_to_html_table(df, max_rows=50)     # embed in your own template
records = df_to_records(df)                        # [{'callsign': 'WW7PSR', ...}, ...]

dict_to_json({"generated_by": "dataforge"}, "output/meta.json")
dict_to_yaml({"generated_by": "dataforge"}, "output/meta.yaml")
```

`max_rows=None` on `df_to_html_table` / `df_to_records` exports every row
instead of truncating to the default 200 -- use with care on very large
datasets, since the whole table/card set renders into one static HTML
page with no pagination.

## Working example: exporting only a filtered subset

```python
from dataforge.ingest import load_dataset
from dataforge.export import to_csv, df_to_html_table

df = load_dataset("examples/sample_repeaters.csv")
usa_only = df[df["country"] == "USA"]

to_csv(usa_only, "output/repeaters_usa.csv")
html = df_to_html_table(usa_only, table_id="usa-repeaters")
```

Because every export function takes a plain `DataFrame`, you can filter,
sort, or transform with regular pandas before exporting -- dataforge's
export layer doesn't need to know about your filtering logic.

## See also

- [pandas `to_csv`/`to_json`/`to_html` docs](https://pandas.pydata.org/docs/reference/frame.html) -- for output options (compression, custom separators, orient variants) beyond dataforge's thin wrappers. `df_to_html_table` and `df_to_records` are the only functions here with dataforge-specific behavior (row truncation, NaN handling); the rest pass straight through to pandas.
