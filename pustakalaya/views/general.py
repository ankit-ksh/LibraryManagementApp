# Implementing user pages

from flask import (
    Blueprint, redirect, render_template, request, session, url_for, flash, send_from_directory
)
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
bp = Blueprint('general', __name__)


@bp.route('/home')
@login_required
def home():
    return redirect('/book/all')



@bp.route('/library')
@login_required
def library():
    my_library = db.paginate(db.select(BookIssueRequest).where(BookIssueRequest.status == 'issued' and BookIssueRequest.user_id==current_user.id))
    template_data = dict(
        title = 'My Library',
        pagination = my_library
    )
    return render_template('book/all_books_paginated.html', **template_data)

@bp.route('/profile')
@login_required
def profile():
    return render_template('general/profile.html')

@bp.route('/notifications')
@login_required
def notifications():
    user_id = request.args.get('user_id')
    return render_template('general/notifications.html')


@bp.route('/preferences')
@login_required
def preferences():
    return render_template('general/preferences.html')



@bp.route('/search')
@login_required
def search():
    q = request.args.get('q')
    filtered_by = None
    books = None
    filter_by = request.args.get('filter_by')
    if filter_by == 'author':
        author_id = request.args.get('author_id')
        author = db.session.get(Author, author_id)
        if db.session.get(Author, author_id):
            filtered_by = f"Author : {db.session.get(Author, author_id).name}"
            books = [result for result in db.session.execute(db.select(Book).where(db.and_(Book.name.ilike(f"%{q}%")), Book.authors.any(Author.id == author.id))).scalars()]
            books = [book for book in books]
    else:
        books = [result for result in db.session.execute(db.select(Book).where(Book.name.ilike(f"%{q}%"))).scalars()]
    
    # provide authors to select from
    query_result = db.session.execute(db.select(Author)).scalars()
    all_authors = [author for author in query_result]

    template_data = dict(
        books=books,
        authors = all_authors,
        query_term = q,
        filtered_by = filtered_by
    )
    return render_template('general/search_results.html', **template_data)


@bp.route('/exp/<int:exp_id>', methods=['GET', 'POST'])
def experiments(**kwargs):
    exp_id = kwargs.get('exp_id')
    template_data = dict(
        exp_id = exp_id
    )
    import os
    abs_file_path = os.path.join(os.getcwd(), f'pustakalaya/templates/experiment/exp_{exp_id}.html')
    file_path = f'pustakalaya/templates/experiment/exp_{exp_id}.html'
    if not os.path.exists(abs_file_path):
        new_exp_file = open(abs_file_path, 'w')
        new_exp_file.write(experiment_boilerplate_text)
        new_exp_file.close()
    
        return render_template(f'experiment/exp_{exp_id}.html', **template_data)
    else:
        return render_template(f'experiment/exp_{exp_id}.html', **template_data)