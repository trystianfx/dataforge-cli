# Third-Party Notices

dataforge-cli is distributed under the MIT License (see [LICENSE](LICENSE)).
It depends on the open-source packages listed below, none of which are
vendored or modified in this repository -- they are installed separately
via `pip` from PyPI.

**Why this file exists:** when dataforge-cli is packaged into a standalone
executable (see "Building a standalone executable" in the [README](README.md)
-- PyInstaller, Nuitka, or cx_Freeze), the compiled binary bundles the code
of these dependencies directly. At that point their licenses' notice-
preservation requirements apply to the distributed binary. This file
satisfies that requirement by preserving each project's name, license, and
a link to its full license text. If you distribute a frozen build of
dataforge-cli, include this file alongside it.

All licenses below are OSI-approved and permissive; none impose copyleft
(share-alike) obligations on dataforge-cli itself.

| Package | License | Project |
|---|---|---|
| pandas | BSD-3-Clause | [github.com/pandas-dev/pandas](https://github.com/pandas-dev/pandas) -- [LICENSE](https://github.com/pandas-dev/pandas/blob/main/LICENSE) |
| PyYAML | MIT | [github.com/yaml/pyyaml](https://github.com/yaml/pyyaml) -- [LICENSE](https://github.com/yaml/pyyaml/blob/main/LICENSE) |
| Jinja2 | BSD-3-Clause | [github.com/pallets/jinja](https://github.com/pallets/jinja) -- [LICENSE](https://github.com/pallets/jinja/blob/main/LICENSE.txt) |
| Typer | MIT | [github.com/fastapi/typer](https://github.com/fastapi/typer) -- [LICENSE](https://github.com/fastapi/typer/blob/master/LICENSE) |
| Rich | MIT | [github.com/Textualize/rich](https://github.com/Textualize/rich) -- [LICENSE](https://github.com/Textualize/rich/blob/master/LICENSE) |
| Plotly (plotly.py + plotly.js) | MIT | [github.com/plotly/plotly.py](https://github.com/plotly/plotly.py) -- [LICENSE](https://github.com/plotly/plotly.py/blob/main/LICENSE.txt) |
| openpyxl | MIT | [foss.heptapod.net/openpyxl/openpyxl](https://foss.heptapod.net/openpyxl/openpyxl) |
| Requests | Apache-2.0 | [github.com/psf/requests](https://github.com/psf/requests) -- [LICENSE](https://github.com/psf/requests/blob/main/LICENSE) |
| python-dateutil | Apache-2.0 OR BSD-3-Clause (dual, your choice) | [github.com/dateutil/dateutil](https://github.com/dateutil/dateutil) -- [LICENSE](https://github.com/dateutil/dateutil/blob/master/LICENSE) |
| ydata-profiling (optional extra) | MIT | [github.com/ydataai/ydata-profiling](https://github.com/ydataai/ydata-profiling) -- [LICENSE](https://github.com/ydataai/ydata-profiling/blob/master/LICENSE) |
| Frictionless Framework (optional extra) | MIT | [github.com/frictionlessdata/frictionless-py](https://github.com/frictionlessdata/frictionless-py) -- [LICENSE](https://github.com/frictionlessdata/frictionless-py/blob/main/LICENSE.md) |

## Keeping this file current

Dependency versions and licenses can change over time. To regenerate an
up-to-date snapshot of what's actually installed in your environment:

```bash
pip install pip-licenses
pip-licenses --format=markdown --with-urls --with-license-file
```

Re-check this file whenever a dependency is added, removed, or its major
version bumped in `pyproject.toml`.

## No warranty

As stated in [LICENSE](LICENSE), dataforge-cli and everything it depends
on is provided "AS IS", without warranty of any kind. This file is
provided for attribution and license-compliance purposes and does not
constitute legal advice.
