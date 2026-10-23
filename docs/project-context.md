# Project Context — MDM-HTMLReport-py (`mdmreportpy`)

> Last updated: 2026-10-23
> Status: initial capture. Architecture + design decisions + review findings are
> recorded here. The **input JSON format spec is still to be formalized** (see
> "Roadmap").
>
> **Convention:** read this file at the start of every task and update it at the end,
> so it stays the permanently updated context of the current work (see
> `.clinerules/00-project-context.md`).

## 1. What this package does

`mdmreportpy` turns JSON (produced by sibling tools in the same global project — e.g.
`otherformatsreadpy_txt/reader_plain.py` or `src/lib/mdmreadpy/src/lib/mdmreportpy`, the MDD reader, the MDD diff tool) into a
single, **fully self-contained HTML "report"**.

Requirements the output must satisfy:

- No external assets delivered alongside the HTML, no network requests at runtime.
- Pure raw HTML plus a small amount of framework-less JS ("an app without a framework").
- Basic structure must work even if every enhancement breaks.
- Must tolerate arbitrary input sizes (memory is a first-class concern).

## 2. Where it lives and how it is built

- Package root: `src/lib/mdmreadpy/src/lib/mdmreportpy`
- Source modules: `src/lib/mdmreadpy/src/lib/mdmreportpy/src/`
- Templates (HTML/CSS/JS assets): `src/lib/mdmreadpy/src/lib/mdmreportpy/src/templates/`
- Build chain: `build.bat` → `build_compiled_template.py` → `pinliner` single-file bundle.

The top-level package is literally named `src` in this repo (the `src/` folder under
`mdmreportpy/`), which matters for the template-embedding technique (see the rules file
`02-python-portability.md`, section "Static assets and the `GENERATED` folder").

## 3. Modules (current state)

| Module | Role |
| --- | --- |
| `src/report_create.py` | Main entry (`entry_point`) and `produce_html()`. Input parsing, text sanitization, plugin dispatch, HTML rendering, CLI. Currently a ~1256-line monolith. |
| `src/report_html_template.py` | Loads + minifies templates and JS plugin assets at import time; builds `TEMPLATE_HTML_*` strings and the `plugins` list. |
| `src/report_html_make_js_plugin_code.py` | Wraps each JS plugin in an IIFE with shared error-handling helpers (`printErrors`, `wrapErrors`). |
| `src/minify_assets.py` | Optional minification via `csscompressor` / `rjsmin` (graceful no-op if missing). |
| `src/launcher.py` | Dispatcher (`--program report`). |
| `src/templates/` | `html_begin.html`, `html_end.html`, `table_begin.html`, `table_end.html`, `common.css`, `common.js`, `mdmreporttable.css`, `normalize.css`, `copybanner.html`, and `plugins/*/script.{js,css}`. |
| `build_compiled_template.py` | Writes `src/GENERATED/TEMPLATE.py` from the assembled template strings (for the pinliner bundle). |

## 4. Input JSON format (draft — to be formalized)

This is an initial sketch, not yet a spec. It will be tightened in the next step using
real examples from the sibling producers.

```text
{
  report_type,                  # e.g. "MDD", "diff", "TextFile", ...
  source_file,                  # single-input reports
  source_left / source_right,   # diff reports
  report_datetime_utc,
  report_datetime_local,
  source_file_metadata: [],     # list of {name, value} property records
  report_scheme: {
    columns: [],                # global column ids
    column_headers: {},         # id -> display title
    flags: []                   # e.g. "data-type:..."
  },
  sections: [
    {
      name,                     # unique section id
      title?,                   # display title (falls back to name)
      columns?,                 # per-section column ids (override global)
      column_headers?,          # per-section title overrides
      statistics?,              # optional banner content
      content: [ { ...row } ]   # each row keyed by column id; "name" is master col
    }
  ]
}
```

Cell content (inside a row) supports several shapes, to be specified precisely later:

- direct string;
- list of elements (discouraged — prefer `{parts:[...]}`);
- object with a `text` field;
- object with a `parts` field (array wrapper);
- a `role` field on an object/part carries formatting semantics (e.g. `added`,
  `removed`, `date`, `label`, `sronly`, `noshowdiff`) for diff highlighting etc.

