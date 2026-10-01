import re
from pathlib import Path

import database.db as db

PROJECT_ROOT = Path(__file__).resolve().parent.parent
HEX_COLOUR_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b")
DEMO_FORM = {"email": db.DEMO_EMAIL, "password": db.DEMO_PASSWORD}


def get_profile(client):
    client.post("/login", data=DEMO_FORM)
    return client.get("/profile")


def test_profile_logged_out_redirects_to_login(client):
    response = client.get("/profile")
    assert response.status_code in (302, 303)
    assert response.headers["Location"].endswith("/login")


def test_profile_logged_in_ok(client):
    response = get_profile(client)
    assert response.status_code == 200
    assert b"coming in Step 4" not in response.data


def test_profile_shows_user_card(client):
    html = get_profile(client).get_data(as_text=True)
    assert 'class="profile-avatar">DU<' in html
    assert "Demo User" in html
    assert "demo@spendly.com" in html
    assert "Member since" in html


def test_profile_shows_summary_stats(client):
    html = get_profile(client).get_data(as_text=True)
    assert html.count('class="stat-card"') >= 3
    assert "₹377.49" in html
    assert "Top category" in html


def test_profile_shows_transactions(client):
    html = get_profile(client).get_data(as_text=True)
    tbody = html.split("<tbody>")[1].split("</tbody>")[0]
    assert tbody.count("<tr>") >= 3
    assert 'class="badge badge-food"' in tbody
    assert "Weekly grocery shop" in tbody


def test_profile_shows_category_breakdown(client):
    html = get_profile(client).get_data(as_text=True)
    assert html.count('class="category-row"') >= 3
    for category in db.CATEGORIES:
        assert f'class="category-name">{category}<' in html


def test_profile_nav_shows_logged_in_state(client):
    html = get_profile(client).get_data(as_text=True)
    assert "Sign out" in html
    assert 'class="nav-user">Demo User<' in html


def test_profile_has_no_inline_styles(client):
    html = get_profile(client).get_data(as_text=True)
    assert "style=" not in html
    assert "<style" not in html


def test_profile_files_have_no_hex_colours():
    for path in ("templates/profile.html", "static/css/profile.css"):
        source = (PROJECT_ROOT / path).read_text(encoding="utf-8")
        assert HEX_COLOUR_RE.search(source) is None, path
