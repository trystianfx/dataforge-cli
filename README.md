# dataforge-cli

**Ingest any dataset. Infer its schema. Analyze it. Publish it to HTML,
PHP, or WordPress.**

`dataforge-cli` is a Python command-line tool (and importable library)
that implements a pipeline for turning messy, heterogeneous datasets into
structured, browsable web content:

```
  ingest        schema         profile        export              render
[ CSV/JSON/YAML/Excel/Parquet ]
        |             |              |              |                  |
        v             v              v              v                  v
   pandas.DataFrame -> inferred    -> summary   -> CSV/JSON/YAML/   -> Jinja2 HTML
                        schema        stats         HTML table         (site or
                        (JSON/YAML)                 + Plotly charts     WP post)
```

This project was scaffolded as a prototype in response to the question:
*"is there an open-source tool that already ingests varied datasets, infers
a schema, analyzes it, and renders the results into HTML/WordPress
templates?"* Short answer: not as a single turnkey tool, but every stage
already has a mature open-source library behind it (pandas, Frictionless
Framework / Table Schema, ydata-profiling, Plotly, Jinja2). This repo wires
those stages together behind one CLI so the "glue" doesn't have to be
rebuilt from scratch every time.

## Why this exists

Every individual stage below is a solved problem in the Python ecosystem.
What's missing is a thin, opinionated layer that chains them together and
lands the output as ready-to-embed HTML for a static site, a PHP page, or
a WordPress post. That's what `dataforge` is:

| Stage | What it does | Backed by |
|---|---|---|
| Ingest | Load CSV, TSV, JSON, YAML, Excel, Parquet, or a remote URL into a normalized `DataFrame` | `pandas`, `requests` |
| Schema | Infer field types (integer, number, boolean, date/datetime, categorical, email, url, string), nullability, cardinality, and basic constraints | custom, Table-Schema-inspired (`dataforge/schema.py`) |
| Profile | Row/column counts, missingness, duplicates, per-column descriptive stats | `pandas` (optional: `ydata-profiling` for a full interactive report) |
| Export | Write CSV, JSON, YAML, and HTML `<table>` fragments | `pandas`, `PyYAML` |
| Chart | Render bar/line/scatter/pie/histogram/box charts as embeddable HTML | `Plotly` |
| Render | Assemble the above into HTML pages via templates | `Jinja2` |
| Publish | Push a rendered page to WordPress as a draft post via REST | `requests` + WP Application Passwords |

## Installation

### Linux

```bash
# Debian/Ubuntu/Raspbian: make sure Python 3.10+ and venv are available
sudo apt update && sudo apt install -y python3 python3-venv python3-pip git

git clone https://github.com/trystianfx/dataforge-cli.git
cd dataforge-cli
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"
```

### macOS

```bash
# Requires Homebrew (https://brew.sh) for a modern Python 3
brew install python git

git clone https://github.com/trystianfx/dataforge-cli.git
cd dataforge-cli
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"
```

### Windows