A "property list" is a special array shape: `[{"name": ..., "value": ...}, ...]`.

## 5. Design decisions (current philosophy)

- **Two plugin layers (intentional).** Prefer minimal core code, but the final result
  should be rich (column filtering, row filtering, TOC/section show-hide, diff
  coloring, etc.). Therefore:
  - **Frontend (JS) plugins** in `report_html_template.py` provide interactivity
    (beautifydates, aligncolwidths, expandable, showhidecolumns, jira,
    columnfiltering, showhidesections, formatpreoutputs, validatemddlabelissues,
    diffondiffshowallrows, common). Each is wrapped in its own IIFE and emits errors
    to the shared `#error_banner`, so a broken plugin cannot stop the others or the
    base page.
  - **Backend (Python) "enhancement plugins"** in `report_create.py`
    (`enchancement_plugins`: combine-attributes-into-master-name, add-diff-classes,
    wrap-tables-for-memory-saving, validate-labels) run at generation time, because
    some transforms must happen before HTML is written (e.g. memory-saving replaces
    a table's body with a deferred JSON string; combine-attributes removes a column
    entirely and folds its data into the `name` column as labels). These are
    controllable via `--disable-plugin`.
- **Memory / performance.**
  - Direct string concatenation is preferred over `.format()`/f-string replacement;
    this measurably reduced memory for large inputs.
  - Sections' table bodies are hidden behind a "click to load" control and stored as a
    JSON string until expanded — this saves browser **DOM** memory (not file size).
  - Filtering is done via CSS class matching, with no framework — very fast even on
    huge pages.
  - Verbose class names (`mdmreport-contentcell`, `mdmreport-colindex-`,
    `mdmreport-wrapper-section-`, `mdmreport-hidetablememorysaving_outer_`, …) are a
    **known size concern** and a recorded goal to shorten later (with a build-time
    check that old/new selectors map correctly).
