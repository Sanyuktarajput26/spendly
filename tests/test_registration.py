from werkzeug.security import check_password_hash

import database.db as db

VALID_FORM = {"name": "Asha Verma", "email": "asha@example.com", "password": "supersecret"}


def count_users(email):
    conn = db.get_db()
    try:
        return conn.execute("SELECT COUNT(*) FROM users WHERE email = ?", (email,)).fetchone()[0]
    finally:
        conn.close()


def test_get_register_shows_form(client):
    response = client.get("/register")
    assert response.status_code == 200
    assert b'<form method="POST" action="/register">' in response.data


def test_valid_registration_creates_user_and_redirects(client):
    response = client.post("/register", data=VALID_FORM)
    assert response.status_code in (302, 303)
    assert response.headers["Location"].endswith("/login")

    user = db.get_user_by_email("asha@example.com")
    assert user is not None
    assert user["name"] == "Asha Verma"
    assert user["password_hash"] != VALID_FORM["password"]
    assert check_password_hash(user["password_hash"], VALID_FORM["password"])


def test_success_message_shown_on_login(client):
    response = client.post("/register", data=VALID_FORM, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == "/login"
    assert "Account created".encode() in response.data
    assert b"auth-success" in response.data


def test_email_is_normalised(client):
    client.post("/register", data={**VALID_FORM, "email": "  Asha@Example.COM  "})
    assert count_users("asha@example.com") == 1


def test_duplicate_email_rejected_case_insensitively(client):
    client.post("/register", data=VALID_FORM)
    response = client.post("/register", data={**VALID_FORM, "email": "ASHA@example.com"})
    assert response.status_code == 409
    assert b"already exists" in response.data
    assert count_users("asha@example.com") == 1


def test_seeded_demo_email_rejected(client):
    response = client.post("/register", data={**VALID_FORM, "email": db.DEMO_EMAIL})
    assert response.status_code == 409
    assert b"already exists" in response.data
    assert count_users(db.DEMO_EMAIL) == 1


def test_short_password_rejected(client):
    response = client.post("/register", data={**VALID_FORM, "password": "short"})
    assert response.status_code == 400
    assert b"at least 8 characters" in response.data
    assert count_users("asha@example.com") == 0


def test_empty_name_rejected(client):
    response = client.post("/register", data={**VALID_FORM, "name": "   "})
    assert response.status_code == 400
    assert b"enter your name" in response.data
    assert count_users("asha@example.com") == 0


def test_malformed_email_rejected(client):
    response = client.post("/register", data={**VALID_FORM, "email": "not-an-email"})
    assert response.status_code == 400
    assert b"valid email" in response.data
    assert count_users("not-an-email") == 0


def test_form_values_kept_after_error_but_not_password(client):
    response = client.post("/register", data={**VALID_FORM, "password": "short"})
    assert b'value="Asha Verma"' in response.data
    assert b'value="asha@example.com"' in response.data
    assert b"short" not in response.data
