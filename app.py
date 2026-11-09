import hashlib
import sqlite3

from flask import Flask, g, redirect, render_template_string, request, session, url_for

app = Flask(__name__)
app.secret_key = "supersecret123"

DATABASE = "notes.db"

BASE = """
<!doctype html>
<title>Notas</title>
<h1>App de notas</h1>
<nav>
  {% if session.get('user') %}
    Hola, {{ session['user'] }} |
    <a href="{{ url_for('notes') }}">Mis notas</a> |
    <a href="{{ url_for('logout') }}">Salir</a>
  {% else %}
    <a href="{{ url_for('login') }}">Entrar</a> |
    <a href="{{ url_for('register') }}">Registro</a>
  {% endif %}
</nav>
<hr>
{{ body|safe }}
"""


def page(body):
    return render_template_string(BASE, body=body)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    db.execute(
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "username TEXT UNIQUE, password TEXT)"
    )
    db.execute(
        "CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "user_id INTEGER, title TEXT, content TEXT)"
    )
    db.commit()
    db.close()


def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()


@app.route("/")
def index():
    if session.get("user"):
        return redirect(url_for("notes"))
    return page("<p>Bienvenido. Entra o crea una cuenta.</p>")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = hash_password(request.form["password"])
        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password),
            )
            db.commit()
        except sqlite3.IntegrityError:
            return page("<p>Ese usuario ya existe.</p>")
        return redirect(url_for("login"))
    return page(
        "<h2>Registro</h2><form method='post'>"
        "Usuario: <input name='username'><br>"
        "Contraseña: <input name='password' type='password'><br>"
        "<button>Crear cuenta</button></form>"
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = hash_password(request.form["password"])
        db = get_db()
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        user = db.execute(query).fetchone()
        if user:
            session["user"] = user["username"]
            session["user_id"] = user["id"]
            return redirect(url_for("notes"))
        return page("<p>Usuario o contraseña incorrectos.</p>")
    return page(
        "<h2>Entrar</h2><form method='post'>"
        "Usuario: <input name='username'><br>"
        "Contraseña: <input name='password' type='password'><br>"
        "<button>Entrar</button></form>"
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/notes", methods=["GET", "POST"])
def notes():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    db = get_db()
    if request.method == "POST":
        db.execute(
            "INSERT INTO notes (user_id, title, content) VALUES (?, ?, ?)",
            (session["user_id"], request.form["title"], request.form["content"]),
        )
        db.commit()
    rows = db.execute(
        "SELECT * FROM notes WHERE user_id = ?", (session["user_id"],)
    ).fetchall()
    items = "".join(
        f"<li><a href='/note/{r['id']}'>{r['title']}</a></li>" for r in rows
    )
    return page(
        "<h2>Mis notas</h2><ul>" + items + "</ul>"
        "<h3>Nueva nota</h3><form method='post'>"
        "Título: <input name='title'><br>"
        "Contenido: <textarea name='content'></textarea><br>"
        "<button>Guardar</button></form>"
    )


@app.route("/note/<int:note_id>")
def note(note_id):
    if not session.get("user_id"):
        return redirect(url_for("login"))
    db = get_db()
    row = db.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    if row is None:
        return page("<p>Nota no encontrada.</p>"), 404
    return page(f"<h2>{row['title']}</h2><div>{row['content']}</div>")


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
