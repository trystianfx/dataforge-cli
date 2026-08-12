# Charts

Renders a single Plotly chart from a dataset as an embeddable HTML
snippet (a `<div>` plus inline `<script>`), suitable for dropping into a
Jinja2 template, a static page, or a WordPress Custom HTML block.

## Supported chart kinds

| Kind | Plotly Express function | Requires `y`? |
|---|---|---|
| `bar` (default) | `px.bar` | optional |
| `line` | `px.line` | optional |
| `scatter` | `px.scatter` | optional |
| `pie` | `px.pie` (`x` = names, `y` = values) | recommended |
| `histogram` | `px.histogram` | not used |
| `box` | `px.box` | optional |

## CLI usage

```bash
dataforge chart examples/sample_repeaters.csv --x city --y frequency_mhz --kind bar
dataforge chart examples/sample_repeaters.csv --x country --kind histogram --out output/by_country.html
dataforge chart examples/sample_repeaters.csv --x mode --y frequency_mhz --kind box --title "Frequency spread by mode"
```

**Options:**

| Flag | Default | Description |
|---|---|---|
| `--x` | required | Column for the x-axis / categories |
| `--y` | none | Column for the y-axis / values (required in practice for `line`/`scatter`/`pie`) |
| `--kind` | `bar` | `bar`, `line`, `scatter`, `pie`, `histogram`, `box` |
| `--out` | `chart.html` | Output HTML file |
| `--title` | auto-generated | Chart title |

The CLI always writes a complete standalone HTML document (with
`<!DOCTYPE html>`, viewport meta tag, etc.); use the Python API directly
if you just want the `<div>`+`<script>` snippet to embed inside a larger
page.

## Python API

```python
from dataforge.ingest import load_dataset
from dataforge.charts import build_chart_html, ChartError

df = load_dataset("examples/sample_repeaters.csv")

snippet = build_chart_html(df, x="city", y="frequency_mhz", kind="bar")
# '<div id="..." class="plotly-graph-div" ...>...</div><script>...</script>'

# Embed fully offline (no CDN dependency) by inlining the whole plotly.js bundle:
snippet_offline = build_chart_html(df, x="city", y="frequency_mhz", include_plotlyjs=True)

try:
    build_chart_html(df, x="not_a_column", kind="bar")
except ChartError as e:
    print(e)
```

`include_plotlyjs` defaults to `"cdn"` (loads plotly.js from a CDN, keeps
pages small) -- pass `True` for offline-capable pages, e.g. a self-hosted
ham shack server with no outbound internet.

## Working example: multiple charts on one page

`dataforge build` only wires up a single `--chart-x`/`--chart-y` pair
today (see the Roadmap for planned auto-suggestion of multiple charts).
To render several charts into one page right now, call `build_chart_html`
directly and feed the list into `dataforge.render.build_site`'s `charts`
argument:

```python
from dataforge.ingest import load_dataset
from dataforge.charts import build_chart_html
from dataforge.render import render_page

df = load_dataset("examples/sample_repeaters.csv")

charts = [
    {"title": "Frequency by city", "html": build_chart_html(df, x="city", y="frequency_mhz", kind="bar")},
    {"title": "Repeaters by country", "html": build_chart_html(df, x="country", kind="histogram")},
]

html = render_page("chart.html.j2", {"dataset_name": "repeaters", "charts": charts})
open("output/charts.html", "w").write(html)
```

## See also

- [Plotly Express documentation](https://plotly.com/python/plotly-express/) -- for chart types and styling options (faceting, animation frames, color scales, custom hover templates) beyond the six kinds `build_chart_html` exposes. Any `plotly.express` figure's `.to_html(full_html=False, ...)` output is compatible with dataforge's render templates if you build a figure yourself.
