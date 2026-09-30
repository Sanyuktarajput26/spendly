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


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/profile")
def profile():
    return "Profile page — coming in Step 4"


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
