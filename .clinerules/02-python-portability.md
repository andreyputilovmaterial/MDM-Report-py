# Python code style

It must be usable as an imported module *or* included as a git submodule, bundled via
`pinliner`, so it obeys strict portability constraints:

1. Relative imports only — entry-point scripts that are also run directly are the exception (see below),
2. Liftable to a different location in a bigger project without changes,
3. Every folder on the path to every module contains `__init__.py`,
4. No static files/assets used as-is at runtime — static assets are discouraged and,
   if needed, must be embedded into a generated Python module at build time (see below),
5. Minimal dependencies.

## Entry-point scripts and conditional imports

This project can be used in different ways: distributed as a single-file bundle created
with `pinliner`, or called directly during development. To support both, a few scripts
are also launched as a program in development and therefore use a three-way conditional
import block instead of a single import style:

```python
if __name__ == '__main__':
    # run as a program, e.g. `python src/diff.py`
    from diff_engine import diff_functions
elif '.' in __name__:
    # imported as a package member
    from .diff_engine import diff_functions
else:
    # included in the pinliner bundle with no parent package
    from diff_engine import diff_functions
```

Examples: `src/launcher.py`, `src/diff.py`. Any script that is meant to be launched
directly should use this pattern; every other module (the ones that are only ever
imported) uses plain relative imports.

## Static assets and the `GENERATED` folder

The default distributable is a single-file bundle produced with `pinliner`, which can
only embed Python modules. A plain static file (an HTML/CSS/JS template, a version
string, or anything that is not a python module, etc.) cannot be used as-is in that bundle, so:

1. **Static assets are discouraged.** It is easier to avoid them than to solve their
   embedding into the pinliner bundle.
2. **When a static asset is necessary — or clearly beneficial (faster development, more
   modular and easier to maintain) — it is allowed, but only via this technique:** the
   build script converts the asset into a Python module written to a `GENERATED`
   subfolder, which the real source code then imports like any other module.

This is a slightly circular workflow: the build script *generates* code that the real
source modules import. Not entirely clean, but it solves the pinliner bundling problem.

Existing examples in this repo:

- `build.bat` / `Makefile` run `git describe --tags --dirty` (a non-Python "static
  asset") and write the result into `src/GENERATED/_VERSION.py` as the `_VERSION`
  variable.
- `build_compiled_template.py` reads the HTML/CSS/JS files under
  `src/lib/mdmreadpy/src/lib/mdmreportpy/src/templates/` and writes their contents as
  string literals into `src/lib/mdmreadpy/src/lib/mdmreportpy/src/GENERATED/TEMPLATE.py`,
  which `report_create.py` imports when running inside the pinliner bundle.

### How template assets are embedded in `mdmreportpy`

The report generator uses a two-path approach for its HTML/CSS/JS templates:

- **Development time:** `report_html_template.py` loads the files under
  `src/templates/` with `importlib.resources` (`resources.files("src.templates")`)
  and minifies them in memory.
- **Build time:** `build_compiled_template.py` imports the source package
  (`from src import report_html_template`), then writes the assembled strings as
  literals into `src/GENERATED/TEMPLATE.py`.
- **Runtime inside the pinliner bundle:** `report_create.py` first tries to import the
  source `report_html_template`; when that fails (a bundle has no filesystem resource
  files) it falls back to `from GENERATED import TEMPLATE as report_html_template`.

The hardcoded `src` package name used by `resources.files("src.templates")` and by
`build_compiled_template.py` is part of this technique (the template package is named
`src` in this repo). It is intentional, though it means the subtree is not relocatable
under a different package name without updating those references.

## When inspecting source code

Any code under a `GENERATED` folder is **generated output, not maintained source code**:

- It exists only to solve the bundling/embedding problem described above.
- It is produced by the build script and can be regenerated at any time.
- It is **not tracked in git** (`.gitignore` excludes `**/GENERATED/`).
- Do not edit it by hand; change the original asset or the build script that produces it
  instead.
