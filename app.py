from flask import Flask, render_template, current_app, g
import click
import sqlite3
from datetime import datetime

app = Flask(__name__)

#Команды работы с БД должны быть тут

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def get_v_info():
    db = get_db()

    with current_app.open_resource('get_v_info.sql') as f:
        db.executescript(f.read().decode('utf8'))


def get_o_info():
        db = get_db()

        with current_app.open_resource('get_o_info.sql') as f:
            db.executescript(f.read().decode('utf8'))


def get_v_passwords():
    db = get_db()

    with current_app.open_resource('get_v_passwords.sql') as f:
        db.executescript(f.read().decode('utf8'))


def get_o_passwords():
    db = get_db()

    with current_app.open_resource('get_o_passwords.sql') as f:
        db.executescript(f.read().decode('utf8'))


# === Главная страница ===
@app.route("/")
def index():
    return render_template("index.html")

# === Каталог мероприятий ===
@app.route("/events")
def events():
    # пока просто отдаём шаблон
    return render_template("events.html")

# === Карточка события ===
@app.route("/events/<int:event_id>")
def event_detail(event_id):
    # пока просто заглушка
    return render_template("event_detail.html", event_id=event_id)

# === Профиль ===
@app.route("/profile")
def profile():
    return render_template("profile.html")

# === Создание события ===
@app.route("/create")
def create_event():
    return render_template("create_event.html")

# === Авторизация ===
@app.route("/login")
def login():
    return render_template("login.html")

# === Запуск приложения ===
if __name__ == "__main__":
    app.run(debug=True)