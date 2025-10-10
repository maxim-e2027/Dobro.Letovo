from flask import Flask, render_template, current_app, g
import click
import sqlite3
import bcrypt
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


def get_volunteer_password(login):
    db = get_db()
    db.executescript('SELECT * FROM Volunteer_Autentification'
                     'WHERE Volunteer_Username = "'+login + '";')

def get_organization_password(login):
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


def register_volunteer(username: str, password: str, name: str, description: str):
    if session.query(Volunteer_Autentification).filter_by(Volunteer_Username=username).first():
        print("Username already exists.")
        return "Username already exists"

    # Get max ID
    last_id = session.query(func.max(Volunteer.Volunteer_ID)).scalar()
    new_id = (last_id or 0) + 1  # If no volunteers yet, start from 1

    # Create authentification entry
    user_auth = Volunteer_Autentification(Volunteer_ID=new_id, Volunteer_Username=username)
    user_auth.set_password(password)
    session.add(user_auth)

    # Create Volunteer profile
    user_profile = Volunteer(
        Volunteer_ID=new_id,
        Volunteer_Name=name,
        Volunteer_Description=description,
        Volunteer_Rating=100,
        Volunteer_Hours=0
    )
    session.add(user_profile)

    session.commit()
    print(f"User '{username}' registered successfully.")

def register_organization(username: str, password: str, name: str, description: str):
    if session.query(Organzation_Autentification).filter_by(username=username).first():
        print("Username already exists.")
        return "Username already exists"

    #Get max ID
    last_id = session.query(func.max(Organisation.Organization_ID)).scalar()
    new_id = (last_id or 0) + 1  # If no volunteers yet, start from 1

    #Create authentification entry
    user_auth = Organzation_Autentification(Organization_ID = new_id, username=username)
    user_auth.set_password(password)
    session.add(user_auth)

    #Create Volunteerprofile
    user_profile = Volunteer(
        Organization_ID = new_id,
        Organization_Name = name,
        Organization_Description = description
    )
    session.add(user_profile)

    session.commit()
    print(f"User '{username}' registered successfully.")

def alter_request(request_id: int, new_status: str) -> None:
    db = get_db()
    (db.executescript
    (f'''UPDATE Request"
    "SET Request_ID = {request_id}
        Request_Status = {new_status}'''))

def check_login_volunteer(email: str, password: str) -> bool:
    db = get_db()

    password_correct = db.executescript(f''' SELECT Volunteer_Password_Hash FROM Volunteer_Autentification
    WHERE Volunteer_Email = {email}''')
    if vounteer_id == '':
        return False
    return bcrypt.checkpw(password.encode('utf-8'), password_correct.encode('utf-8'))

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
    db = get.db()
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
    if check_login_volunteer((email, password)):
        print('Successful Login')
    else:
        print('Wrong email or password')
    return render_template("login.html")

# === Запуск приложения ===
if __name__ == "__main__":
    app.run(debug=True)