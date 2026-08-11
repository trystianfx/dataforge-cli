"""Analysis layer: produce summary statistics and data-quality signals for
a DataFrame. This is deliberately lightweight (pure pandas) so the CLI has
zero heavy dependencies out of the box.

If `ydata-profiling` is installed (see the `profiling` extra in
pyproject.toml), `generate_profile(..., engine="ydata")` will delegate to it
for a much richer HTML report (distributions, correlations, alerts).
"""
from __future__ import annotations

from typing import Any

import pandas as pd


def generate_profile(df: pd.DataFrame, *, dataset_name: str = "dataset") -> dict[str, Any]:
    """Lightweight profile: shape, missingness, duplicates, per-column stats."""
    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    per_column = {}
    for col in df.columns:
        series = df[col]
        entry: dict[str, Any] = {
            "missing": int(series.isna().sum()),
            "missing_pct": round(float(series.isna().mean()) * 100, 2),
            "unique": int(series.nunique(dropna=True)),
        }
        if col in numeric_cols:
            desc = series.describe()
            entry["stats"] = {k: float(v) for k, v in desc.to_dict().items()}
        per_column[col] = entry

    return {
        "name": dataset_name,
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "duplicate_rows": int(df.duplicated().sum()),
        "memory_usage_bytes": int(df.memory_usage(deep=True).sum()),
        "per_column": per_column,
    }


def generate_ydata_report_html(df: pd.DataFrame, *, dataset_name: str = "dataset") -> str:
    """Delegate to ydata-profiling for a full interactive HTML report.

    Requires the optional `profiling` extra: `pip install dataforge-cli[profiling]`
    """
    try:
        from ydata_profiling import ProfileReport
    except ImportError as exc:
        raise ImportError(
            "ydata-profiling is not installed. Run: pip install dataforge-cli[profiling]"
        ) from exc

    report = ProfileReport(df, title=f"{dataset_name} profile", explorative=True)
    return report.to_html()
