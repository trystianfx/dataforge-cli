# Schema

Infers a portable schema description for a dataset: field types,
nullability, cardinality, and basic constraints. Two interchangeable
engines are available.

## Engines

| Engine | Flag | Dependencies | Output |
|---|---|---|---|
| Heuristic (default) | `--engine heuristic` | none | pandas-dtype-based type/constraint guesses |
| Frictionless | `--engine frictionless` | `pip install dataforge-cli[frictionless]` | Standards-compliant Table Schema, plus `--validate` for row/cell-level validation |

### Heuristic engine logical types

`string`, `integer`, `number`, `boolean`, `datetime`, `categorical`
(low-cardinality object columns), `email`, `url`. Detection is sampling
and regex-based -- see the "Design notes" caveat in the main README before
relying on it for anything load-bearing.

## CLI usage

```bash
# Print schema to stdout (heuristic engine)
dataforge schema examples/sample_repeaters.csv

# Save as JSON or YAML
dataforge schema examples/sample_repeaters.csv --out output/schema.json
dataforge schema examples/sample_repeaters.csv --out output/schema.yaml

# Name the dataset in the output
dataforge schema examples/sample_repeaters.csv --dataset-name repeaters

# Frictionless engine + validation report
dataforge schema examples/sample_repeaters.csv --engine frictionless --validate --out output/schema.json
```

**Options:**

| Flag | Default | Description |
|---|---|---|
| `--out` | stdout | Output file; `.yaml`/`.yml` extension writes YAML, anything else writes JSON |
| `--dataset-name` | filename stem | Name embedded in the output schema |
| `--engine` | `heuristic` | `heuristic` or `frictionless` |
| `--validate` | off | Also run Frictionless validation (requires `--engine frictionless`) |

## Python API

```python
from dataforge.ingest import load_dataset
from dataforge.schema import infer_schema

df = load_dataset("examples/sample_repeaters.csv")
result = infer_schema(df, dataset_name="repeaters")

result["row_count"]      # 20
result["column_count"]   # 10
result["fields"][0]
# {'name': 'callsign', 'pandas_dtype': 'object', 'type': 'string',
#  'nullable': False, 'null_count': 0, 'unique_count': 20,
#  'sample_values': ['WW7PSR', 'WW7MST', ...], 'constraints': {...}}
```

Frictionless engine (requires the `frictionless` extra):

```python
from dataforge.schema_frictionless import infer_schema_frictionless, validate_source

result = infer_schema_frictionless("examples/sample_repeaters.csv", dataset_name="repeaters")
print(result["engine"])          # "frictionless"
print(result["table_schema"])    # raw Frictionless Table Schema dict

report = validate_source("examples/sample_repeaters.csv")
print(report["valid"])
```

## Working example: nullable-field detection

```python
from dataforge.ingest import load_dataset
from dataforge.schema import infer_schema

df = load_dataset("examples/sample_repeaters.csv")
schema = infer_schema(df)

nullable_fields = [f["name"] for f in schema["fields"] if f["nullable"]]
print(nullable_fields)   # ['tone_hz'] -- two rows have a blank tone
```

## See also

- [Frictionless Framework docs](https://framework.frictionlessdata.io/) -- for the full Table Schema spec, custom constraint definitions, and multi-table `Package` support beyond what `--engine frictionless` currently exposes.
