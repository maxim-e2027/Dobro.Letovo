import bcrypt
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

db = SQLAlchemy()

# ===========================================================
# === ОСНОВНЫЕ ТАБЛИЦЫ (используются в приложении Flask) ===
# ===========================================================

class Volunteer(db.Model, UserMixin):
    __tablename__ = 'Volunteers'

    # Колонки совпадают с существующей базой
    id = db.Column('Volunteer_ID', db.Integer, primary_key=True)
    name = db.Column('Volunteer_Name', db.String(50), nullable=False)
    email = db.Column('Volunteer_Email', db.String(128), unique=True, nullable=False)
    password_hash = db.Column('Volunteer_Password_Hash', db.String(128))
    bio = db.Column('Bio', db.String(255))
    avatar = db.Column('Avatar', db.String(255), nullable=True)
    secret_key = db.Column('Secret_Key', db.String(128))
    rating = db.Column('Volunteer_Rating', db.Integer, default=0)
    hours = db.Column('Volunteer_Hours', db.Integer, default=0)
    description = db.Column('Volunteer_Description', db.String(255))

    # ======================
    # Методы для работы с паролем
    # ======================
    def set_password(self, password: str):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))


class Organisation(db.Model, UserMixin):
    __tablename__ = 'Organisations'
    id = db.Column('Organisation_ID', db.Integer, primary_key=True)
    name = db.Column('Organisation_Name', db.String(50), nullable=False)
    description = db.Column('Organisation_Description', db.String(200))
    email = db.Column('Organisation_Email', db.String(128))
    password_hash = db.Column('Organisation_Password_Hash', db.String(128))

    def set_password(self, password: str):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def __repr__(self):
        return f"<Organisation ID={self.id}, name={self.name}>"

# ===========================================================
# === ДОПОЛНИТЕЛЬНЫЕ ТАБЛИЦЫ АВТОРИЗАЦИИ (из второго файла) ===
# ===========================================================

class VolunteerAuth(db.Model):
    __tablename__ = 'Volunteer_Autentification'
    id = db.Column('Volunteer_ID', db.Integer, db.ForeignKey('Volunteers.Volunteer_ID'), primary_key=True)
    username = db.Column('Volunteer_Username', db.String(128), nullable=False, unique=True)
    email = db.Column('Volunteer_Email', db.String(128), nullable=False, unique=True)
    password_hash = db.Column('Volunteer_Password_Hash', db.String(128), nullable=False)

    def set_password(self, password: str):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

class OrganizationAuth(db.Model):
    __tablename__ = 'Organization_Autentification'
    id = db.Column('Organization_ID', db.Integer, db.ForeignKey('Organisations.Organisation_ID'), primary_key=True)
    username = db.Column('Organization_Username', db.String(128), nullable=False, unique=True)
    email = db.Column('Organization_Email', db.String(128), nullable=False, unique=True)
    password_hash = db.Column('Organization_Password_Hash', db.String(128), nullable=False)

    def set_password(self, password: str):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

# ===========================================================
# === КОММЕНТАРИИ, СОБЫТИЯ, ЗАЯВКИ ===
# ===========================================================

class Comment(db.Model):
    __tablename__ = 'Comments'
    id = db.Column('Comment_ID', db.Integer, primary_key=True)
    event_id = db.Column('Event_ID', db.Integer, db.ForeignKey('Volunteers.Volunteer_ID'), nullable=False)
    volunteer_id = db.Column('Volunteer_ID', db.Integer, db.ForeignKey('Volunteers.Volunteer_ID'), nullable=False)
    organisation_id = db.Column('Organisation_ID', db.Integer, db.ForeignKey('Organisations.Organisation_ID'), nullable=False)
    date = db.Column('Comment_Date', db.String(10))
    text = db.Column('Comment_Text', db.String(1000))
    direction = db.Column('Comment_Direction', db.String(2))  # VO / OV

    def __repr__(self):
        return f"<Comment ID={self.id}, Volunteer={self.volunteer_id}, Org={self.organisation_id}>"

