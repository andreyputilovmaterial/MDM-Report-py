# Report JSON format

Stable reference for the JSON "report" shape consumed by `mdmreportpy`. See
`docs/architecture.md` for how the package is organized, and
`docs/rich-text-format.md` for the shapes allowed inside cell values and
`column_headers`.

## Shape

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

## Cell values

Cell values (the `content` entries, keyed by column id) follow the rich-text format
described in `docs/rich-text-format.md`: a plain string, a list of parts, a
`{"text": ...}` / `{"parts": [...]}` segment, or a property list
`[{"name": ..., "value": ...}, ...]`.

## Column headers

`column_headers` values — global (`report_scheme.column_headers`) and per-section
(`section.column_headers`) — accept the same rich-text shapes as cell values. They are
sanitized through the same pipeline as cells.

`source_file_metadata` entries are property records (`name`, `value`, and an optional
`role`), i.e. a property list.
