"""dataforge command-line interface.

Pipeline stages exposed as subcommands:
  ingest   -> preview a dataset load
  schema   -> infer & export a schema (json/yaml)
  profile  -> analyze & export summary statistics
  chart    -> render a single Plotly chart to HTML
  build    -> run the full pipeline and emit an HTML site (summary/schema/charts)
  wp-push  -> push a rendered HTML page to WordPress as a draft post
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich.console import Console
from rich.table import Table

from dataforge.charts import ChartKind, build_chart_html
from dataforge.export import df_to_html_table, df_to_records, dict_to_json, dict_to_yaml, to_csv
from dataforge.ingest import load_dataset
from dataforge.profile import generate_profile
from dataforge.render import build_site
from dataforge.schema import infer_schema
from dataforge.utils import ensure_dir, slugify
from dataforge.wp_publish import WordPressConfig, push_html_as_post

app = typer.Typer(help="Ingest, analyze, and publish datasets to HTML/WordPress.")
console = Console()


@app.command()
def ingest(source: str, rows: int = typer.Option(5, help="Preview row count")) -> None:
    """Load a dataset and print a quick preview + shape."""
    df = load_dataset(source)
    console.print(f"[bold green]Loaded[/] {source}: {df.shape[0]} rows x {df.shape[1]} columns")

    table = Table(show_header=True, header_style="bold cyan")
    for col in df.columns:
        table.add_column(str(col))
    for _, row in df.head(rows).iterrows():
        table.add_row(*[str(v) for v in row.tolist()])
    console.print(table)


@app.command()
def schema(
    source: str,
    out: Optional[Path] = typer.Option(None, help="Output file (.json or .yaml)"),
    dataset_name: Optional[str] = typer.Option(None, help="Name to embed in the schema"),
    engine: str = typer.Option(
        "heuristic", help="Schema engine: 'heuristic' (default, no extra deps) or 'frictionless'"
    ),
    validate: bool = typer.Option(
        False, "--validate", help="Also run Frictionless validation (requires --engine frictionless)"
    ),
) -> None:
    """Infer a schema for the dataset and print or save it.

    --engine frictionless delegates to the Frictionless Framework
    (Table Schema spec) instead of dataforge's built-in heuristics -- see
    dataforge.schema_frictionless and the README "Schema engines" section.
    Requires: pip install dataforge-cli[frictionless]
    """
    name = dataset_name or Path(source).stem

    if engine == "frictionless":
        from dataforge.schema_frictionless import infer_schema_frictionless, validate_source

        result = infer_schema_frictionless(source, dataset_name=name)
        if validate:
            report = validate_source(source)
            console.print("[bold]Frictionless validation report:[/]")
            console.print_json(json.dumps(report, default=str))
    elif engine == "heuristic":
        df = load_dataset(source)
        result = infer_schema(df, dataset_name=name)
    else:
        raise typer.BadParameter("engine must be 'heuristic' or 'frictionless'")

    if out is None:
        console.print_json(json.dumps(result, default=str))
        return

    if out.suffix in (".yaml", ".yml"):
        dict_to_yaml(result, out)
    else:
        dict_to_json(result, out)
    console.print(f"[bold green]Schema written to[/] {out}")


@app.command()
def profile(
    source: str,
    out: Optional[Path] = typer.Option(None, help="Output file (.json or .yaml)"),
    dataset_name: Optional[str] = typer.Option(None, help="Name to embed in the profile"),
) -> None:
    """Analyze the dataset and print or save summary statistics."""
    df = load_dataset(source)
    name = dataset_name or Path(source).stem
    result = generate_profile(df, dataset_name=name)

    if out is None:
        console.print_json(json.dumps(result, default=str))
        return

    if out.suffix in (".yaml", ".yml"):
        dict_to_yaml(result, out)
    else:
        dict_to_json(result, out)
    console.print(f"[bold green]Profile written to[/] {out}")


@app.command()
def chart(
    source: str,
    x: str = typer.Option(..., help="Column for the x-axis / categories"),
    y: Optional[str] = typer.Option(None, help="Column for the y-axis / values"),
    kind: ChartKind = typer.Option("bar", help="bar | line | scatter | pie | histogram | box"),
    out: Path = typer.Option(Path("chart.html"), help="Output HTML file"),
    title: Optional[str] = typer.Option(None, help="Chart title"),
) -> None:
    """Render a single chart from the dataset to a standalone HTML file."""
    df = load_dataset(source)
    html = build_chart_html(df, x=x, y=y, kind=kind, title=title)
    out.write_text(
        f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<meta name='viewport' content='width=device-width, initial-scale=1'></head>"
        f"<body>{html}</body></html>",
        encoding="utf-8",
    )
    console.print(f"[bold green]Chart written to[/] {out}")


@app.command()
def build(
    source: str,
    out_dir: Path = typer.Option(Path("output"), help="Directory for generated site + data files"),
    dataset_name: Optional[str] = typer.Option(None, help="Name to embed in outputs"),
    chart_x: Optional[str] = typer.Option(None, help="Column for a chart x-axis (optional)"),
    chart_y: Optional[str] = typer.Option(None, help="Column for a chart y-axis (optional)"),
    chart_kind: ChartKind = typer.Option("bar", help="Chart type if chart_x is given"),
    schema_engine: str = typer.Option(
        "heuristic", help="Schema engine: 'heuristic' (default) or 'frictionless'"
    ),
    layout: str = typer.Option(
        "table",
        help=(
            "Dataset preview layout on the generated summary page: "
            "'table' (scrollable HTML table, default), 'cards' (Flexbox card per row), "
            "or 'grid' (CSS Grid card per row). Use 'cards'/'grid' for wide datasets "
            "(many columns) to avoid horizontal scrolling."
        ),
    ),
) -> None:
    """Run the full pipeline: ingest -> schema -> profile -> (optional chart)
    -> CSV/JSON/YAML/HTML outputs -> rendered HTML site.
    """
    if layout not in ("table", "cards", "grid"):
        raise typer.BadParameter("layout must be 'table', 'cards', or 'grid'")

    df = load_dataset(source)
    name = dataset_name or slugify(Path(source).stem)
    out_dir = ensure_dir(out_dir)
    data_dir = ensure_dir(out_dir / "data")

    if schema_engine == "frictionless":
        from dataforge.schema_frictionless import infer_schema_frictionless

        schema_result = infer_schema_frictionless(source, dataset_name=name)
    else:
        schema_result = infer_schema(df, dataset_name=name)

    profile_result = generate_profile(df, dataset_name=name)

    to_csv(df, data_dir / f"{name}.csv")
    dict_to_json(schema_result, data_dir / f"{name}.schema.json")
    dict_to_yaml(schema_result, data_dir / f"{name}.schema.yaml")
    dict_to_json(profile_result, data_dir / f"{name}.profile.json")

    table_html = df_to_html_table(df)
    records = df_to_records(df) if layout != "table" else None

    charts = []
    if chart_x:
        chart_html = build_chart_html(df, x=chart_x, y=chart_y, kind=chart_kind)
        charts.append({"title": f"{chart_kind}: {chart_x}", "html": chart_html})

    written = build_site(
        dataset_name=name,
        table_html=table_html,
        schema=schema_result,
        profile=profile_result,
        charts=charts,
        out_dir=out_dir,
        layout=layout,
        records=records,
    )

    console.print(f"[bold green]Site built in[/] {out_dir}")
    for label, path in written.items():
        console.print(f"  - {label}: {path}")
    console.print(f"  - data files: {data_dir}")
    console.print(f"  - preview layout: {layout}")


@app.command("wp-push")
def wp_push(
    html_file: Path = typer.Argument(..., help="Path to a rendered HTML file (e.g. output/index.html)"),
    site: str = typer.Option(..., help="WordPress base URL, e.g. https://example.com"),
    username: str = typer.Option(..., help="WordPress username"),
    app_password: str = typer.Option(..., envvar="WP_APP_PASSWORD", help="WP application password"),
    title: str = typer.Option(..., help="Title for the new post/page"),
    status: str = typer.Option("draft", help="draft | pending | publish"),
    post_type: str = typer.Option("posts", help="posts | pages"),
) -> None:
    """Push a rendered HTML file to WordPress as a new draft post/page via
    the REST API. Requires an Application Password (WP Admin > Users).
    """
    config = WordPressConfig(base_url=site, username=username, app_password=app_password)
    html_content = html_file.read_text(encoding="utf-8")
    result = push_html_as_post(
        config, title=title, html_content=html_content, status=status, post_type=post_type
    )
    console.print(f"[bold green]Pushed to WordPress[/] id={result.get('id')} link={result.get('link')}")


if __name__ == "__main__":
    app()
