from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class Volunteer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    bio = db.Column(db.Text)
    avatar = db.Column(db.String(300))

    requests = db.relationship("Request", back_populates="volunteer", cascade="all, delete-orphan")
    comments = db.relationship("Comment", back_populates="volunteer", cascade="all, delete-orphan")


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))

    requests = db.relationship("Request", back_populates="event", cascade="all, delete-orphan")
    comments = db.relationship("Comment", back_populates="event", cascade="all, delete-orphan")

class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    volunteer_id = db.Column(db.Integer, db.ForeignKey("volunteer.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False)
    status = db.Column(db.String(50), default="pending")

    volunteer = db.relationship("Volunteer", back_populates="requests")
    event = db.relationship("Event", back_populates="requests")


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    volunteer_id = db.Column(db.Integer, db.ForeignKey("volunteer.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False)

    volunteer = db.relationship("Volunteer", back_populates="comments")
    event = db.relationship("Event", back_populates="comments")