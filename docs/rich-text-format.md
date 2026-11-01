# Rich-text content format

Cell values and `column_headers` values may be "rich text": text plus optional
formatting semantics (mostly for diff highlighting). This page specifies the accepted
shapes.

## Shapes

A value may be any of:

- a **plain string** — e.g. `"hello"`;
- a **list of segments** — e.g.
  `[{"text": "hello"}, {"text": " world", "role": "added"}]`;
- a **segment object with `text`** — e.g. `{"text": "hello", "role": "added"}`;
- a **segment wrapper with `parts`** — e.g.
  `{"parts": [{"text": "hello"}, {"text": " world", "role": "added"}]}`;
- a **property list** — a list of `{"name": ..., "value": ...}` records (each may carry
  an optional `role`), rendered as `name = "value"`; this is how `source_file_metadata`
  and attribute lists are shown.

A **segment** is any object that carries a `text` field or a `parts` field (a list of
segments). Numbers and other scalars are rendered as their string form.

## The `role` field

A segment may carry a `role` field, which selects special markup. Built-in roles:

- `added`, `removed`, `source_added`, `source_removed` — diff highlighting
  (`added`/`removed` = inline overlay, `source_*` = underlying overlay);
- `date`, `time`, `datetime` — date/time markup (frontend JS converts to local time);
- `label` — pseudo-label;
- `sronly` — screen-reader-only text;
- `ellipsis` — collapsed long text;
- `noshowdiff` — used together with `added`/`removed` to suppress the diff prefix.

Only the built-in roles receive special markup. A custom/unknown `role` renders the
segment as plain text unless a backend plugin or a role handler adds markup for it.

## Extra, non-standard properties

A segment object may carry additional, non-standard properties beyond `text`, `parts`,
and `role`. This is allowed and **must not be a blocker**: no tool that reads or
consumes the format (HTML report, diff, Excel, …) should crash or fail just because an
object carries properties it does not recognize.

At the same time, such properties are **not guaranteed to work**: a consumer may ignore
them, drop them, or leave them untouched, and no consumer is required to interpret or
preserve them.

Concretely:

- **HTML report:** non-standard properties must not become part of the visible text.
  The renderer ignores them and only reads `text`, `parts`, and `role`, so

  ```json
  {"text": "hello", "role": "added", "my_custom_property": 123}
  ```

  renders exactly like `{"text": "hello", "role": "added"}`.

- **Diff:** whatever the diff tool does with non-standard properties is not guaranteed
  to be meaningful — it only must not crash and must not block. In particular `role`
  (and other such properties) is not semantically diffable: if the left cell is
  `{"text": "aaa", "role": "label"}` and the right is `{"text": "aab", "role": "sronly"}`,
  there is no meaningful `added`/`removed` representation of the `role` change. Turning
  `role` into a rich-text value with `added`/`removed` parts would produce a value that
  is neither `label` nor `sronly` and therefore loses its meaning. Consumers must accept
  that such a property may simply be left as-is (e.g. preserved unchanged) rather than
  diffed.

> **Known inconsistency:** the plain-text extraction helper `sanitize_text_general`
> (used by the `diff_add_classes` backend plugin) is currently stricter — it only
> recognizes a segment when the object contains no keys other than `text`, `parts`,
> and `role`, so the example above would fall back to being stringified there. The
> intended contract (extra properties allowed and ignored) is tracked in
> `docs/project-context.md`.
