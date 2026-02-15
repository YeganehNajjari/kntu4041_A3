import sqlite3
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
import requests
from flask import Response, request

@app.get("/geoserver/wms")
def geoserver_wms_proxy():
    geoserver_wms = "http://localhost:8080/geoserver/wms"
    upstream = requests.get(geoserver_wms, params=request.args, stream=True)

    resp = Response(upstream.content, status=upstream.status_code)
    # مهم: نوع محتوا (png/json/xml) حفظ بشه
    if "Content-Type" in upstream.headers:
        resp.headers["Content-Type"] = upstream.headers["Content-Type"]
    return resp
app.secret_key = "CHANGE_ME_TO_A_RANDOM_SECRET"
DB_PATH = "users.db"


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        """)
        conn.commit()


def get_user_by_username(username: str):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, username, email, password_hash FROM users WHERE username = ?", (username,))
        return cur.fetchone()


def get_user_by_email(email: str):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, username, email, password_hash FROM users WHERE email = ?", (email,))
        return cur.fetchone()


def create_user(username: str, email: str, password: str):
    password_hash = generate_password_hash(password)
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash),
        )
        conn.commit()


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper


@app.route("/")
def home():
    if session.get("user_id"):
        return redirect(url_for("map_page"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not username or not email or not password:
            flash("All fields are required.", "error")
            return redirect(url_for("register"))

        if password != confirm:
            flash("Passwords do not match.", "error")
            return redirect(url_for("register"))

        if get_user_by_username(username):
            flash("Username already taken.", "error")
            return redirect(url_for("register"))

        if get_user_by_email(email):
            flash("Email already registered.", "error")
            return redirect(url_for("register"))

        create_user(username, email, password)
        flash("Registration successful. Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = get_user_by_username(username)
        if not user:
            flash("Invalid username or password.", "error")
            return redirect(url_for("login"))

        user_id, _username, _email, password_hash = user
        if not check_password_hash(password_hash, password):
            flash("Invalid username or password.", "error")
            return redirect(url_for("login"))

        session["user_id"] = user_id
        session["username"] = _username
        return redirect(url_for("map_page"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/map")
@login_required
def map_page():
    return render_template("map.html", username=session.get("username"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)

