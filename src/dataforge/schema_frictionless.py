"""Frictionless Framework integration for schema inference and validation.

This module is the roadmap item "swap in Frictionless Framework for
ingestion + schema inference" implemented as an *additive* engine rather
than a hard replacement: the original heuristic engine in `schema.py`
remains the default (zero extra dependencies), and this module provides an
opt-in `--engine frictionless` path via the `frictionless` extra.

Frictionless (https://framework.frictionlessdata.io/) brings three things
the heuristic engine does not have:
  1. A standards-compliant Table Schema output (portable beyond dataforge).
  2. Real validation (`validate_source`) -- type/constraint violations per
     row/cell, not just descriptive stats.
  3. Broader format + encoding detection during the describe step itself.

Implementation note: this integration is written against the documented
Frictionless Framework v5 API (`frictionless.describe`, `frictionless.validate`,
`Resource.schema`, `Schema.to_dict()`). It could not be exercised against a
live install in the environment this was authored in (no package index
access), so treat it as a best-effort reference implementation -- please
open an issue/PR if a Frictionless version you use produces a different
`describe()`/`validate()` return shape than expected here.
"""
from __future__ import annotations

from typing import Any


class FrictionlessNotInstalled(ImportError):
    pass


def _require_frictionless():
    try:
        import frictionless  # noqa: F401
    except ImportError as exc:
        raise FrictionlessNotInstalled(
            "frictionless is not installed. Run: pip install dataforge-cli[frictionless]"
        ) from exc
    return frictionless


def infer_schema_frictionless(source: str, *, dataset_name: str = "dataset") -> dict[str, Any]:
    """Describe a data source using Frictionless Framework and normalize
    the result into the same shape produced by `dataforge.schema.infer_schema`,
    so callers (and the rendered schema.html template) don't need to care
    which engine produced it.
    """
    frictionless = _require_frictionless()
    resource = frictionless.describe(source)

    raw_schema = resource.schema.to_dict() if getattr(resource, "schema", None) else {"fields": []}
    raw_fields = raw_schema.get("fields", [])

    fields = []
    for f in raw_fields:
        constraints = f.get("constraints", {}) or {}
        fields.append(
            {
                "name": f.get("name"),
                "pandas_dtype": None,
                "type": f.get("type", "any"),
                "nullable": not constraints.get("required", False),
                "null_count": None,
                "unique_count": None,
                "sample_values": [],
                "constraints": constraints,
            }
        )

    row_count = None
    stats = getattr(resource, "stats", None)
    if stats is not None:
        row_count = getattr(stats, "rows", None) or (stats.get("rows") if isinstance(stats, dict) else None)

    return {
        "name": dataset_name,
        "row_count": row_count,
        "column_count": len(fields),
        "fields": fields,
        "engine": "frictionless",
        "table_schema": raw_schema,
    }


def validate_source(source: str) -> dict[str, Any]:
    """Run Frictionless validation against a source and return a plain
    dict report (row/cell-level type & constraint violations). Requires
    the `frictionless` extra; raises FrictionlessNotInstalled otherwise.
    """
    frictionless = _require_frictionless()
    report = frictionless.validate(source)

    if hasattr(report, "to_dict"):
        return report.to_dict()
    if isinstance(report, dict):
        return report
    return {"valid": getattr(report, "valid", None), "raw": str(report)}
