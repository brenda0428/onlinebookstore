# database tables

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin 
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


# user table for login
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


# book table - stores all books in inventory
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)
    category = db.Column(db.String(100))
    image_url = db.Column(db.String(500), default='pics/default-book.jpg')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Book {self.title}>'


# sale table - records each sale transaction
class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    sale_date = db.Column(db.DateTime, default=datetime.utcnow)

    book = db.relationship('Book', backref=db.backref('sales', lazy=True))

    def __repr__(self):
        return f'<Sale {self.id} - Book ID {self.book_id}>'
