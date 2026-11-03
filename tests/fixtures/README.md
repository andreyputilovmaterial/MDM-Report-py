# Example inputs and outputs of `mdmreportpy`

Each `*.mdd.json` is an example *input* (produced by `mdmreadpy` or the diff tool); the
matching `*.mdd.html` is the example *output* of this package rendered from that input.
All are small synthetic reports — **not real/sensitive data** — and are used by
`tests/test_fixtures.py`.

Inputs:

- `a1_v1.mdd.json`, `a1_v2.mdd.json`, `b1_today.mdd.json`, `b1_tomorrow.mdd.json` —
  plain MDD reports from `mdmreadpy`.
- `report.diff.a1_-v1-v2-.mdd.json`, `report.diff.b1_-today-tomorrow-.mdd.json` —
  diff reports produced by the diff tool.
- `report.diff.report.diff.-a1_-b1_---v1-today---v2-tomorrow--.mdd.json` — a
  "diff-on-diff" report (diffing the two diff reports above).

The matching `.html` files are the example outputs. `tests/test_fixtures.py`
re-renders each input with `produce_html` and checks a self-contained page comes out.
The committed HTML files are kept as reference examples, not compared byte-for-byte
(they embed a build timestamp and the minification/plugin output may change).
