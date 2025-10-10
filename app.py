from flask import Flask, render_template, current_app, g
import click
import sqlite3
from datetime import datetime

app = Flask(__name__)
global new_file
new_file = 0
global i_d
i_d = 0

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


def get_v_password(login):
    db = get_db()
    db.executescript('SELECT * FROM Volunteer_Autentification'
                     'WHERE Volunteer_Username = "'+login + '";')

def get_o_password(login):
    db = get_db()
    db.executescript(('SELECT * FROM Organization_Autentification'
                     'WHERE Organization_Username = "'+login + '";'))


def create_event(req_ppl, date, desc, o_id, name):
    """
    Creates an event
    :param req_ppl: How many ppl u need
    :param date: date of event
    :param desc: description
    :return: nothin
    """
    db = get_db()
    e_id = db.executescript('SELECT Event_ID FROM Event'
                              'ORDER BY Event_ID DESC'
                              'LIMIT 1 OFFSET 0')
    db.executescript('INSERT INTO Event'
                     'VALUES ('+str(e_id)+', '+o_id+', '+req_ppl+', '+date+', '+desc+', '+name+');')


def create_request(v_id, e_id, content):
    db = get_db()
    r_id = db.executescript('SELECT Request_ID FROM Request'
                            'ORDER BY Request_ID DESC'
                            'LIMIT 1 OFFSET 0')
    db.executescript('INSERT INTO Event'
                     'VALUES (' + str(r_id) + ', ' + v_id + ', ' + e_id + ', "AWAITING APPROVAL", ' + content + ');')


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


@app.route("/create", methods=["POST"])
def event_store():
    name = Flask.request.form.get('title')
    date = Flask.request.form.get('date')
    location = Flask.request.form.get('location')
    capacity = Flask.request.form.get('capacity')
    desc = Flask.request.form.get('description')
    f = open('e'+str(new_file), 'w')
    ds = 'e'+str(new_file)
    f.write(desc)
    f.close
    new_file += 1
    create_event(capacity, date, ds, i_d, name)


# === Авторизация ===
@app.route("/login")
def login():
    return render_template("login.html")

# === Запуск приложения ===
if __name__ == "__main__":
    app.run(debug=True)
