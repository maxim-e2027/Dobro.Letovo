from app import app, db
from models import Event

with app.app_context():
    # Очистим таблицу (по желанию)
    db.session.query(Event).delete()

    events = [
        Event(title="Эко-субботник", category="Экология", description="Собираем мусор в парке"),
        Event(title="Помощь в приюте", category="Животные", description="Уборка и кормление собак"),
        Event(title="Уроки для школьников", category="Образование", description="Помощь в обучении детей"),
        Event(title="Сбор вещей для нуждающихся", category="Благотворительность", description="Принимаем одежду и игрушки"),
        Event(title="Волонтёры на концерт", category="Культура", description="Организация мероприятия"),
    ]

    db.session.add_all(events)
    db.session.commit()
    print("База данных заполнена тестовыми ивентами!")