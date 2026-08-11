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
) -> dict[str, Path]:
    """Render summary.html, schema.html, and (optionally) charts.html into
    out_dir and return a dict of {page_name: written_path}.
    """
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
