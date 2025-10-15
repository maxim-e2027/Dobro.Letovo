import os
from models import db, Event, Comment, Request, Volunteer, Organisation, init_database_with_sqlite
from flask_migrate import Migrate
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user
from werkzeug.utils import secure_filename
from datetime import datetime

# ============================================
# === НАСТРОЙКИ ХРАНЕНИЯ ФАЙЛОВ И FLASK ===
# ============================================
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///dobro.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "super-secret-key-123"

# ============================================
# === ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ ===
# ============================================
db.init_app(app)
migrate = Migrate(app, db)

SQL_FILE = "schema_full_sqlite.sql"
with app.app_context():
    if not os.path.exists("dobro.db"):
        print("⚙️  База данных не найдена. Создаю из SQL-скрипта...")
        init_database_with_sqlite(app, SQL_FILE)
    else:
        print("✅ База данных уже существует. Пропускаю инициализацию.")

# ============================================
# === LOGIN MANAGER ===
# ============================================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

def load_user(user_id):
    user = Volunteer.query.get(int(user_id))
    if not user:
        user = Organisation.query.get(int(user_id))
    return user

# ============================================
# === ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ ===
# ============================================
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ============================================
# === МАРШРУТЫ ===
# ============================================

@app.route("/")
def index():
    return render_template("index.html")

# --- Каталог мероприятий с фильтрами ---
@app.route("/events")
def events():
    events = Event.query.all()
    for e in events:
        try:
            e.formatted_date = datetime.strptime(e.date, "%Y-%m-%d").strftime("%d.%m.%Y")
        except:
            e.formatted_date = e.date
    return render_template("events.html", events=events)

# --- Детали события ---
@app.route("/events/<int:event_id>")
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    comments = Comment.query.filter_by(event_id=event_id).all()
    return render_template("event_detail.html", event=event, comments=comments)

# --- Присоединиться к событию ---
@app.route("/events/<int:event_id>/join", methods=["POST"])
def join_event(event_id):
    volunteer = Volunteer.query.first()
    if volunteer:
        req = Request(volunteer_id=volunteer.id, event_id=event_id, status="pending")
        db.session.add(req)
        db.session.commit()
        return redirect(url_for("event_detail", event_id=event_id))
    return "Нет волонтёров для теста!"

# --- Комментарии к событию ---
@app.route("/events/<int:event_id>/comments", methods=["POST"])
def event_comments(event_id):
    author_id = request.form.get("volunteer_id")
    content = request.form.get("content")

    if not content.strip():
        return redirect(url_for("event_detail", event_id=event_id))

    new_comment = Comment(text=content, volunteer_id=author_id, event_id=event_id)
    db.session.add(new_comment)
    db.session.commit()
    return redirect(url_for("event_detail", event_id=event_id))

# ===================================================
# === Редактирование профиля ===
# ===================================================
@app.route("/profile/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
def edit_profile(user_id):
    user = Volunteer.query.get_or_404(user_id)

    if request.method == "POST":
        user.name = request.form.get("name")
        user.email = request.form.get("email")
        user.bio = request.form.get("bio", "")

        if "avatar" in request.files:
            file = request.files["avatar"]
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(filepath)
                user.avatar = f"uploads/{filename}"

        db.session.commit()
        flash("Профиль успешно обновлён!", "success")
        return redirect(url_for("profile", user_id=user.id))

    return render_template("edit_profile.html", user=user)

# === Создание события ===
@app.route("/create")
def create_event():
    return render_template("create_event.html")
# ===================================================
# === LOGIN MANAGER (универсальный для двух ролей) ===
# ===================================================
@login_manager.user_loader
def load_user(user_id):
    # Попробуем сначала найти волонтёра, потом организацию
    user = Volunteer.query.get(int(user_id))
    if not user:
        user = Organisation.query.get(int(user_id))
    return user

# ===================================================
# === РЕГИСТРАЦИЯ ВОЛОНТЁРА ===
# ===================================================
@app.route("/register/volunteer", methods=["GET", "POST"])
def register_volunteer():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        age = request.form.get("age")
        skills = request.form.get("skills")
        time = request.form.get("available_time")

        if not name or not email or not password:
            flash("Имя, email и пароль обязательны!", "danger")
            return redirect(url_for("register_volunteer"))

        if Volunteer.query.filter_by(email=email).first():
            flash("Волонтёр с таким email уже существует!", "danger")
            return redirect(url_for("register_volunteer"))

        new_vol = Volunteer(name=name, email=email, bio=f"Возраст: {age}, Навыки: {skills}, Время: {time}")
        new_vol.set_password(password)
        db.session.add(new_vol)
        db.session.commit()

        login_user(new_vol)
        flash("Регистрация волонтёра успешна!", "success")
        # ✅ вот здесь исправлено
        return redirect(url_for("volunteer_profile", volunteer_id=new_vol.id))

    return render_template("register_volunteer.html")

# ===================================================
# === РЕГИСТРАЦИЯ ОРГАНИЗАЦИИ ===
# ===================================================
@app.route("/register/organisation", methods=["GET", "POST"])
def register_organisation():
    if request.method == "POST":
        org_name = request.form.get("org_name")
        contact_email = request.form.get("email")
        position = request.form.get("position")
        password = request.form.get("password")
        description = request.form.get("description")

        if not org_name or not contact_email or not password:
            flash("Название, email и пароль обязательны!", "danger")
            return redirect(url_for("register_organisation"))

        if Organisation.query.filter_by(email=contact_email).first():
            flash("Организация с таким email уже существует!", "danger")
            return redirect(url_for("register_organisation"))

        new_org = Organisation(name=org_name, email=contact_email, description=description)
        new_org.set_password(password)
        db.session.add(new_org)
        db.session.commit()

        login_user(new_org)
        flash("Организация успешно зарегистрирована!", "success")
        return redirect(url_for("organisation_profile", organisation_id=new_org.id))

    return render_template("register_organisation.html")

# ===================================================
# === УНИВЕРСАЛЬНЫЙ ЛОГИН (для волонтёров и организаций) ===
# ===================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role')  # volunteer или organisation
        email = request.form.get('email')
        password = request.form.get('password')

        user = None

        if role == 'volunteer':
            user = Volunteer.query.filter_by(email=email).first()
        elif role == 'organisation':
            user = Organisation.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash(f"Добро пожаловать, {user.name}!", "success")
            if role == 'volunteer':
                return redirect(url_for('profile', user_id=user.id))
            else:
                return redirect(url_for('index'))
        else:
            flash("Неверный email, пароль или роль!", "danger")

    return render_template('login.html')
@app.route("/profile/volunteer/<int:volunteer_id>")
@login_required
def volunteer_profile(volunteer_id):
    volunteer = Volunteer.query.get_or_404(volunteer_id)
    return render_template("profile_volunteer.html", volunteer=volunteer)


@app.route("/profile/organisation/<int:organisation_id>")
@login_required
def organisation_profile(organisation_id):
    organisation = Organisation.query.get_or_404(organisation_id)
    return render_template("profile_organisation.html", organisation=organisation)

# ===================================================
# === Выход ===
# ===================================================
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "info")
    return redirect(url_for('login'))

# === Запуск приложения ===
if __name__ == "__main__":
    app.run(debug=True)
