from flask_login import UserMixin
from . import db


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    link = db.Column(db.String(120), nullable=False)
    upvotes = db.Column(db.Integer, default=0)
    def __repr__(self):
        return '<User %r>' % self.username

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100), unique=True)

class Upvote(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	id_post = db.Column(db.Integer, nullable=False)
	upvoter = db.Column(db.String(100), nullable=False)

class Follow(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	followed = db.Column(db.Integer, nullable=False)
	follower = db.Column(db.String(100), nullable=False)
