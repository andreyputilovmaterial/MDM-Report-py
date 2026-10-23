# MDM-HTMLReport-py — architecture & input JSON format

Stable reference. Living working-memory notes (findings, roadmap, open questions) live
in `docs/project-context.md`, which is updated on every agent run and is not linked
from user-facing docs.

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
| `src/report_create.py` | Main entry (`produce_html`, `entry_point`). Input parsing, text sanitization, plugin dispatch, HTML rendering, CLI. |
| `src/report_html_template.py` | Loads and minifies HTML/CSS/JS templates and builds the JS plugin list at import time. |
| `src/report_html_make_js_plugin_code.py` | Wraps each JS plugin in an IIFE with shared error handling (`printErrors`, `wrapErrors`). |
| `src/minify_assets.py` | Optional CSS/JS minification (`csscompressor` / `rjsmin`), graceful no-op if missing. |
| `src/launcher.py` | Dispatcher (`--program report`). |
| `src/templates/` | HTML/CSS/JS assets, incl. `plugins/*/script.{js,css}`. |
| `build_compiled_template.py` | Writes `src/GENERATED/TEMPLATE.py` for the pinliner bundle. |

## 3. Input JSON format

```
{
  "report_type": "MDD" | "diff" | "TextFile" | ...,
  "source_file": "...",                       # single-input reports
  "source_left": "...", "source_right": "...",  # diff reports
  "report_datetime_utc": "...",
  "report_datetime_local": "...",
  "source_file_metadata": [ {"name": ..., "value": ..., "role": ...} ],
  "report_scheme": {
    "columns": [...],
    "column_headers": {...},
    "flags": [...]
  },
  "sections": [
    {
      "name": "...",
      "title": "...",            # optional display title (falls back to name)
      "columns": [...],          # optional per-section column override
      "column_headers": {...},   # optional per-section title override
      "statistics": "...",       # optional banner
      "content": [ { "colname": <cell>, ... }, ... ]
    }
  ]
}
```

Cell values may be strings, lists, `{"text": ...}`, `{"parts": [...]}`, or property
lists `[{"name": ..., "value": ...}, ...]`. A `role` field carries formatting semantics
(`added`, `removed`, `date`, `label`, `sronly`, `noshowdiff`, ...).

## 4. Plugin layers (intentional)

- **Frontend JS plugins** (interactivity): beautifydates, aligncolwidths, expandable,
  showhidecolumns, jira, columnfiltering, showhidesections, formatpreoutputs,
  validatemddlabelissues, diffondiffshowallrows, common.
- **Backend Python "enhancement plugins"** (transforms before HTML is written):
  combine-attributes-into-master-name, add-diff-classes, wrap-tables-for-memory-saving,
  validate-labels. Disable with `--disable-plugin`.

## 5. Build / template embedding

Templates are read at development time via `importlib.resources`, compiled to
`src/GENERATED/TEMPLATE.py` at build time, and the runtime falls back to `GENERATED`
inside the pinliner bundle. See `.clinerules/02-python-portability.md`.
