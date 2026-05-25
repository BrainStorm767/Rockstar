from flask import Flask, render_template, request, redirect, session
import sqlite3
import uuid
import os

from werkzeug.utils import secure_filename

# =========================
# APP
# =========================

app = Flask(__name__)

app.secret_key = "rockstar_secret"

# =========================
# UPLOADS
# =========================

UPLOAD_FOLDER = "static/uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# =========================
# DATABASE
# =========================

def get_db():

    conn = sqlite3.connect("shop.db")

    conn.row_factory = sqlite3.Row

    return conn

# =========================
# INIT DATABASE
# =========================

def init_db():

    conn = get_db()

    cur = conn.cursor()

    # PRODUCTS

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS products(
            id TEXT PRIMARY KEY,
            name TEXT,
            price TEXT,
            image TEXT,
            description TEXT
        )
        """
    )

    # USERS

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users(
            id TEXT PRIMARY KEY,
            username TEXT,
            password TEXT
        )
        """
    )

    conn.commit()

    conn.close()

# =========================
# HOME
# =========================

@app.route("/")
def home():

    if not session.get("admin"):

        return redirect("/login")

    conn = get_db()

    products = conn.execute(
        "SELECT * FROM products"
    ).fetchall()

    conn.close()

    return render_template(
        "index.html",
        products=products
    )

# =========================
# LOGIN PAGE
# =========================

@app.route("/login")
def login():

    if session.get("admin"):

        return redirect("/")

    return render_template("login.html")

# =========================
# SIGNUP PAGE
# =========================

@app.route("/signup")
def signup():

    return render_template("signup.html")

# =========================
# SIGNUP ACTION
# =========================

@app.route("/signup-action", methods=["POST"])
def signup_action():

    username = request.form["username"]

    password = request.form["password"]

    conn = get_db()

    conn.execute(
        """
        INSERT INTO users
        (id, username, password)
        VALUES (?, ?, ?)
        """,
        (
            str(uuid.uuid4()),
            username,
            password
        )
    )

    conn.commit()

    conn.close()

    return redirect("/login")

# =========================
# LOGIN ACTION
# =========================

@app.route("/login-action", methods=["POST"])
def login_action():

    username = request.form["username"]

    password = request.form["password"]

    conn = get_db()

    user = conn.execute(
        """
        SELECT * FROM users
        WHERE username=? AND password=?
        """,
        (
            username,
            password
        )
    ).fetchone()

    conn.close()

    if user:

        session["admin"] = True

        session["username"] = username

        return redirect("/")

    return redirect("/login")

# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

# =========================
# ADMIN PANEL
# =========================

@app.route("/admin")
def admin():

    return redirect("/admin-panel")

@app.route("/admin-panel")
def admin_panel():

    if not session.get("admin"):

        return redirect("/login")

    conn = get_db()

    products = conn.execute(
        "SELECT * FROM products"
    ).fetchall()

    conn.close()

    return render_template(
        "admin.html",
        products=products
    )

# =========================
# ADD PRODUCT
# =========================

@app.route("/add", methods=["POST"])
def add():

    if not session.get("admin"):

        return redirect("/login")

    name = request.form["name"]

    price = request.form["price"]

    description = request.form["description"]

    file = request.files["image"]

    filename = secure_filename(file.filename)

    unique_name = str(uuid.uuid4()) + "_" + filename

    save_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        unique_name
    )

    file.save(save_path)

    image_url = "/static/uploads/" + unique_name

    conn = get_db()

    conn.execute(
        """
        INSERT INTO products
        (id, name, price, image, description)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            str(uuid.uuid4()),
            name,
            price,
            image_url,
            description
        )
    )

    conn.commit()

    conn.close()

    return redirect("/admin-panel")

# =========================
# PRODUCT PAGE
# =========================

@app.route("/product/<pid>")
def product(pid):

    if not session.get("admin"):

        return redirect("/login")

    conn = get_db()

    product = conn.execute(
        "SELECT * FROM products WHERE id=?",
        (pid,)
    ).fetchone()

    conn.close()

    return render_template(
        "product.html",
        product=product
    )

# =========================
# DELETE PRODUCT
# =========================

@app.route("/delete/<pid>")
def delete(pid):

    if not session.get("admin"):

        return redirect("/login")

    conn = get_db()

    conn.execute(
        "DELETE FROM products WHERE id=?",
        (pid,)
    )

    conn.commit()

    conn.close()

    return redirect("/admin-panel")

# =========================
# RUN
# =========================

if __name__ == "__main__":

    init_db()

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )