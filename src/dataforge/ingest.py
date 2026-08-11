"""Ingestion layer: normalize datasets of varying formats/sources into a
single pandas.DataFrame, regardless of whether they arrived as CSV, TSV,
JSON, YAML, Excel, Parquet, or a remote URL pointing at any of the above.

This module intentionally stays dependency-light. For more elaborate,
format-aware ingestion (encoding sniffing, header repair, foreign keys,
constraint checking) swap this out for `frictionless-py`, which implements
the Frictionless / Table Schema spec and is a good drop-in upgrade path --
see the README "Roadmap" section.
"""
from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Any

import pandas as pd
import requests
import yaml

from dataforge.utils import get_logger

log = get_logger(__name__)

SUPPORTED_EXTENSIONS = {
    ".csv", ".tsv", ".json", ".yaml", ".yml",
    ".xlsx", ".xls", ".parquet",
}


class IngestError(Exception):
    """Raised when a source cannot be loaded into a DataFrame."""


def _read_bytes_from_source(source: str) -> tuple[bytes, str]:
    """Return (raw_bytes, suffix) for a local path or a remote URL."""
    if source.startswith("http://") or source.startswith("https://"):
        log.info(f"Fetching remote dataset: {source}")
        resp = requests.get(source, timeout=30)
        resp.raise_for_status()
        suffix = Path(source.split("?")[0]).suffix.lower()
        return resp.content, suffix

    path = Path(source)
    if not path.exists():
        raise IngestError(f"Source not found: {source}")
    return path.read_bytes(), path.suffix.lower()


def load_dataset(source: str) -> pd.DataFrame:
    """Load a dataset from a local file path or URL into a DataFrame.

    Supported formats: .csv, .tsv, .json, .yaml/.yml, .xlsx/.xls, .parquet
    JSON/YAML are flattened with pandas.json_normalize when they contain a
    list of records; a single dict is wrapped into a one-row frame.
    """
    raw, suffix = _read_bytes_from_source(source)

    if suffix not in SUPPORTED_EXTENSIONS:
        raise IngestError(
            f"Unsupported extension '{suffix}'. Supported: {sorted(SUPPORTED_EXTENSIONS)}"
        )

    buf = io.BytesIO(raw)

    if suffix == ".csv":
        return pd.read_csv(buf)
    if suffix == ".tsv":
        return pd.read_csv(buf, sep="\t")
    if suffix in (".xlsx", ".xls"):
        return pd.read_excel(buf)
    if suffix == ".parquet":
        return pd.read_parquet(buf)
    if suffix == ".json":
        data: Any = json.loads(raw.decode("utf-8"))
        return _records_to_frame(data)
    if suffix in (".yaml", ".yml"):
        data = yaml.safe_load(raw.decode("utf-8"))
        return _records_to_frame(data)

    raise IngestError(f"No handler implemented for '{suffix}'")


def _records_to_frame(data: Any) -> pd.DataFrame:
    if isinstance(data, list):
        return pd.json_normalize(data)
    if isinstance(data, dict):
        # Common shapes: {"records": [...]}, {"data": [...]}, or a flat dict
        for key in ("records", "data", "items", "rows"):
            if key in data and isinstance(data[key], list):
                return pd.json_normalize(data[key])
        return pd.json_normalize([data])
    raise IngestError("JSON/YAML source must decode to a list of records or a dict")
