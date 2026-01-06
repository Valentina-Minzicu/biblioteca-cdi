from flask import Blueprint, render_template, redirect, request, url_for, flash, abort
from flask_login import login_user, logout_user, login_required
from .models import Admin, Book, Loan
from . import db
from sqlalchemy import or_

admin_bp = Blueprint("admin", __name__)

@admin_bp.get("/login")
def login():
    return render_template("login.html")

@admin_bp.post("/login")
def login_post():
    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""
    
    admin = Admin.query.filter_by(username=username).first()
    if not admin or not admin.check_password(password):
        flash("Date de autentificare fresite", "error")
        return redirect(url_for("admin.login"))
    
    login_user(admin)
    return redirect(url_for("admin.dashboard"))

@admin_bp.get("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("public.index"))

@admin_bp.get("/")
@login_required
def dashboard():
    q_books = (request.args.get("q_books") or "").strip()
    q_loans = (request.args.get("q_loan") or "").strip()
    
    books_q = Book.query
    if q_books:
        like = f"%{q_books}%"
        books_q = books_q.filter(or_(
            Book.title.ilike(like),
            Book.author.ilike(like)
        ))
    books = books_q.order_by(Book.id.asc()).all()
    
    loans_q = books_q = Loan.query
    if q_loans:
        like = f"%{q_loans}%"
        loans_q = loans_q.filter(or_(
            Loan.student_name.ilike(like),
            Loan.student_class.ilike(like)
        ))
    loans = loans_q.order_by(Loan.reserved_at.desc()).all()
    
    return render_template(
        "admin_dashboard.html",
        books=books,
        loans=loans,
        q_books=q_books,
        q_loans=q_loans
    )

@admin_bp.get("/books/new")
@login_required
def book_new():
    return render_template("book_form.html", mode="new", book=None)

@admin_bp.post("/books/new")
@login_required
def book_new_post():
    title = (request.form.get("title") or "").strip()
    author = (request.form.get("author") or "").strip()
    total = request.form.get("total_copies", type = int)
    
    if not title or not author or total is None or total <= 0:
        flash("Completeaz corect: titlu, autor, total exemplare (>= 1).", "error")
        return redirect(url_for("admin.book_new"))

    book = Book(title=title, author=author, total_copies=total, available_copies=total)
    db.session.add(book)
    db.session.commit()
    flash("Cartea a fost adaugata", "ok")
    return redirect(url_for("admin.dashboard"))

@admin_bp.get("/books/<int:book_id>/edit")
@login_required
def book_edit(book_id: int):
    book = Book.query.get_or_404(book_id)
    return render_template("book_form.html", mode = "edit", book=book)

@admin_bp.post("/books/<int:book_id>/edit")
@login_required
def book_edit_post(book_id: int):
    book = Book.query.get_or_404(book_id)
    
    title = (request.form.get("title") or "").strip()
    author = (request.form.get("author") or "").strip()
    new_total = request.form.get("total_copies", type = int)
    
    if not title or not author or new_total is None or new_total <= 0:
        flash("Completeaz corect: titlu, autor, total exemplare (>= 1).", "error")
        return redirect(url_for("admin.book_edit", book_id = book_id))
    
    reserved_count = Loan.query.filter_by(book_id = book.id).count()
    
    if new_total < reserved_count:
        flash("Nu poti seta totalul la {new_total}. Exista deja {reserved_cpunt} reservari/impurmuturi inregistrare", "error")
        return redirect(url_for("admin.book_edit"), book_id = book_id)
    
    book.title = title
    book.author = author
    book.total_copies = new_total
    book.available_copies = new_total - reserved_count
    
    db.session.commit()
    flash("Cartea a fost modificata", "ok")
    return redirect(url_for("admin.dashboard"))

@admin_bp.post("/books/<int:book_id>/delete")
@login_required
def book_delete(book_id: int):
    book = Book.query.get_or_404(book_id)
    
    active = Loan.query.filter_by(book_id=book.id).count()
    if active > 0:
        flash("Nu poti stegre cartea: exista deja imprumuturi asociate. Stegre mai intai inregistrarile imprumuturilor", "error")
        return redirect(url_for("admin.dashboard"))
    
    db.session.delete(book)
    db.session.commit()
    flash("Cartea a fost stearsa", "ok")
    return redirect(url_for("admin.dashboard"))

@admin_bp.post("/loan/toggle-borrowed")
@login_required
def toggle_borrowed():
    loan_id = request.form.get("loan_id", type = int)
    loan = Loan.query.get_or_404(loan_id)
    loan.is_borrowed = not loan.is_borrowed
    db.session.commit()
    return redirect(url_for("admin.dashboard"))

@admin_bp.post("/loan/delete")
@login_required
def delete_loan():
    loan_id = request.form.get("loan_id", type = int)
    loan = Loan.query.get_or_404(loan_id)
    
    book = Book.query.get(loan.book_id)
    if book:
        book.available_copies += 1
    
    db.session.delete(loan)
    db.session.commit()
    return redirect(url_for("admin.dashboard"))