Use PowerShell. Install Python 3.10+ from [python.org](https://www.python.org/downloads/)
(check **"Add python.exe to PATH"** during setup) or via `winget`:

```powershell
winget install Python.Python.3.12
```

Then, in a new PowerShell window:

```powershell
git clone https://github.com/trystianfx/dataforge-cli.git
cd dataforge-cli
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -e ".[dev]"
```

If PowerShell blocks the activation script with an execution-policy error,
run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, then retry.
Command Prompt users can activate instead with `.venv\Scripts\activate.bat`.

### Optional: full profiling engine

On any OS, once the venv above is active:

```bash
pip install -e ".[profiling]"
```

This pulls in `ydata-profiling` for the full interactive HTML profiling
report path (heavier install, brings in scipy/statsmodels/visualization
deps).

### Verify the install

```bash
dataforge --help
dataforge build examples/sample_repeaters.csv --out-dir output/repeaters --chart-x city --chart-y frequency_mhz
```

## Quick start

A sample dataset is included at `examples/sample_repeaters.csv` (amateur
radio repeater listings, because of course).

**1. Preview a dataset:**

```bash
dataforge ingest examples/sample_repeaters.csv
```

**2. Infer and save its schema:**

```bash
dataforge schema examples/sample_repeaters.csv --out output/repeaters.schema.json
```

**3. Profile it:**

```bash
dataforge profile examples/sample_repeaters.csv --out output/repeaters.profile.json
```

**4. Render a single chart:**

```bash
dataforge chart examples/sample_repeaters.csv \
  --x city --y frequency_mhz --kind bar --out output/chart.html
```

**5. Run the full pipeline (recommended):**

```bash
dataforge build examples/sample_repeaters.csv \
  --out-dir output/repeaters \
  --chart-x city --chart-y frequency_mhz --chart-kind bar
```

This produces:

```
output/repeaters/
  index.html          # dataset overview + preview table
  schema.html          # rendered schema table
  charts.html           # embedded Plotly chart(s)
  data/
    repeaters.csv
    repeaters.schema.json
    repeaters.schema.yaml
    repeaters.profile.json
```

Open `output/repeaters/index.html` in a browser -- no server required, the
pages are fully static (Plotly loads from a CDN by default).

## Publishing to WordPress

`dataforge` does not require a live WordPress site to build HTML output --
the pages from `dataforge build` can be dropped into any theme via a
Custom HTML block, an `iframe`, or a PHP `include()`. If you do want to
push a rendered page directly into WordPress as a draft post:

1. In WP Admin, go to **Users > Profile > Application Passwords** and
   generate one for your account.
2. Run:

```bash
export WP_APP_PASSWORD="xxxx xxxx xxxx xxxx xxxx xxxx"

dataforge wp-push output/repeaters/index.html \
  --site https://your-site.example.com \
  --username your-wp-username \
  --title "Yuma Repeater Directory" \
  --status draft
```

This creates a **draft** post (never publishes automatically) using the
WordPress REST API (`/wp-json/wp/v2/posts`). Review it in wp-admin, then
publish manually. Use `--post-type pages` to create a Page instead, or
`--status publish` once you trust the pipeline.

## CLI reference

| Command | Purpose |
|---|---|
| `dataforge ingest SOURCE` | Load and preview a dataset |
| `dataforge schema SOURCE [--out FILE]` | Infer schema, print or save as JSON/YAML |
| `dataforge profile SOURCE [--out FILE]` | Analyze dataset, print or save stats as JSON/YAML |
| `dataforge chart SOURCE --x COL [--y COL] [--kind KIND]` | Render one chart to standalone HTML |
| `dataforge build SOURCE --out-dir DIR [--chart-x COL --chart-y COL]` | Full pipeline: ingest -> schema -> profile -> export -> HTML site |
| `dataforge wp-push FILE --site URL --username USER --title TITLE` | Push a rendered HTML file to WordPress as a draft |

Run `dataforge --help` or `dataforge COMMAND --help` for full option lists.

## Project layout

```
dataforge-cli/
  src/dataforge/
    cli.py            # Typer CLI entry point, wires all stages together
    ingest.py          # Load CSV/TSV/JSON/YAML/Excel/Parquet -> DataFrame
    schema.py           # Type + constraint inference -> portable schema dict
    profile.py           # Summary stats; optional ydata-profiling bridge
    export.py             # CSV/JSON/YAML/HTML-table writers
    charts.py              # Plotly chart HTML generation
    render.py               # Jinja2 site assembly
    wp_publish.py             # WordPress REST API push (draft-first, no deletes)
    templates/                 # base.html.j2, summary.html.j2, schema.html.j2, chart.html.j2
    utils.py                    # logging, slugify, dir helpers
  examples/
    sample_repeaters.csv          # sample dataset used in the quick start & tests
  tests/                            # pytest suite covering ingest/schema/export
  dataforge_entry.py                 # freeze-friendly entry point for PyInstaller/Nuitka/cx_Freeze
  dataforge.spec                      # PyInstaller build spec (bundles Jinja2 templates)
  setup_cxfreeze.py                    # cx_Freeze build script
  pyproject.toml
  requirements.txt
  README.md
```

## Design notes

- **Draft-first publishing.** `wp-push` defaults to creating a WordPress
  draft, never a live publish, and the module contains no delete
  operations. Nothing on your live site changes without a manual review
  step in wp-admin.
- **CDN vs. offline charts.** `build_chart_html()` defaults to
  `include_plotlyjs="cdn"` to keep generated pages small; pass
  `include_plotlyjs=True` in code if you need charts to work fully
  offline (e.g. an air-gapped ham shack server).
- **Schema inference is heuristic, not authoritative.** Type detection
  (email/url/categorical/datetime) is based on sampling and simple regex
  checks -- always spot-check `schema.html` against a dataset you know
  before trusting it for anything downstream like validation gating.
- **No lock-in.** Every stage is a plain function that takes/returns
  pandas DataFrames or plain dicts, so you can use `dataforge` as a
  library (`from dataforge.schema import infer_schema`) in a notebook or
  another app instead of the CLI.

## Roadmap

These are natural next steps, roughly in priority order:

1. **Swap in Frictionless Framework** (`frictionless-py`) for ingestion +
   schema inference to get proper Table Schema compliance, constraint
   validation, and multi-table/relational support for free.
2. **`ydata-profiling` HTML report command** -- a `dataforge profile
   --engine ydata --out report.html` path that emits the full interactive
   profiling report instead of the lightweight JSON summary.
3. **More chart types & auto-suggestion** -- given a schema, suggest
   sensible chart pairings (e.g. categorical x numeric -> bar;
   datetime x numeric -> line) instead of requiring `--chart-x/--chart-y`.
4. **WordPress shortcode companion plugin** -- a tiny PHP plugin
   (`[dataforge_chart id="..."]`) that fetches generated JSON/chart HTML
   from a REST endpoint, so charts stay live-updating instead of being
   pasted in as static HTML.
5. **Multi-dataset / relational schema support** -- handle datasets that
   arrive as multiple related tables (foreign keys) rather than one flat
   file.
6. **Web upload front-end** -- a small FastAPI + HTMX app wrapping this
   CLI so non-CLI users can drag-and-drop a file and get a rendered site
   back, deployable via Docker on self-hosted infrastructure.
7. **Data-quality gating** -- integrate Great Expectations so `build` can
   fail (or flag) when incoming data violates the previously-saved
   schema, useful for recurring/scheduled ingestion jobs.

## Building a standalone executable

For distributing `dataforge` to a machine without Python installed (or
just to have one self-contained binary), three freezing tools are
supported. All three build against `dataforge_entry.py` at the repo root
(a thin wrapper around the Typer app) rather than the installed
`console_scripts` entry point, and **none of them cross-compile** -- build
on the same OS you intend to run the executable on.

| Tool | Output | Notes |
|---|---|---|
| PyInstaller | one-file or one-folder | Fastest to set up, widest package compatibility |
| Nuitka | one-file or one-folder | Compiles Python to C; slower build, better performance & harder to reverse-engineer |
| cx_Freeze | one-folder only (+ optional installer) | Can also produce a Windows `.msi` or macOS `.app`/`.dmg` |

Install whichever tool you want inside the project's virtual environment
first, e.g. `pip install pyinstaller`.

### PyInstaller (all platforms)

A ready-to-use spec file is included at `dataforge.spec` -- it bundles the
Jinja2 template directory, which PyInstaller cannot discover automatically.

```bash
pip install pyinstaller
pyinstaller dataforge.spec
```

The executable lands in `dist/dataforge` (`dist/dataforge.exe` on Windows).
To build without the spec file (simpler, but you must pass `--add-data`
yourself so templates are bundled):

```bash
# Linux/macOS
pyinstaller --onefile --add-data "src/dataforge/templates:dataforge/templates" dataforge_entry.py

# Windows (note the semicolon separator instead of a colon)
pyinstaller --onefile --add-data "src\dataforge\templates;dataforge\templates" dataforge_entry.py
```

### Nuitka (all platforms)

Nuitka compiles to C and produces the most tamper-resistant binary of the
three, at the cost of longer build times.

```bash
pip install nuitka

# One-folder build (recommended first attempt -- easier to debug missing imports)
python -m nuitka --standalone --follow-imports \
  --include-data-dir=src/dataforge/templates=dataforge/templates \
  dataforge_entry.py

# One-file build once the standalone build works cleanly
python -m nuitka --onefile --follow-imports \
  --include-data-dir=src/dataforge/templates=dataforge/templates \
  dataforge_entry.py
```

The one-folder build lands in `dataforge_entry.dist/`; the one-file build
produces a single `dataforge_entry.bin` (Linux/macOS) or
`dataforge_entry.exe` (Windows) in the current directory. If pandas/plotly
submodules go missing at runtime, add `--follow-import-to=pandas` /
`--follow-import-to=plotly` explicitly.

### cx_Freeze (all platforms, no one-file option)

A setup script is included at `setup_cxfreeze.py`.

```bash
pip install cx_Freeze
python setup_cxfreeze.py build_exe
```

The output folder is `build/exe.<platform>.<pyver>/` containing the
executable plus all dependencies -- ship the whole folder together.
Windows and macOS users can additionally build an installer:

```bash
# Windows only -- produces an .msi installer
python setup_cxfreeze.py bdist_msi

# macOS only -- produces a .app bundle or a .dmg image
python setup_cxfreeze.py bdist_mac
python setup_cxfreeze.py bdist_dmg
```

### Choosing between them

- Want the quickest working binary today: **PyInstaller**.
- Want the smallest attack surface for reverse engineering, and can
  tolerate a slower build: **Nuitka**.
- Want a Windows `.msi` or macOS `.app`/`.dmg` installer out of the box,
  and don't need a single-file binary: **cx_Freeze**.

## Testing

```bash
pytest
```

## License

MIT -- see [LICENSE](LICENSE).
