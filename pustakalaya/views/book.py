# Implementing book display pages
import os


from flask import (
    Blueprint, redirect, render_template, request, session, url_for, flash, send_from_directory
)
from datetime import datetime
from pustakalaya.extensions import db
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)
from pustakalaya.model import *
from pustakalaya.utils.general import *
from pustakalaya.utils.variables import *
from pustakalaya.utils.decorators import *

bp = Blueprint('book', __name__, url_prefix='/book')


@bp.route('/all')
@login_required
def home():
    all_books = db.session.execute(db.select(Book)).scalars()
    page = db.paginate(db.select(Book), max_per_page=10)

    template_data = dict(
        title = 'All Books in Pustakalaya',
        pagination = page
    )
    # if the user is librarian give them the list of sections to assign books to them
    if current_user.role == 'librarian':
        template_data['sections'] = scalars_to_list(db.session.scalars(db.select(Section)))
    return render_template('book/all_books_paginated.html', **template_data)


@bp.route('/my_library')
@login_required
def my_library():
    return render_template('book/my_library.html')

@bp.route('/<int:book_id>')
@login_required
def book_page(**kwargs):
    book_id = kwargs.get('book_id')
    template_data = dict(
        book = db.session.get(Book, book_id)
    )
    return render_template('book/real_book_page.html', **template_data)




@bp.route('/all/<category>/<int:category_id>')
@login_required
def book_category_all(**kwargs):
    sections = scalars_to_list(db.session.scalars(db.select(Section)))
    category = kwargs.get('category')
    category_id = kwargs.get('category_id')
    if category == 'author':
        category_object = db.session.get(Author, category_id)
    elif category == 'section':
        category_object = db.session.get(Section, category_id)

    if category_object:
        books = category_object.books
    else:
        return abort(404)
    template_data = dict(
        books = books
    )
    if current_user.role == 'librarian':
        template_data['sections'] = sections
    return render_template('book/all_books_page.html', **template_data)


# show overview of a category
@bp.route('/<category>/<category_id>')
@login_required
def overview_of_category(**kwargs):
    category = kwargs.get('category')
    category_id = kwargs.get('category_id')
    if category == 'author':
        category_object = db.session.get(Author, category_id)
    elif category == 'section':
        category_object = db.session.get(Section, category_id)

    if category_object:
        books = category_object.books[:10]
    else:
        return abort(404)
    template_data = dict(
        books=books,
        main_category = category
        )
    return render_template('music/real_book_overview_page.html', **template_data)





@bp.route('/serve/<item>/<int:book_id>')
@login_required
def server(item, book_id):
    book = db.session.get(Book, book_id)
    if not book:
        return abort(404)
    abs_music_dir = os.path.join(os.getcwd(), current_app.config['UPLOAD_FOLDER'])
    if item == 'pdf':
        return send_from_directory(abs_music_dir, book.file_name)
    elif item == 'cover_image':
        return send_from_directory(abs_music_dir, book.cover_image)