- **Error handling.** Fail early for critical errors; for malformed data, try to
  render and fall back to blank rather than over-validate. "Missing property → blank"
  is the intended rule (there is currently one inconsistency — see finding #5).
- **Static assets via `GENERATED`.** Templates are read at dev time via
  `importlib.resources`, compiled to `GENERATED/TEMPLATE.py` at build time, and the
  runtime falls back to `GENERATED` inside the pinliner bundle. See the rules file for
  the precise mechanism.

## 6. Review findings & dispositions (2026-10-20)

Each finding records the reasoning, the decision, and the next action.

### 1. No automated tests — confirmed gap (highest priority for future changes)
- **Reasoning:** the code is described as stable, but there is no regression safety net.
- **Decision:** tests are a primary goal, but they must come **after** the input format
  is documented/spec'd.
- **Action:** docs → spec → tests (see Roadmap).

### 2. `report_create.py` is a ~1256-line monolith — accepted as the *final* goal
- **Reasoning:** mixes input parsing, sanitization, plugin dispatch, rendering, CLI.
- **Decision:** agree it should be split, but not first; final refactor step.

### 3. `htmlattr_sanitize_value_general.is_empty` has `isinstance(s,int) or isinstance(s,int)` — confirmed bug
- **Reasoning:** duplicate `int`; `float` is never handled.
- **Decision:** fix it as part of extracting shared helpers.
- **Action:** create a `common_functions.py` helper module; move `is_empty` and similar
  definitions there and fix the typo.

### 4. Implicit global `errorBannerReadyPromise` in generated JS — confirmed bug
- **Reasoning:** `errorBannerReadyPromise = new Promise(...)` has no `var/let/const`,
  so it leaks to `window` and each plugin IIFE overwrites it. Harmless today (all
  identical) but fragile.
- **Action:** declare it (`var`/`let`/`const`) when touching that wrapper.

### 5. Unguarded `inp['source_file_metadata']` / `inp['report_datetime_utc']` in `produce_html` — confirmed inconsistency
- **Reasoning:** contradicts "missing property → blank"; other fields are guarded but
  these are not.
- **Decision:** agree it should be corrected.
- **Action:** use `.get()`/defaults consistently when the input contract is finalized.

### 6. `flags = list(set([...]))` loses order — withdrawn (not an issue)
- **Decision:** flags are a set of binary switches; order is irrelevant. Leave as-is.

### 7. `from ast import Import` unused — confirmed dead code
- **Reasoning:** it imports Python's AST `Import` node class; it is never used.
- **Action:** remove during cleanup.

### 8. `sanitize_idfield` unused vs `sanitize_cssfield` — open question
- **Reasoning:** three identifier/sanitizer helpers currently coexist, with unclear
  semantic difference.
- **Action:** clarify which is needed and under what conditions during the spec work.

### 9. Dead / duplicated code — confirmed cleanup candidates
- Duplicate `is_property_list` (module level + inside `sanitize_text_general`).
- Commented-out first version of `html_sanitize_value_asproperties`.
- Dead `special_pattern = '<<KEYWORD>>'` code in `html_sanitize_text`.
- `html.escape('{result}'.format(result=result))` → `html.escape(result)`.
- **Action:** remove during the shared-helper extraction, covered by the new tests.

### 10. Three identifier encodings + hardcoded `col_x95_axis_x40_side_x41_` in CSS — not an issue (low priority)
- **Decision:** these ids are not user-visible; the `_xNN_` encoding is intentional to
  keep extra info available as CSS classes for possible future plugins, escaping
  everything that cannot appear in a class. It may be cosmetically improved later but
  is not a priority.

### 11. Two plugin systems with different names/controllability — intentional
- **Decision:** the split is deliberate (backend transforms vs frontend
  interactivity). No change; document only.

### 12. `resources.files("src.templates")` portability — clarified, not a defect
- **Reasoning:** the hardcoded `src` package name is part of the asset-embedding
  technique, not an accident.
- **Decision:** the rules file did not describe this accurately; updated
  `02-python-portability.md` to document the actual mechanism.

### 13. Naive `<table>` split in the memory-saving plugin — open (to review later)
- **Reasoning:** splits on first `<table` / last `</table>`; fine for one table per
  section today, fragile if a nested/banner `<table>` ever appears.
- **Action:** review and decide whether a more robust split or a guard is needed.

### 14. `combine_attributes_into_master_name_col` mutates rows in place — open (to review later)
- **Reasoning:** currently mutates to remove the attribute column; may be required for
  the column-removal behavior.
- **Decision:** prefer a clean non-mutating function if possible; to be reviewed.

### 15. Per-row `section-{sec_id}` flag — intentional
- **Decision:** kept on purpose to leave identifiers available for future plugins;
  having it as a CSS class is considered a good idea. No change.

### 16. Verbose class names / HTML size — confirmed concern, recorded as a goal
- **Action:** shorten class names later, with a build-time check that old/new selectors
  stay in sync (minification alone does not shrink the class names in the table markup).

### 17. Code style: `.format()` vs f-strings, single vs double quotes — style note
- **Reasoning:** `'{x}'.format(x=...)` is not a preference; it came from an example and
  is being gradually replaced with `f'{x}'`. Quote style (single vs double) is still
  undecided.
- **Action:** record as an open style decision; normalize opportunistically.

## 7. Roadmap

1. **Documentation (this file).** Record architecture, decisions, findings. *(this step)*
2. **Formalize the JSON input format spec.** Work through real examples from the
   sibling producers; document every accepted cell-content shape and role.
3. **Extract `common_functions.py`** and fix the small confirmed bugs (#3, #4, #5, #7,
   #9).
4. **Add tests.** Unit tests for the pure sanitization/format functions + a golden-file
   test (small JSON fixture → assert HTML structure).
5. **Refactor.** Split `report_create.py`; normalize the identifier/sanitizer helpers
   (#8); shorten verbose class names (#16); review open items (#13, #14).

## 8. Open questions

- Exact, complete list of accepted cell-content shapes and `role` values (to be
  settled in step 2).
- Whether `sanitize_idfield` is needed or can be removed/merged with
  `sanitize_cssfield`.
- Whether the memory-saving `<table>` split needs to be made more robust.
- Whether `combine_attributes_into_master_name_col` can be made non-mutating.
- Quote style convention (single vs double) and final stance on f-strings.
