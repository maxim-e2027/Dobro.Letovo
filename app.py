import os
from models import db, Event, Comment, Request, Volunteer, init_database_with_sqlite
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

@login_manager.user_loader
def load_user(user_id):
    return Volunteer.query.get(int(user_id))

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
# === Регистрация ===
# ===================================================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        bio = request.form.get('bio', '')

        if not name or not email or not password:
            flash("Имя, email и пароль обязательны!", "danger")
            return redirect(url_for('register'))

        if Volunteer.query.filter_by(email=email).first():
            flash("Пользователь с таким email уже существует!", "danger")
            return redirect(url_for('register'))

        new_user = Volunteer(name=name, email=email, bio=bio)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for('profile', user_id=new_user.id))

    return render_template('login.html')

# ===================================================
# === Логин ===
# ===================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = Volunteer.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash(f"Добро пожаловать, {user.name}!", "success")
            return redirect(url_for('profile', user_id=user.id))
        else:
            flash("Неверный email или пароль!", "danger")
    return render_template('login.html')

# ===================================================
# === Профиль ===
# ===================================================
@app.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    user = Volunteer.query.get_or_404(user_id)
    return render_template('profile.html', user=user)

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