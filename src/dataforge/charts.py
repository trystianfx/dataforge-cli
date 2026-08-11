"""Chart generation using Plotly. Produces self-contained HTML snippets
(a <div> plus inline <script>) that can be dropped straight into a Jinja2
template, a static HTML page, or a WordPress "Custom HTML" block.
"""
from __future__ import annotations

from typing import Literal

import pandas as pd
import plotly.express as px

ChartKind = Literal["bar", "line", "scatter", "pie", "histogram", "box"]


class ChartError(Exception):
    pass


def build_chart_html(
    df: pd.DataFrame,
    *,
    x: str,
    y: str | None = None,
    kind: ChartKind = "bar",
    title: str | None = None,
    include_plotlyjs: str | bool = "cdn",
) -> str:
    """Return an HTML snippet (div + script) for the requested chart.

    include_plotlyjs="cdn" keeps the page light (loads plotly.js from a CDN);
    pass True to inline the full plotly.js bundle for fully offline pages.
    """
    if x not in df.columns:
        raise ChartError(f"Column '{x}' not found in dataset")
    if y is not None and y not in df.columns:
        raise ChartError(f"Column '{y}' not found in dataset")

    title = title or f"{kind.title()} chart: {x}" + (f" vs {y}" if y else "")

    if kind == "bar":
        fig = px.bar(df, x=x, y=y, title=title)
    elif kind == "line":
        fig = px.line(df, x=x, y=y, title=title)
    elif kind == "scatter":
        fig = px.scatter(df, x=x, y=y, title=title)
    elif kind == "pie":
        fig = px.pie(df, names=x, values=y, title=title)
    elif kind == "histogram":
        fig = px.histogram(df, x=x, title=title)
    elif kind == "box":
        fig = px.box(df, x=x, y=y, title=title)
    else:
        raise ChartError(f"Unsupported chart kind: {kind}")

    fig.update_layout(margin=dict(l=40, r=20, t=60, b=40))
    return fig.to_html(full_html=False, include_plotlyjs=include_plotlyjs, config={"responsive": True})
