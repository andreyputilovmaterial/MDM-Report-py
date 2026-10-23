# MDM-HTMLReport-py (`mdmreportpy`)

Turns JSON into a single, fully self-contained HTML report. It is the "print/export"
half of the MDM toolchain: the various readers and the diff tool all produce the same
JSON shape, and this package renders that JSON to HTML for a human to read in a
browser.

Input JSON is produced by, among others:

- the MDD reader (`mdmreadpy`),
- the diff tool (which itself compares JSON reports),
- the other format readers in the global project (Excel, SPSS, text, ms markitdown, …).

## What it does

- Reads a JSON "report" file (see `docs/architecture.md` for the format).
- Produces one `.html` file next to the input, with no external assets and no network
  requests at runtime.
- Works even if every JS enhancement fails: the base table is plain HTML, and each JS
  plugin is isolated in its own IIFE so a broken plugin cannot break the page or the
  other plugins.

## Requirements

- Python 3.
- Optional, for minification only: `csscompressor` and `rjsmin`. If they are missing,
  CSS/JS are emitted un-minified (with a one-time warning).

## Usage

Direct (during development):

```
python src/report_create.py --inpfile path/to/report.json
```

Or through the universal launcher:

```
python src/launcher.py --program report --inpfile path/to/report.json
```

Options:

- `--output-format html` — the default and currently the only implemented format here;
  Excel export lives in the sibling `mdmexcelreportpy`.
- `--disable-plugin NAME` (repeatable) — disable a backend enhancement plugin.

## Build

`build.bat` regenerates `src/GENERATED/_VERSION.py`, runs
`build_compiled_template.py`, and produces the single-file `dist/mdmtoolsap_bundle.py`
with `pinliner`. See `.clinerules/02-python-portability.md` for the template-embedding
technique.

## Documentation

- [Architecture & input JSON format](docs/architecture.md) — stable reference for
  developers.
