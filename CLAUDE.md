# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

"Spendly" — a Flask expense tracker built as a step-by-step learning project. Routes for core features
(auth, expense CRUD) exist in `app.py` as placeholders returning plain strings (e.g. `"Add expense — coming
in Step 7"`); they are implemented incrementally by "students" as the project progresses. Check `app.py` for
which routes are still placeholders before assuming a feature works end-to-end.

`database/db.py` is currently an empty stub — its docstring specifies the contract it must fulfill once
implemented: `get_db()` (SQLite connection with `row_factory` and foreign keys enabled), `init_db()` (create
tables with `CREATE TABLE IF NOT EXISTS`), `seed_db()` (insert sample dev data).

## Commands

Windows/PowerShell, using the committed `venv`:

```powershell
venv\Scripts\activate
pip install -r requirements.txt
python app.py          # runs on http://localhost:5001 with debug=True
```

Run tests (pytest + pytest-flask are in requirements.txt, but no tests exist yet — add them under a `tests/`
directory):

```powershell
pytest
pytest tests/test_file.py::test_name   # single test
```

There is no lint/format tooling configured in this repo.

## Architecture

- **`app.py`** — single-file Flask app; all routes are defined here directly (no blueprints). Runs on port
  5001.
- **`database/`** — intended to hold the SQLite access layer (`db.py`) once implemented; the actual `.db`
  file (`expense_tracker.db`) is gitignored and created at runtime, not committed.
- **`templates/`** — Jinja2 templates. `base.html` is the shared layout (nav + footer) that page templates
  extend via `{% extends "base.html" %}` and override `title`/`head`/`content`/`scripts` blocks. Static
  pages (`landing.html`, `terms.html`, `privacy.html`) and auth forms (`login.html`, `register.html`) follow
  this pattern. Forms currently POST to hardcoded paths (e.g. `/register`) without CSRF protection or
  backend handling yet.
- **`static/css/`** — `style.css` holds shared/base styles (nav, footer, auth forms); `landing.css` holds
  landing-page-specific styles. Keep this split when adding page-specific styles rather than growing
  `style.css` unboundedly.
- **`static/js/main.js`** — currently empty; intended home for JS as features are built (e.g. the landing
  page's "see how it works" YouTube modal is currently inlined in `landing.html` rather than moved here).
