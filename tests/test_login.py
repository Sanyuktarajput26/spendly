import database.db as db

DEMO_FORM = {"email": db.DEMO_EMAIL, "password": db.DEMO_PASSWORD}
INVALID_LOGIN = b"Invalid email or password."


def log_in(client, **overrides):
    return client.post("/login", data={**DEMO_FORM, **overrides})


def test_get_login_shows_form(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b'<form method="POST" action="/login">' in response.data


def test_demo_login_redirects_to_profile(client):
    response = log_in(client)
    assert response.status_code in (302, 303)
    assert response.headers["Location"].endswith("/profile")

    demo = db.get_user_by_email(db.DEMO_EMAIL)
    with client.session_transaction() as sess:
        assert sess["user_id"] == demo["id"]
        assert sess["user_name"] == demo["name"]


def test_login_email_case_and_whitespace_insensitive(client):
    response = log_in(client, email="  DEMO@Spendly.com  ")
    assert response.status_code in (302, 303)
    with client.session_transaction() as sess:
        assert "user_id" in sess


def test_registered_user_can_login(client):
    client.post(
        "/register",
        data={"name": "Asha Verma", "email": "asha@example.com", "password": "supersecret"},
    )
    response = log_in(client, email="asha@example.com", password="supersecret")
    assert response.status_code in (302, 303)
    with client.session_transaction() as sess:
        assert sess["user_name"] == "Asha Verma"


def test_wrong_password_401_generic_error(client):
    response = log_in(client, password="wrong-password")
    assert response.status_code == 401
    assert INVALID_LOGIN in response.data
    assert f'value="{db.DEMO_EMAIL}"'.encode() in response.data
    assert b"wrong-password" not in response.data
    with client.session_transaction() as sess:
        assert "user_id" not in sess


def test_unknown_email_same_error(client):
    response = log_in(client, email="nobody@example.com")
    assert response.status_code == 401
    assert INVALID_LOGIN in response.data
    with client.session_transaction() as sess:
        assert "user_id" not in sess


def test_empty_fields_400(client):
    assert log_in(client, email="").status_code == 400
    assert log_in(client, password="").status_code == 400
    with client.session_transaction() as sess:
        assert "user_id" not in sess


def test_logged_in_redirected_from_login_and_register(client):
    log_in(client)
    for path in ("/login", "/register"):
        response = client.get(path)
        assert response.status_code in (302, 303)
        assert response.headers["Location"].endswith("/profile")


def test_logout_clears_session_and_redirects(client):
    log_in(client)
    response = client.get("/logout")
    assert response.status_code in (302, 303)
    assert response.headers["Location"].endswith("/")
    with client.session_transaction() as sess:
        assert "user_id" not in sess
        assert "user_name" not in sess

    landing = client.get("/")
    assert b"You have been signed out." in landing.data


def test_logout_when_logged_out_ok(client):
    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == "/"


def test_nav_reflects_auth_state(client):
    signed_out = client.get("/").data
    assert b"Sign in" in signed_out
    assert b"Sign out" not in signed_out

    log_in(client)
    signed_in = client.get("/").data
    assert b"Sign out" in signed_in
    assert b"Demo User" in signed_in
    assert b"Sign in" not in signed_in


def test_session_has_no_password_data(client):
    log_in(client)
    with client.session_transaction() as sess:
        assert set(sess.keys()) <= {"user_id", "user_name", "_flashes"}
