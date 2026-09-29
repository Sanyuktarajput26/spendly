import shutil
import sys
import tempfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import database.db as db  # noqa: E402

# Redirect the DB to a temp file BEFORE importing app, because app.py runs
# init_db()/seed_db() at import time and must never touch expense_tracker.db.
TEST_DB_DIR = Path(tempfile.mkdtemp(prefix="spendly-tests-"))
db.DB_PATH = TEST_DB_DIR / "test.db"

from app import app as flask_app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _cleanup_test_db_dir():
    yield
    shutil.rmtree(TEST_DB_DIR, ignore_errors=True)


@pytest.fixture
def app():
    flask_app.config.update(TESTING=True)
    return flask_app


@pytest.fixture(autouse=True)
def fresh_db():
    """Give every test a clean schema plus the demo seed data."""
    conn = db.get_db()
    try:
        conn.execute("DROP TABLE IF EXISTS expenses")
        conn.execute("DROP TABLE IF EXISTS users")
        conn.commit()
    finally:
        conn.close()
    db.init_db()
    db.seed_db()
