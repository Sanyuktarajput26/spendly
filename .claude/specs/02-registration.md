# Spec: Registration

## Overview
Turn the static `/register` page into a working sign-up flow. Today `GET /register` only renders
`register.html`, and its form POSTs to `/register` with no backend handling. This step adds the POST
handler: it validates the submitted name, email and password, rejects duplicate emails, hashes the
password with werkzeug, inserts the user into the `users` table, and redirects to the login page with a
success message. Registration is the first auth feature on the Spendly roadmap. Login and logout
(Step 3) and the profile page (Step 4) both need real user accounts to exist.

## Depends on
- **Step 1 — Database setup** (`.claude/specs/01-database-setup.md`): `get_db()`, `init_db()` and the
  `users` table with `UNIQUE` on `email` must already be in place (they are, in `database/db.py`).

## Routes
- `GET /register` — render the registration form (already exists, keep behaviour) — public
- `POST /register` — validate input, create the user, redirect to `/login` on success, or re-render
  `register.html` with an error and the previously entered name and email on failure — public

Both methods are handled by the existing `register()` view via `methods=["GET", "POST"]`. No new URL
paths are added.

## Database changes
No database changes. The existing `users` table (`id`, `name`, `email UNIQUE`, `password_hash`,
`created_at`) already covers registration.

New helper functions go in `database/db.py`. They are not schema changes:
- `get_user_by_email(email)` — returns the `sqlite3.Row` or `None`
- `create_user(name, email, password)` — hashes the password with `generate_password_hash`, inserts
  the row with a parameterised query, and returns the new user's `id`

## Templates
- **Create:** none
- **Modify:**
  - `templates/register.html`: keep the entered `name` and `email` in the inputs when the form is
    re-rendered after an error (`value="{{ name or '' }}"`, `value="{{ email or '' }}"`). Never refill
    the password. Add `minlength="8"` to the password input to match the placeholder.
  - `templates/login.html`: show flashed success messages (for example "Account created — please sign
    in") above the form, using a new `.auth-success` class.

## Files to change
- `app.py`: set `app.secret_key` (read from the `SECRET_KEY` environment variable, with a dev-only
  fallback) so `flash()` works. Import `request`, `redirect`, `url_for` and `flash`. Change
  `register()` to accept GET and POST and implement the POST logic.
- `database/db.py`: add `get_user_by_email()` and `create_user()`.
- `templates/register.html`: see Templates.
- `templates/login.html`: see Templates.
- `static/css/style.css`: add a `.auth-success` style next to `.auth-error`, built only from
  existing CSS variables (`--accent`, `--accent-light`, `--radius-sm`, etc.).

## Files to create
- `tests/test_registration.py`: pytest tests covering a successful registration, a duplicate email,
  and validation failures (missing fields, bad email, short password). The tests must use a temporary
  database, never the real `expense_tracker.db`.
- `tests/conftest.py`: an `app`/`client` fixture that points `DB_PATH` at a temp file and runs
  `init_db()`.

## New dependencies
No new dependencies. `flask`, `werkzeug`, `pytest` and `pytest-flask` are already in
`requirements.txt`.

## Rules for implementation
- No SQLAlchemy or ORMs. Use `sqlite3` through `get_db()` only.
- Parameterised queries only. Never build SQL with f-strings, `%` or `.format()`.
- Passwords are hashed with werkzeug (`generate_password_hash`). Never store or log the plain password.
- Use CSS variables. Never hardcode hex values in new CSS.
- All templates extend `base.html`.
- Keep all routes in `app.py`. No blueprints, matching the current architecture.
- Validation, done server-side even though the HTML has `required`:
  - Strip whitespace from `name` and `email`. Lowercase `email` before the lookup and the insert.
  - `name` must not be empty.
  - `email` must not be empty and must match a basic `something@something.tld` shape.
  - `password` must be at least 8 characters.
  - The duplicate-email check runs before the insert. Also catch `sqlite3.IntegrityError` on insert as
    a fallback and show the same "email already registered" error.
- On error: re-render `register.html` with a single clear `error` string and HTTP status 400. Only
  the duplicate-email case may return 409 instead.
- On success: `flash()` a success message and redirect (303/302) to `url_for('login')`. Do not log the
  user in. Session handling belongs to Step 3.
- Always close DB connections (`try/finally`, as in `db.py`).
- Do not implement login, logout or the session. Those are Step 3.

## Definition of done
- [ ] `python app.py` starts without errors on http://localhost:5001
- [ ] `GET /register` shows the form, same as before
- [ ] Submitting valid details creates a row in `users` whose `password_hash` is a werkzeug hash, not
      the plain password
- [ ] After a successful sign-up the browser lands on `/login` and shows the "Account created" message
- [ ] Registering again with the same email (in any letter case) shows an "already registered" error and
      creates no second row
- [ ] Registering with `demo@spendly.com` shows the "already registered" error
- [ ] A password shorter than 8 characters is rejected with an error, and no row is created
- [ ] An empty name or a malformed email is rejected with an error, and no row is created
- [ ] After an error, the name and email fields keep their values and the password field is empty
- [ ] The new `.auth-success` style uses only CSS variables (no hex values)
- [ ] `pytest` passes, and the tests do not touch `expense_tracker.db`
