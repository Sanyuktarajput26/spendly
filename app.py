import os
import re
import sqlite3

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from database.db import create_user, get_db, get_user_by_email, init_db, seed_db

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LENGTH = 8
# Same message for unknown email and wrong password, so the form doesn't reveal registered emails.
INVALID_LOGIN_MSG = "Invalid email or password."

app = Flask(__name__)
# Dev-only fallback; set SECRET_KEY in the environment for any real deployment.
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-insecure-secret-key")

with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("profile"))

    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    def form_error(message, status=400):
        return render_template("register.html", error=message, name=name, email=email), status

    if not name:
        return form_error("Please enter your name.")
    if not EMAIL_RE.match(email):
        return form_error("Please enter a valid email address.")
    if len(password) < MIN_PASSWORD_LENGTH:
        return form_error(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
    if get_user_by_email(email) is not None:
        return form_error("An account with this email already exists.", 409)

    try:
        create_user(name, email, password)
    except sqlite3.IntegrityError:
        return form_error("An account with this email already exists.", 409)

    flash("Account created — please sign in.", "success")
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("profile"))

    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    def form_error(message, status):
        return render_template("login.html", error=message, email=email), status

    if not email or not password:
        return form_error("Please enter your email and password.", 400)

    user = get_user_by_email(email)
    if user is None or not check_password_hash(user["password_hash"], password):
        return form_error(INVALID_LOGIN_MSG, 401)

    # Start a fresh session so no pre-login data carries over.
    session.clear()
    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    return redirect(url_for("profile"))


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out.", "success")
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    # Placeholder data mirroring the seed_db() demo expenses — replaced by database queries in Step 5.
    user = {
        "name": "Demo User",
        "email": "demo@spendly.com",
        "initials": "DU",
        "member_since": "September 2026",
    }
    stats = {
        "total_spent": 377.49,
        "transaction_count": 8,
        "top_category": "Health",
    }
    transactions = [
        {"date": "2026-09-18", "description": "Dinner with friends", "category": "Food", "amount": 22.75},
        {"date": "2026-09-15", "description": "Miscellaneous", "category": "Other", "amount": 15.00},
        {"date": "2026-09-12", "description": "New shoes", "category": "Shopping", "amount": 35.25},
        {"date": "2026-09-10", "description": "Concert tickets", "category": "Entertainment", "amount": 60.00},
        {"date": "2026-09-07", "description": "Gym membership", "category": "Health", "amount": 100.00},
        {"date": "2026-09-05", "description": "Electricity bill", "category": "Bills", "amount": 89.99},
        {"date": "2026-09-03", "description": "Metro card top-up", "category": "Transport", "amount": 12.00},
        {"date": "2026-09-01", "description": "Weekly grocery shop", "category": "Food", "amount": 42.50},
    ]
    categories = [
        {"name": "Health", "amount": 100.00, "percent": 26},
        {"name": "Bills", "amount": 89.99, "percent": 24},
        {"name": "Food", "amount": 65.25, "percent": 17},
        {"name": "Entertainment", "amount": 60.00, "percent": 16},
        {"name": "Shopping", "amount": 35.25, "percent": 9},
        {"name": "Other", "amount": 15.00, "percent": 4},
        {"name": "Transport", "amount": 12.00, "percent": 3},
    ]
    return render_template(
        "profile.html", user=user, stats=stats, transactions=transactions, categories=categories
    )


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
