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

- Python 3 (standard library only at runtime).
- Build/development only, for minification: `csscompressor` and `rjsmin` — declared in
  `requirements-dev.txt` (`pip install -r requirements-dev.txt`). They minify the
  embedded CSS/JS when the template is built; if they are missing, CSS/JS are emitted
  un-minified (with a one-time warning). They are **not** runtime dependencies and are
  **not** installed by the distributed launchers.

## Usage

Direct (during development):

```
python -m src.report_create --inpfile path/to/report.json
```

Or through the universal launcher:

```
python -m src.launcher --program report --inpfile path/to/report.json
```

### Three ways to launch

As everywhere in this toolchain, the program can be started three equivalent ways:

1. **Single-file bundle** (distribution). `build.bat`/`build.sh` produce
   `dist/mdmtoolsap_bundle.py` with pinliner's `--main src.launcher --main-attr main`
   entry point (the bundle runs `launcher.main()` when executed directly). Prepare the
   environment with `run_init`, then run the bundle with the venv Python:

   ```
   run_init.sh
   ./.venv/bin/python dist/mdmtoolsap_bundle.py --program report --inpfile path/to/report.json
   ```

2. **Direct module** (development). Run the entry-point module directly with `-m`:

   ```
   python -m src.report_create --inpfile path/to/report.json
   ```

3. **Launcher proxy** (development). Run the universal dispatcher with `-m`:

   ```
   python -m src.launcher --program report --inpfile path/to/report.json
   ```

Options:

- `--output-format html` — the default and currently the only implemented format here;
  Excel export lives in the sibling `mdmexcelreportpy`.
- `--output-filename PATH` — set the output file name (and path) explicitly. When
  provided it is used verbatim (no `.html` is appended); otherwise the name is derived
  from the input JSON file.
- `--disable-plugin NAME` (repeatable) — disable a backend enhancement plugin:
  `mdd_combine_attributes`, `mdd_validate_labels`, `diff_add_classes`,
  `page_wrap_tables_for_memory_saving`.

## Build

`build.bat` regenerates `src/GENERATED/_VERSION.py`, runs
`build_compiled_template.py`, and produces the single-file `dist/mdmtoolsap_bundle.py`
with `pinliner`. Install the build-only minifiers first with
`pip install -r requirements-dev.txt` (optional; without them the template is emitted
un-minified). See `.clinerules/02-python-portability.md` for the template-embedding
technique.

## Documentation

- [Architecture](docs/architecture.md) — package layout, plugin layers, build/template
  embedding.
- [Report JSON format](docs/report-json-format.md) — the JSON "report" shape.
- [Rich-text content format](docs/rich-text-format.md) — cell/header content shapes and
  `role` semantics.
