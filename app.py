import os
from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Event, Comment, Request, Volunteer
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dobro.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# обязательно для сессий и login_user
app.secret_key = "super-secret-key-123"

migrate = Migrate(app, db)
# Привязываем db к app
db.init_app(app)

with app.app_context():
    db.create_all()

with app.app_context():
    # создаём тестового волонтёра, если его ещё нет
    test_volunteer = Volunteer.query.filter_by(email="test@volunteer.com").first()
    if not test_volunteer:
        test_volunteer = Volunteer(
            name="Тестовый Волонтёр",
            email="test@volunteer.com",
            bio="Это тестовый аккаунт для входа",
            password = "123",
            secret_key = "123"
        )
        db.session.add(test_volunteer)
        db.session.commit()


@app.route("/login_test", methods=["GET", "POST"])
def login_test():
    # Берём тестового волонтёра
    volunteer = Volunteer.query.filter_by(email="test@volunteer.com").first()
    if not volunteer:
        flash("Тестовый аккаунт не найден!", "danger")
        return redirect(url_for("index"))

    # логиним пользователя
    login_user(volunteer)
    flash(f"Вы вошли как {volunteer.name}", "success")

    # перенаправляем на профиль
    return redirect(url_for("profile", user_id=volunteer.id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # куда редиректить, если не авторизован

# === Главная страница ===
@app.route("/")
def index():
    return render_template("index.html")

# --- Каталог мероприятий с фильтрами ---
@app.route("/events")
def events():
    category = request.args.get("category")
    search = request.args.get("search")

    query = Event.query

    # Фильтр по категории
    if category and category != "all":
        query = query.filter(Event.category == category)

    # Поиск по названию и описанию
    if search:
        query = query.filter(
            (Event.title.ilike(f"%{search}%")) |
            (Event.description.ilike(f"%{search}%"))
        )

    events = query.all()
    categories = db.session.query(Event.category).distinct().all()

    return render_template("events.html", events=events, categories=[c[0] for c in categories])

# --- Детали события ---
@app.route("/events/<int:event_id>")
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    comments = Comment.query.filter_by(event_id=event_id).all()
    return render_template("event_detail.html", event=event, comments=comments)


# --- Присоединиться к событию ---
@app.route("/events/<int:event_id>/join", methods=["POST"])
def join_event(event_id):
    # Заглушка: берём первого волонтёра (id=1), пока нет авторизации
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
    author_id = request.form.get("volunteer_id")  # id волонтёра из формы
    content = request.form.get("content")

    if not content.strip():
        return redirect(url_for("event_detail", event_id=event_id))

    new_comment = Comment(content=content, volunteer_id=author_id, event_id=event_id)
    db.session.add(new_comment)
    db.session.commit()

    return redirect(url_for("event_detail", event_id=event_id))

# === Профиль ===
@app.route("/profile/<int:user_id>")
@login_required
def profile(user_id):
    user = Volunteer.query.get_or_404(user_id)
    return render_template("profile.html", user=user)

@app.route("/profile/<int:user_id>/edit", methods=["GET", "POST"])
def edit_profile(user_id):
    user = Volunteer.query.get_or_404(user_id)

    if request.method == "POST":
        user.name = request.form["name"]
        user.email = request.form["email"]
        user.bio = request.form["bio"]

        # загрузка аватара
        if "avatar" in request.files:
            file = request.files["avatar"]
            if file and allowed_file(file.filename):
                from werkzeug.utils import secure_filename
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(filepath)
                user.avatar = f"{UPLOAD_FOLDER}/{filename}"

        db.session.commit()
        flash("Профиль успешно обновлен!", "success")
        return redirect(url_for("profile", user_id=user.id))

    return render_template("edit_profile.html", user=user)


# === Создание события ===
@app.route("/create")
def create_event():
    return render_template("create_event.html")

@login_manager.user_loader
def load_user(user_id):
    return Volunteer.query.get(int(user_id))

# === Авторизация ===
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        user = Volunteer.query.filter_by(email=email).first()
        if user:
            login_user(user)  # авторизуем
            flash("Вы успешно вошли!", "success")
            return redirect(url_for("profile", user_id=user.id))
        else:
            flash("Пользователь не найден!", "danger")
    return render_template("login.html")

# === Выход из профиля ===
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта.", "info")
    return redirect(url_for("index"))

# === Регистрация ===
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        bio = request.form.get("bio", "")

        if not name or not email:
            flash("Имя и email обязательны!", "danger")
            return redirect(url_for("register"))

        # Проверяем, есть ли уже пользователь с таким email
        existing_user = Volunteer.query.filter_by(email=email).first()
        if existing_user:
            flash("Пользователь с таким email уже существует!", "danger")
            return redirect(url_for("register"))

        # создаём нового волонтёра
        new_volunteer = Volunteer(name=name, email=email, bio=bio)
        db.session.add(new_volunteer)
        db.session.commit()

        # автоматически логиним после регистрации
        login_user(new_volunteer)
        flash("Регистрация прошла успешно!", "success")
        return redirect(url_for("profile", user_id=new_volunteer.id))

    return render_template("register.html")

# === Запуск приложения ===
if __name__ == "__main__":
    app.run(debug=True)