from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db, login_manager

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable = False)
    author = db.Column(db.String(200), nullable = False)
    total_copies = db.Column(db.Integer, nullable = False, default = 1)
    available_copies = db.Column(db.Integer, nullable = False, default = 1)
    
    loans = db.relationship("Loan", backref = "book", lazy = True)

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable = False)
    
    student_name = db.Column(db.String(200), nullable = False)
    student_class = db.Column(db.String(50), nullable = False)
    
    reserved_at = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    is_borrowed = db.Column(db.Boolean, nullable = False, default = False)
    
class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(200), unique = True, nullable = False)
    password_hash = db.Column(db.String(255), nullable = False)
    
    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
    
    @login_manager.user_loader
    def load_user(admin_id):
        return Admin.query.get(int(admin_id))