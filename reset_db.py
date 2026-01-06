from app import create_app, db
from app.models import Book, Loan, Admin

DELETE_ADMINS = False

def main():
    app = create_app()
    with app.app_context():
        Loan.query.delete()
        Book.query.delete()
        
        if DELETE_ADMINS:
            Admin.query.delete()

        db.session.commit()

if __name__ == "__main__":
    main()