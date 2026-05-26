from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(80), unique=True, nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    password   = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bio        = db.Column(db.String(300), default="")
    location   = db.Column(db.String(100), default="")

    reviews    = db.relationship('Review', backref='user', lazy=True, cascade='all, delete-orphan')
    diary      = db.relationship('DiaryEntry', backref='user', lazy=True, cascade='all, delete-orphan')
    watchlist  = db.relationship('Watchlist', backref='user', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'

class Review(db.Model):
    __tablename__ = 'reviews'
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    movie_id   = db.Column(db.Integer, nullable=False)
    movie_title= db.Column(db.String(200), nullable=False)
    movie_poster=db.Column(db.String(300), default="")
    rating     = db.Column(db.Float, nullable=False)
    review_text= db.Column(db.Text, default="")
    watch_type = db.Column(db.String(20), default="first")  # first or rewatch
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    likes      = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Review {self.movie_title} by {self.user_id}>'

class DiaryEntry(db.Model):
    __tablename__ = 'diary'
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    movie_id    = db.Column(db.Integer, nullable=False)
    movie_title = db.Column(db.String(200), nullable=False)
    movie_poster= db.Column(db.String(300), default="")
    movie_year  = db.Column(db.String(10), default="")
    rating      = db.Column(db.Float, default=0)
    watched_at  = db.Column(db.DateTime, default=datetime.utcnow)
    notes       = db.Column(db.Text, default="")

class Watchlist(db.Model):
    __tablename__ = 'watchlist'
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    movie_id    = db.Column(db.Integer, nullable=False)
    movie_title = db.Column(db.String(200), nullable=False)
    movie_poster= db.Column(db.String(300), default="")
    movie_year  = db.Column(db.String(10), default="")
    added_at    = db.Column(db.DateTime, default=datetime.utcnow)
