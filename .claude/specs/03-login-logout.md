# Spec: Login and Logout

## Overview
Turn the static `/login` page into a working sign-in flow and replace the `/logout` placeholder
(`"Logout — coming in Step 3"`) with real session handling. Today `GET /login` only renders
`login.html`, whose form POSTs to `/login` with no backend handler. This step adds the POST handler:
it looks up the user by email, verifies the password with werkzeug's `check_password_hash`, stores the
user's id and name in Flask's signed `session` cookie, and redirects into the app. `GET /logout`
clears the session and returns the user to the landing page. The shared nav in `base.html` becomes
session-aware, showing "Sign in / Get started" to guests and the user's name plus "Sign out" to
logged-in users. Login is the gate for everything after it on the Spendly roadmap: the profile page
(Step 4) and all expense CRUD (Steps 7–9) need to know who the current user is.

## Depends on
- **Step 1 — Database setup** (`.claude/specs/01-database-setup.md`): `get_db()`, the `users` table,
  and the seeded demo user (`demo@spendly.com` / `demo123`).
- **Step 2 — Registration** (`.claude/specs/02-registration.md`): `get_user_by_email()` in
  `database/db.py`, `app.secret_key` (needed for `session` and `flash`), flashed-message rendering in
  `login.html`, and the `.auth-success` style.

## Routes
- `GET /login` — render the sign-in form (already exists). If the user is already logged in,
  redirect to `url_for('profile')` instead — public
- `POST /login` — validate credentials; on success start a session and redirect to
  `url_for('profile')`; on failure re-render `login.html` with a generic error and the entered email —
  public
- `GET /logout` — clear the session, flash "You have been signed out.", redirect to
  `url_for('landing')` — public (safe to hit when already logged out)
- `GET /register` — (existing) additionally redirect to `url_for('profile')` if already logged in —
  public

`login()` changes to `methods=["GET", "POST"]`. `logout()` replaces the existing placeholder. No new
URL paths are added. `/profile` stays a placeholder (Step 4) but is the post-login landing spot.

## Database changes
No database changes. The existing `users` table already stores `email` (unique) and `password_hash`.
Reuse `get_user_by_email()` from `database/db.py` — do not add a duplicate lookup helper.

## Templates
- **Create:** none
- **Modify:**
  - `templates/login.html`: keep the entered email in the input after a failed attempt
    (`value="{{ email or '' }}"`); never refill the password. Change the hardcoded
    `action="/login"` to `action="{{ url_for('login') }}"`.
  - `templates/base.html`: make `.nav-links` session-aware. When `session.user_id` is set, show the
    user's name (e.g. `<span class="nav-user">{{ session.user_name }}</span>`) and a "Sign out" link to
    `url_for('logout')`. Otherwise keep the current "Sign in" and "Get started" links.
  - `templates/landing.html`: render flashed messages (so the "You have been signed out." message
    is visible after logout), reusing the `.auth-success` class. If the landing page has no natural
    spot, render flashes in `base.html` just above `{% block content %}` instead — but then remove
    the duplicate flash loop from `login.html` so messages don't render twice.

## Files to change
- `app.py`:
  - Import `session` from `flask` and `check_password_hash` from `werkzeug.security`.
  - Implement `POST /login` inside `login()`.
  - Replace the `logout()` placeholder with the real implementation.
  - Add the already-logged-in redirect to `GET /login` and `GET /register`.
  - Move `logout` out of the "Placeholder routes" section into the main routes section.
- `templates/login.html`: see Templates.
- `templates/base.html`: see Templates.
- `templates/landing.html`: see Templates (only if flashes are rendered there).
- `static/css/style.css`: add a small `.nav-user` style (muted text next to the nav links) using
  existing CSS variables only (`--ink-muted`, `--font-body`, etc.).

## Files to create
- `tests/test_login.py`: pytest tests using the existing `tests/conftest.py` fixtures (temp DB, demo
  user seeded). Cover:
  - successful login with the demo user sets `session["user_id"]` and redirects to `/profile`
  - email is matched case-insensitively and with surrounding whitespace stripped
  - wrong password → 401, generic error, no `user_id` in session
  - unknown email → 401, the *same* generic error text as wrong password
  - empty email or password → 400 with an error
  - logged-in user hitting `GET /login` or `GET /register` is redirected to `/profile`
  - `GET /logout` clears the session and redirects to `/`
  - `GET /logout` while logged out does not error
  - nav shows "Sign out" and the user's name when logged in, "Sign in" when logged out

## New dependencies
No new dependencies. Flask's built-in `session` and `werkzeug.security.check_password_hash` are
already available. Do not add Flask-Login.

## Rules for implementation
- No SQLAlchemy or ORMs. Use `sqlite3` through the helpers in `database/db.py` only.
- Parameterised queries only. Never build SQL with f-strings, `%` or `.format()`.
- Passwords hashed with werkzeug: verify with `check_password_hash(user["password_hash"], password)`.
  Never compare plain text, and never log or re-render the submitted password.
- Use CSS variables — never hardcode hex values in new CSS.
- All templates extend `base.html`.
- Keep all routes in `app.py`. No blueprints, matching the current architecture.
- Normalise the email exactly like registration: `.strip().lower()` before the lookup.
- Use one generic error message for both "no such email" and "wrong password" (e.g. "Invalid email
  or password.") so the form does not reveal which emails are registered. Return HTTP 401 for bad
  credentials and 400 for missing fields.
- On successful login, call `session.clear()` before setting `session["user_id"]` and
  `session["user_name"]`, so no pre-login session data carries over.
- Store only `user_id` and `user_name` in the session — never the password hash or other row data.
- Logout uses `session.clear()` (not just popping one key), then flashes and redirects.
- Redirect after POST (PRG): a successful login must `redirect()`, never render a template directly.
- Do not add a `next` query parameter / open-redirect handling in this step; always redirect to
  `url_for('profile')`.
- Do not implement the profile page, a `login_required` decorator, or any expense routes — those
  belong to Step 4 and later.
- CSRF protection is out of scope for this step (consistent with Step 2); don't add Flask-WTF.

## Definition of done
- [ ] `python app.py` starts without errors on http://localhost:5001
- [ ] Signing in with `demo@spendly.com` / `demo123` redirects to `/profile`
- [ ] Signing in with ` DEMO@Spendly.com ` (mixed case, surrounding spaces) also works
- [ ] A user created via `/register` can sign in with the password they chose
- [ ] A wrong password shows "Invalid email or password.", keeps the email filled in, and leaves the
      password field empty
- [ ] An unregistered email shows the exact same error message as a wrong password
- [ ] Submitting with an empty field shows an error instead of crashing
- [ ] While signed in, the nav shows the user's name and a "Sign out" link instead of "Sign in" /
      "Get started"
- [ ] While signed in, visiting `/login` or `/register` redirects to `/profile`
- [ ] Clicking "Sign out" lands on `/` with a "You have been signed out." message, and the nav shows
      "Sign in" / "Get started" again
- [ ] Visiting `/logout` when not signed in redirects to `/` without an error
- [ ] The browser's session cookie contains no password or password hash
- [ ] The new `.nav-user` style uses only CSS variables (no hex values)
- [ ] `pytest` passes (existing registration tests plus new login tests), and the tests do not touch
      `expense_tracker.db`
