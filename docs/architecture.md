# MDM-HTMLReport-py — architecture

Stable reference. Living working-memory notes (findings, roadmap, open questions) live
in `docs/project-context.md`, which is updated on every agent run and is not linked
from user-facing docs.

The input JSON format is specified in two companion files:

- `docs/report-json-format.md` — the JSON "report" shape this package consumes.
- `docs/rich-text-format.md` — the rich-text shapes used for cell values and
  `column_headers`.

## 1. Where it fits

`mdmreportpy` is a **reporter**: it consumes the common JSON "report" shape and emits
HTML. It does not know or care which reader produced the JSON. Producers include:

- `mdmreadpy` (the MDD reader),
- the diff tool (compares two JSON reports and writes a new JSON report),
- the other format readers (Excel, SPSS, text, ms markitdown, …).

`mdmreportpy` itself only emits HTML; it is not a JSON producer.

## 2. Modules

| Path | Role |
| --- | --- |
| `src/report_create.py` | Main entry (`produce_html`, `entry_point`). Input parsing, plugin dispatch, HTML rendering, CLI. |
| `src/common_functions.py` | Shared text/HTML sanitization and formatting helpers (pure functions). |
| `src/plugins/` | Backend enhancement plugins + the plugin contract (`base.py`: `PluginContext`, `run_plugins`, hook-point constants). |
| `src/report_html_template.py` | Loads and minifies HTML/CSS/JS templates and builds the JS plugin list at import time. |
| `src/report_html_make_js_plugin_code.py` | Wraps each JS plugin in an IIFE with shared error handling (`printErrors`, `wrapErrors`). |
| `src/minify_assets.py` | Optional CSS/JS minification (`csscompressor` / `rjsmin`), graceful no-op if missing. |
| `src/launcher.py` | Dispatcher (`--program report`). |
| `src/templates/` | HTML/CSS/JS assets, incl. `plugins/*/script.{js,css}`. |
| `build_compiled_template.py` | Writes `src/GENERATED/TEMPLATE.py` for the pinliner bundle. |

## 3. Plugin layers (intentional)

- **Frontend JS plugins** (interactivity): beautifydates, aligncolwidths, expandable,
  showhidecolumns, jira, columnfiltering, showhidesections, formatpreoutputs,
  validatemddlabelissues, diffondiffshowallrows, common. Live in
  `src/templates/plugins/<name>/`.
- **Backend Python plugins** (transforms before/while HTML is written). Live in
  `src/plugins/`; each registers handlers for one or more named hook points
  (`on_table_before`, `on_row_before`, `on_col_before`, `on_col_after`,
  `on_row_after`, `on_table_after`) and mutates a `PluginContext`. Domain-prefixed
  names:
  - `mdd_combine_attributes` (MDD reports),
  - `mdd_validate_labels` (MDD reports),
  - `diff_add_classes` (diff reports),
  - `page_wrap_tables_for_memory_saving` (any report).
  Disable with `--disable-plugin <name>`.

## 4. Build / template embedding

Templates are read at development time via `importlib.resources`, compiled to
`src/GENERATED/TEMPLATE.py` at build time, and the runtime falls back to `GENERATED`
inside the pinliner bundle. Minifying the embedded CSS/JS is a build-time optimization:
the helpers it uses (`csscompressor` / `rjsmin`) are development-only and declared in
`requirements-dev.txt` (not `requirements.txt`, so the distributed launchers never
install them). See `.clinerules/02-python-portability.md`.
