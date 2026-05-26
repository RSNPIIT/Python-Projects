from extensions import db
from flask_login import UserMixin

class Person(db.Model):
    __tablename__ = 'people'
    pid = db.Column(db.Integer , primary_key = True)
    name = db.Column(db.Text , nullable = False)
    age = db.Column(db.Integer)
    job = db.Column(db.Text)

    def __repr__(self):
        return f'Person with name {self.name} and age {self.age}'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    uid = db.Column(
        db.Integer,
        primary_key=True
    )
    username = db.Column(
        db.Text,
        unique=True,
        nullable=False
    )
    password = db.Column(
        db.Text,
        nullable=False
    )
    is_admin = db.Column(
        db.Boolean,
        default=False
    )