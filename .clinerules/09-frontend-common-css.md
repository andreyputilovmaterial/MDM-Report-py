# Global CSS (`common.css`)

`src/templates/common.css` is the shared global "skin" embedded in every report.
Its rules are broad and reach all markup, so it must stay predictable and
low-surprise.

- Before assuming a layout bug lives in `common.css`, check the report-domain
  skin (`src/templates/mdmreporttable.css`) or a plugin `script.css` first. Most
  report-table/plugin styling belongs there, not in the global skin.
- Only modify `common.css` when a change is genuinely global (a shared token,
  a shared utility, or a rule that should apply everywhere).
- **Every change to `common.css` must be recorded** in
  `src/templates/common.css.changelog.md` (the file lives alongside
  `common.css`). Log entries are reverse-chronological and include the date and
  a short reason for each change.
