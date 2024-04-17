# Implementing section pages

import os
from flask import (
    Blueprint, redirect, render_template, request, session, url_for, flash
)
from werkzeug.utils import secure_filename
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)
from pustakalaya.extensions import db
from pustakalaya.model import *
from pustakalaya.utils.general import *
from pustakalaya.utils.decorators import *

bp = Blueprint('section', __name__, static_folder='static', url_prefix='/section')




# create section | C in CRUD
@bp.route("/create", methods=['POST', 'GET'])
@login_required
def create_section():
    if request.method == 'POST':
        section_name = request.form.get('section_name')
        section_description = request.form.get('description')
        new_section = Section(name=section_name, description=section_description)
        # adding all the book_id into a list
        books_to_add = [] # a list of book_id
        form_dict = request.form.to_dict()
        for key in form_dict:
            if key[0:4] == 'book':
                books_to_add.append(int(form_dict[key]))
        if books_to_add:
            for book_id in books_to_add:
                book_to_add = db.session.get(Book, book_id)
                new_section.books.append(book_to_add)
        db.session.add(new_section)
        try:
            db.session.commit()
        except Exception as e:
            return e
        return redirect(f"/section/{new_section.id}")
    return render_template('section/create_section.html', book_list=get_top_n(Book, 20))


# page for sections | R in CRUD
@bp.route('/<int:section_id>')
def section_page(**kwargs):
    section_id = kwargs.get('section_id')
    section = db.session.get(Section, section_id)
    if not section:
        return abort(404)
    section_books = section.books
    books = [result for result in section_books][:5]
    template_data = dict(
        title = f"Section {section.name}",
        books = books,
        music_collection = 'Section',
        main_category='section',
        section = section
    )
    return render_template('section/real_section_overview_page.html', **template_data)

@bp.route('/<type>')
def setions_view(**kwargs):
    if type == 'all':
        sections = db.paginate(db.select(Section), max_per_page=10)
        template_data = dict(
            title = 'All Sections',
            pagination = sections
        )
        return render_template('section/all_sections_paginated.html', **template_data)
    elif type == 'overview':
        template_data = dict(
            title = 'All Sections',
            sections = db.paginate(db.select(Section)).limit(10)
        )
        return render_template('section/all_sections_paginated.html', **template_data)



# to modify any section's data | U & D in CRUD
@bp.route('/modify/<action>', methods=['GET', 'POST'])
def modify_section(action):
    section_id = request.form.get('section_id')
    section_id = request.args.get('section_id', section_id)
    section = db.session.get(Section, section_id)
    if section and (action == 'append_book'):
        book_id = request.form.get('book_id')
        book = db.session.get(Book, book_id)
        if book in section.books:
            return redirect(request.referrer)
        section.books.append(book)
    elif section and (action == 'remove_book'):
        book_id = request.form.get('book_id')
        book = db.session.get(Book, book_id)
        section.books.remove(book)
        db.session.commit()
    elif section and (action == 'rename'):
        new_name = request.form.get('name')
        new_description = request.form.get('description')
        section.name = new_name
        section.description = new_description
    elif section and (action == 'delete'):
        db.session.delete(section)
        db.session.commit()
        return redirect(url_for('general.home'))
    else:
        return redirect(request.referrer)
    try:
        db.session.commit()
    except:
        abort(501)
    return redirect(request.referrer)

