from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import db
from .models import Book, Loan
from sqlalchemy import or_

public_bp = Blueprint("public", __name__)

@public_bp.get("/")
def index():
    q = (request.args.get("q") or "").strip()
    
    query = Book.query
    if q:
        like = f"%{q}%"
        query = query.filter(or_(
            Book.title.ilike(like),
            Book.author.ilike(like)
        ))
    
    books = Book.query.order_by(Book.author.asc()).all()
    return render_template("index.html", books=books)

@public_bp.post("/reserve")
def reserve():
    book_id = request.form.get("book_id", type=int)
    name = (request.form.get("student_name") or "").strip()
    sclass = (request.form.get("student_class") or "").strip()
    
    if not name or not sclass:
        flash("Completeaza numele si clasa","error")
        return redirect(url_for("public.index"))
    
    book = Book.query.get_or_404(book_id)
    
    if book.available_copies <= 0:
        flash("Nu mai exista exemplare disponibile pentru aceasata carte", "error")
        return redirect(url_for("public.index"))
    
    book.available_copies -= 1
    loan = Loan(book_id = book.id, student_name = name, student_class = sclass)
    db.session.add(loan)
    db.session.commit()
    
    flash("Rezervare inregistrata. Te rugam sa ridici cartea in cel mult 7 zile.", "ok")
    return redirect(url_for("public.index"))