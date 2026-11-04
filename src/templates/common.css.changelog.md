# `common.css` changelog

Every change to `common.css` must be recorded here, in reverse-chronological
order, with the date and a short reason for the change. See
`.clinerules/09-frontend-common-css.md`.

## 2026-11-04

- Replaced the original minimal skin with the cross-project reusable "lib" skin:
  `--mdm-*` tokens, base/layout/typography, and generic `mdm-link-*` /
  `mdm-btn-*` / `mdm-table` / `mdm-u-*` classes. The report feature domain moved
  to `mdmreporttable.css` (banners, tables, controls, diff overlays).
- Settled the colour tokens on the report's own palette: primary action is a
  neutral grey `#555` (no purple), confirm/green/link use `#217346`, and yellow
  highlights became `--mdm-color-highlight` / `--mdm-color-highlight-soft`.
- Kept `Helvetica` as the base body font.