class Event(db.Model):
    __tablename__ = 'Events'
    id = db.Column('Event_ID', db.Integer, primary_key=True)
    organisation_id = db.Column('Organisation_ID', db.Integer, db.ForeignKey('Organisations.Organisation_ID'))
    required_volunteers = db.Column('Required_Volunteers', db.Integer)
    date = db.Column('Event_Date', db.String(10))
    description = db.Column('Event_Description', db.String(200))
    name = db.Column('Event_Name', db.String(50))
    category = db.Column('Category', db.String(50))

    def __repr__(self):
        return f"<Event ID={self.id}, name={self.name}, required={self.required_volunteers}>"

class Request(db.Model):
    __tablename__ = 'Requests'
    id = db.Column('Request_ID', db.Integer, primary_key=True)
    volunteer_id = db.Column('Volunteer_ID', db.Integer, db.ForeignKey('Volunteers.Volunteer_ID'))
    event_id = db.Column('Event_ID', db.Integer, db.ForeignKey('Events.Event_ID'))
    status = db.Column('Request_Status', db.String(20))
    content = db.Column('Request_Content', db.String(255))

    def __repr__(self):
        return f"<Request ID={self.id}, Volunteer={self.volunteer_id}, Event={self.event_id}, Status={self.status}>"

# ===========================================================
# === ФУНКЦИИ РЕГИСТРАЦИИ (из второго файла) ===
# ===========================================================

def register_volunteer(username: str, password: str, name: str, description: str):
    """Регистрирует волонтёра (из второй модели)."""
    if VolunteerAuth.query.filter_by(username=username).first():
        return "Username already exists"

    last_id = db.session.query(func.max(Volunteer.id)).scalar() or 0
    new_id = last_id + 1

    auth_entry = VolunteerAuth(id=new_id, username=username, email=f"{username}@example.com")
    auth_entry.set_password(password)

    profile = Volunteer(id=new_id, name=name, description=description, rating=100, hours=0)
    db.session.add_all([auth_entry, profile])
    db.session.commit()

    return f"Volunteer '{username}' registered successfully"

def register_organization(username: str, password: str, name: str, description: str):
    """Регистрирует организацию (из второй модели)."""
    if OrganizationAuth.query.filter_by(username=username).first():
        return "Username already exists"

    last_id = db.session.query(func.max(Organisation.id)).scalar() or 0
    new_id = last_id + 1

    auth_entry = OrganizationAuth(id=new_id, username=username, email=f"{username}@example.com")
    auth_entry.set_password(password)

    org_profile = Organisation(id=new_id, name=name, description=description)
    db.session.add_all([auth_entry, org_profile])
    db.session.commit()

    return f"Organization '{username}' registered successfully"

# ===========================================================
# === ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ ЧЕРЕЗ SQL-СКРИПТ (SQLite) ===
# ===========================================================

def init_database_with_sqlite(app, sql_path: str = "schema_full_sqlite.sql"):
    """
    Инициализирует базу данных SQLite, выполняя SQL-скрипт (DDL).
    Поддерживает создание таблиц, индексов и VIEW.
    SQLite не поддерживает EXTENSION, ENUM, TRIGGER на plpgsql,
    поэтому такие конструкции должны быть удалены из SQL-файла.
    """
    import os
    from sqlalchemy import text

    with app.app_context():
        engine = db.engine

        if not os.path.exists(sql_path):
            raise FileNotFoundError(f"SQL-файл не найден: {sql_path}")

        with open(sql_path, "r", encoding="utf-8") as f:
            sql_script = f.read()

        # SQLite позволяет выполнять несколько выражений за один exec()
        # Но для надёжности разбиваем вручную по ";"
        statements = [stmt.strip() for stmt in sql_script.split(";") if stmt.strip()]

        with engine.connect() as conn:
            for stmt in statements:
                try:
                    conn.execute(text(stmt))
                except Exception as e:
                    print(f"[SQLite SQL ERROR] {e} при выполнении: {stmt[:120]}...")
            conn.commit()

        print("✅ SQLite schema успешно применена из:", sql_path)
