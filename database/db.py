import sqlite3
from pathlib import Path

from werkzeug.security import generate_password_hash

DB_PATH = Path(__file__).resolve().parent.parent / "expense_tracker.db"

CREATE_USERS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

CREATE_EXPENSES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS expenses (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    amount      REAL NOT NULL,
    category    TEXT NOT NULL,
    date        TEXT NOT NULL,
    description TEXT,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
"""

DEMO_EMAIL = "demo@spendly.com"
DEMO_PASSWORD = "demo123"  # dev-only demo login, used once the /login route is implemented

CATEGORIES = ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]


def get_db():
    """Return a new SQLite connection with row access by column name and FK enforcement on."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_user_by_email(email):
    """Return the user row matching this email, or None if no such user exists."""
    conn = get_db()
    try:
        return conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    finally:
        conn.close()


def create_user(name, email, password):
    """Insert a new user with a hashed password and return the new user's id."""
    conn = get_db()
    try:
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, generate_password_hash(password)),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def init_db():
    """Create all tables if they don't already exist."""
    conn = get_db()
    try:
        conn.execute(CREATE_USERS_TABLE_SQL)
        conn.execute(CREATE_EXPENSES_TABLE_SQL)
        conn.commit()
    finally:
        conn.close()


def seed_db():
    """Insert a demo user and sample expenses for local development, if not already present."""
    conn = get_db()
    try:
        existing = conn.execute("SELECT 1 FROM users LIMIT 1").fetchone()
        if existing is not None:
            return

        password_hash = generate_password_hash(DEMO_PASSWORD)
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", DEMO_EMAIL, password_hash),
        )
        user_id = cursor.lastrowid

        # One expense per category, plus an extra Food entry to reach 8 total.
        sample_expenses = [
            (user_id, 42.50, "Food", "2026-09-01", "Weekly grocery shop"),
            (user_id, 12.00, "Transport", "2026-09-03", "Metro card top-up"),
            (user_id, 89.99, "Bills", "2026-09-05", "Electricity bill"),
            (user_id, 100.00, "Health", "2026-09-07", "Gym membership"),
            (user_id, 60.00, "Entertainment", "2026-09-10", "Concert tickets"),
            (user_id, 35.25, "Shopping", "2026-09-12", "New shoes"),
            (user_id, 15.00, "Other", "2026-09-15", "Miscellaneous"),
            (user_id, 22.75, "Food", "2026-09-18", "Dinner with friends"),
        ]
        conn.executemany(
            """
            INSERT INTO expenses (user_id, amount, category, date, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            sample_expenses,
        )
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    seed_db()
    print(f"Database initialized at {DB_PATH}")
