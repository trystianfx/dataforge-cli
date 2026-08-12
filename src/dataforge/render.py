"""Template rendering layer: turns dataset + schema + profile + chart HTML
into finished HTML pages using Jinja2, ready to be dropped onto a static
site, included via PHP, or published to WordPress (see wp_publish.py).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from dataforge.utils import ensure_dir

TEMPLATES_DIR = Path(__file__).parent / "templates"
VALID_LAYOUTS = ("table", "cards", "grid")


def _env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "j2"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_page(template_name: str, context: dict[str, Any]) -> str:
    env = _env()
    template = env.get_template(template_name)
    return template.render(**context)


def build_site(
    *,
    dataset_name: str,
    table_html: str,
    schema: dict[str, Any],
    profile: dict[str, Any],
    charts: list[dict[str, str]] | None,
    out_dir: str | Path,
    layout: str = "table",
    records: list[dict[str, Any]] | None = None,
) -> dict[str, Path]:
    """Render summary.html, schema.html, and (optionally) charts.html into
    out_dir and return a dict of {page_name: written_path}.

    `layout` controls how the dataset preview on summary.html is rendered:
      - "table" (default): a single scrollable HTML table -- best for
        datasets with few enough columns to read as rows, or when you want
        a familiar spreadsheet-like view. Wide tables get a horizontal
        scroll container rather than squeezing/wrapping columns.
      - "cards": a Flexbox card per row, wrapping naturally at any
        viewport width -- best for wide datasets on mobile.
      - "grid": a CSS Grid card per row (auto-fit columns) -- similar to
        "cards" but with more even card sizing on desktop.

    `records` (list of dicts) is required when layout is "cards" or
    "grid"; pass the output of `dataforge.export.df_to_records(df)`.
    """
    if layout not in VALID_LAYOUTS:
        raise ValueError(f"layout must be one of {VALID_LAYOUTS}, got {layout!r}")
    if layout != "table" and records is None:
        raise ValueError(f"layout={layout!r} requires `records` (see dataforge.export.df_to_records)")

    out_dir = ensure_dir(out_dir)
    charts = charts or []

    written: dict[str, Path] = {}

    summary_html = render_page(
        "summary.html.j2",
        {
            "dataset_name": dataset_name,
            "table_html": table_html,
            "profile": profile,
            "has_charts": bool(charts),
            "layout": layout,
            "records": records or [],
        },
    )
    summary_path = out_dir / "index.html"
    summary_path.write_text(summary_html, encoding="utf-8")
    written["summary"] = summary_path

    schema_html = render_page(
        "schema.html.j2",
        {"dataset_name": dataset_name, "schema": schema},
    )
    schema_path = out_dir / "schema.html"
    schema_path.write_text(schema_html, encoding="utf-8")
    written["schema"] = schema_path

    if charts:
        charts_html = render_page(
            "chart.html.j2",
            {"dataset_name": dataset_name, "charts": charts},
        )
        charts_path = out_dir / "charts.html"
        charts_path.write_text(charts_html, encoding="utf-8")
        written["charts"] = charts_path

    return written
