# Log of issues

> Running log of bugs and fixes for this repo.
>
> **Update rule:** update this file only when the user explicitly asks — never
> proactively.

## 2026-11-14 — `mdd_combine_attributes` crashes on rich-text column headers (`dict` + `str`)

**Symptom.** `mdmreportpy` fails while producing an HTML diff report:

```
html markup: failed when processing section fields
TypeError: unsupported operand type(s) for +: 'dict' and 'str'
  at src/plugins/mdd_combine_attributes.py:62
      add_parts.append({'text': def_add['matching_col'] + '\n', 'role': 'label'})
```

**Root cause.** The diff tool now emits rich-text `column_headers` (see
`docs/rich-text-format.md`), e.g.:

```json
"attributes_left": {"parts": [{"role": "context", "text": "Item Attributes"}, {"text": " (Left file)"}]}
```

`mdd_combine_attributes` takes the attribute column header as `matching_col` (it is
`rows[0][col_id_att]`, where `rows[0]` is the header row added in
`prep_htmlmarkup_section`) and still assumes it is a plain `str`. Line 62 concatenates
it with `'\n'`, so a dict header raises `TypeError`.

**Trigger.** All of:

1. `report_type == "diff"` (or any report with rich-text column headers);
2. an attribute column whose `column_headers` value is a rich-text dict/list;
3. ≥ 2 attribute columns whose per-row data differ — otherwise the duplicate check
   (`check_duplicates` fingerprints) collapses the list to one part and the label branch
   (`add_col_label`) is skipped, hiding the bug.

In the failing report the `attributes_left` / `attributes_right` cells are property lists
(`[{"name": ..., "value": {"role": "context", "text": ...}}, ...]`) that differ between
left and right.

**Fix.**

- In `src/plugins/mdd_combine_attributes.py`, flatten `matching_col` to plain text before
  using it as a label: import `sanitize_text_general` from `common_functions` (the same
  pattern `diff_add_classes.py` uses) and compute
  `matching_col_text = sanitize_text_general(def_add['matching_col'])`, then use
  `matching_col_text + '\n'`.
- Keep the raw `def_add['matching_col'] == def_add['data']` object comparison as-is: it
  still short-circuits the header row (where `data` is the same header object) and the
  plain-string case, and `dict == list` / `dict == str` are safe (return `False`).
- Optional secondary hardening (not part of this crash, left open): make the local
  `is_empty` in this plugin treat an empty rich-text segment / empty property list the
  same way as an empty plain value.

**Regression tests added.**

- `tests/test_backend_plugins.py` (`TestMddCombineAttributes`):
  - `test_combine_attributes_with_rich_text_headers_and_property_list_cells` — rich-text
    dict headers + differing property-list `attributes_left`/`attributes_right` cells must
    not raise and must merge the attribute columns into `name`;
  - `test_combine_attributes_label_uses_plain_text_header` — the label part's `text` is a
    plain string equal to the flattened header (e.g. `"Item Attributes (Left file)\n"`),
    not a dict.
- `tests/fixtures/report.diff.rich_headers_attrs-.mdd.json` + matching `.mdd.html`, and
  `tests/test_fixtures.py`: a small **non-sensitive** synthetic diff fixture mirroring the
  real shape (rich-text headers + property-list attribute cells), so `produce_html` is
  guarded end-to-end. The `sanitize_text_general` flattening of the `{"parts": [...]}`
  header shape was already covered by `TestRichTextValues.test_sanitize_text_general_flattens_rich_text`.

**Status.** Fixed and covered by regression tests (2026-11-14).

