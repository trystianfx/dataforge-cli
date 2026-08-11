"""Structured output generators: CSV, JSON, YAML, and HTML tables from a
DataFrame or an arbitrary dict (e.g. an inferred schema or profile).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import yaml


def to_csv(df: pd.DataFrame, out_path: str | Path) -> Path:
    out_path = Path(out_path)
    df.to_csv(out_path, index=False)
    return out_path


def dict_to_json(data: dict[str, Any], out_path: str | Path) -> Path:
    out_path = Path(out_path)
    out_path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    return out_path


def dict_to_yaml(data: dict[str, Any], out_path: str | Path) -> Path:
    out_path = Path(out_path)
    out_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return out_path


def df_to_json_records(df: pd.DataFrame, out_path: str | Path) -> Path:
    out_path = Path(out_path)
    out_path.write_text(df.to_json(orient="records", indent=2), encoding="utf-8")
    return out_path


def df_to_html_table(df: pd.DataFrame, *, table_id: str = "dataforge-table", max_rows: int | None = 200) -> str:
    view = df.head(max_rows) if max_rows else df
    return view.to_html(
        table_id=table_id,
        classes="dataforge-table",
        index=False,
        border=0,
        na_rep="",
        escape=True,
    )
