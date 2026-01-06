from app import create_app, db
from app.models import Admin, Book

app = create_app()

with app.app_context():
    if not Admin.query.filter_by(username="admin").first():
        a = Admin(username="admin")
        a.set_password("Admin123!")
        db.session.add(a)
        
    if Book.query.count() == 0:
        db.session.add(Book(title="Ion", author = "Liviu Rebreanu", total_copies = 3, available_copies = 3))
        db.session.add(Book(title="Morometii", author = "Marin Preda", total_copies = 2, available_copies = 2))
        db.session.add(Book(title="Enigma Otiliei", author = "George Calinescu", total_copies = 1, available_copies = 1))
    
    db.session.commit()
    print("Seed done.")