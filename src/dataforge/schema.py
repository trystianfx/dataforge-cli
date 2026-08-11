"""Schema inference: analyze a DataFrame and produce a portable schema
description (inspired by the Frictionless Table Schema spec) that can be
serialized to JSON or YAML.

For each column we infer:
  - a pandas dtype and a normalized "logical type" (integer, number,
    boolean, date, datetime, string, categorical, email, url)
  - nullability and null count
  - uniqueness / cardinality
  - basic constraints (min/max for numeric & date columns, max length for
    strings, the value set for low-cardinality categoricals)
  - a handful of sample values for human review
"""
from __future__ import annotations

import re
import warnings
from typing import Any

import pandas as pd

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
URL_RE = re.compile(r"^https?://", re.IGNORECASE)

CATEGORICAL_MAX_UNIQUE_RATIO = 0.2
CATEGORICAL_MAX_UNIQUE_COUNT = 50
SAMPLE_SIZE = 5


def _logical_type(series: pd.Series) -> str:
    non_null = series.dropna()
    if non_null.empty:
        return "string"

    if pd.api.types.is_bool_dtype(series):
        return "boolean"
    if pd.api.types.is_integer_dtype(series):
        return "integer"
    if pd.api.types.is_float_dtype(series):
        return "number"
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"

    # Try to coerce object columns to datetime; fall back gracefully.
    if series.dtype == object:
        sample = non_null.astype(str).head(20)
        if sample.map(lambda v: bool(EMAIL_RE.match(v))).all():
            return "email"
        if sample.map(lambda v: bool(URL_RE.match(v))).all():
            return "url"
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                pd.to_datetime(sample, errors="raise")
            return "datetime"
        except (ValueError, TypeError):
            pass

        unique_ratio = series.nunique(dropna=True) / max(len(non_null), 1)
        if (
            series.nunique(dropna=True) <= CATEGORICAL_MAX_UNIQUE_COUNT
            and unique_ratio <= CATEGORICAL_MAX_UNIQUE_RATIO
        ):
            return "categorical"

    return "string"


def _field_schema(name: str, series: pd.Series) -> dict[str, Any]:
    logical_type = _logical_type(series)
    non_null = series.dropna()
    field: dict[str, Any] = {
        "name": name,
        "pandas_dtype": str(series.dtype),
        "type": logical_type,
        "nullable": bool(series.isna().any()),
        "null_count": int(series.isna().sum()),
        "unique_count": int(series.nunique(dropna=True)),
        "sample_values": [_jsonable(v) for v in non_null.head(SAMPLE_SIZE).tolist()],
    }

    if logical_type in ("integer", "number") and not non_null.empty:
        field["constraints"] = {
            "minimum": _jsonable(non_null.min()),
            "maximum": _jsonable(non_null.max()),
            "mean": float(non_null.mean()),
        }
    elif logical_type == "datetime" and not non_null.empty:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                parsed = pd.to_datetime(non_null, errors="coerce")
            field["constraints"] = {
                "minimum": str(parsed.min()),
                "maximum": str(parsed.max()),
            }
        except (ValueError, TypeError):
            pass
    elif logical_type == "categorical":
        field["constraints"] = {"enum": sorted(map(str, non_null.unique().tolist()))}
    elif logical_type in ("string", "email", "url") and not non_null.empty:
        lengths = non_null.astype(str).map(len)
        field["constraints"] = {"max_length": int(lengths.max()), "min_length": int(lengths.min())}

    return field


def _jsonable(value: Any) -> Any:
    """Coerce numpy/pandas scalar types into plain JSON/YAML-safe values."""
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value


def infer_schema(df: pd.DataFrame, *, dataset_name: str = "dataset") -> dict[str, Any]:
    """Infer a Table-Schema-like description for the given DataFrame."""
    return {
        "name": dataset_name,
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "fields": [_field_schema(col, df[col]) for col in df.columns],
    }
