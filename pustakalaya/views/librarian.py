# Implementing user pages

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

bp = Blueprint('librarian', __name__, url_prefix='/librarian')








@bp.route('/dashboard')
@librarian_required
def dashboard():
    # Data related to the platform
    tables = [User, Book, Section, BookIssueRequest, Language, Author]
    pustkalaya_data = {}
    for table in tables:
        pustkalaya_data[table.__tablename__] = dict(
            total_in_number = len([item for item in db.session.execute(db.select(table)).scalars()])
        )
    
    # books issue data
    requests = db.session.scalars(db.select(BookIssueRequest))
    all_requests_data = dict(
        issued = 0,
        pending = 0,
        revoked = 0,
        rejected = 0
    )
    for request in requests:
        if request.status == 'issued':
            all_requests_data['issued'] += 1
        elif request.status == 'pending':
            all_requests_data['pending'] += 1
        elif request.status == 'revoked':
            all_requests_data['revoked'] += 1
        elif request.status == 'rejected':
            all_requests_data['rejected'] += 1

    template_data = dict(
        pustakalaya_data=pustkalaya_data,
        all_requests_data = all_requests_data
    )
    # Data related to the platform specific to the Librarian

    return render_template('librarian/dashboard.html', **template_data)

@bp.route('/request/<action>')
@librarian_required
def take_action_on_book_request(**kwargs):
    issue_request_id = request.args.get('issue_request_id')
    issue_request = db.session.get(BookIssueRequest, issue_request_id)
    if issue_request:
        issue_request = db.session.scalar(db.select(BookIssueRequest).where(BookIssueRequest.request_id == issue_request_id))
    else:
        return abort(404)
    if kwargs.get('action') == 'approve':
        issue_request.status = 'issued'
        issue_request.issue_time = datetime.now()
    elif kwargs.get('action') == 'revoke_access':
        issue_request.status = 'revoked'
        issue_request.return_time = datetime.now()
    elif kwargs.get('action') == 'reject':
        issue_request.status = 'rejected'
        issue_request.rejection_time = datetime.now()
    db.session.commit()
    return redirect(request.referrer)


########################## Upload and edit book ################################



@bp.route('/book/upload', methods=['GET', 'POST'])
@librarian_required
def upload_book():
    if request.method == 'POST':
        book_name = request.form.get('book_name')
        isbn = request.form.get('isbn')
        publisher = request.form.get('publisher')
        number_of_pages = request.form.get('number_of_pages')
        section_id = request.form.get('section_id')
        publish_year = request.form.get('publish_year')
        upload_date = datetime.now()
        author_id = request.form.get('author_id')
        librarian_id = request.form.get('librarian_id')
        description = request.form.get('description')

        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

            # create folder if it doesn't exist
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
            # Save file to the file system
            file.save(filepath)

            author = db.session.get(Author, author_id)

            # Save file information to the database
            new_book = Book(name=book_name, description=description, isbn=isbn, publisher=publisher, publish_year=publish_year, upload_date=upload_date, number_of_pages=number_of_pages, section_id=section_id, file_name=filename, file_path=filepath)
            new_book.authors.append(author)
            db.session.add(new_book)
            db.session.commit()
            return redirect(url_for('book.book_page', book_id=new_book.id))
        else:
            flash('Failed', 'error')
            return 'failed'
    # provide authors to select from
    query_result = db.session.execute(db.select(Author)).scalars()
    template_data = dict(
        authors = [author for author in db.session.scalars(db.select(Author))],
        sections = [section for section in db.session.scalars(db.select(Section))]
    )
    return render_template('librarian/upload_book.html', **template_data)



@bp.route('/book/<action>/<int:book_id>', methods=['GET', 'POST'])
@librarian_required
def modify_book(**kwargs):
    book = db.session.get(Book, kwargs.get('book_id'))
    if kwargs.get('action') == 'edit':
        if request.method == 'GET':
            book_id = kwargs.get('book_id')
            if book_id:
                # provide author to select from
                template_data = dict(
                    book = db.session.get(Book, book_id),
                    all_authors = [author for author in db.session.scalars(db.select(Author))],
                    book_authors = db.session.get(Book, book_id).authors
                )
                return render_template('librarian/edit_book.html', **template_data)
            else:
                return abort(401)
        # post method edit action
        if request.method == 'POST':
            book_id = kwargs.get('book_id')
            book_to_edit = db.session.get(Book, book_id)
            # return request.form

            # handle add author and remove author separately
            (add_author_id, remove_author_id) = (request.form.get('add_author_id'), request.form.get('remove_author_id'))
            (add_author, remove_author) = (db.session.get(Author, add_author_id), db.session.get(Author, remove_author_id))
            if add_author:
                book_to_edit.authors.append(add_author)
            if remove_author:
                book_to_edit.authors.remove(remove_author)
            for key, value in request.form.items():
                if (key not in ['file', 'add_author_id', 'remove_author_id']) and (value not in ['None', '', None]):
                    print(key, value)
                    setattr(book_to_edit, key, value)
            file = request.files.get('file', None)
            # for handling the actual file
            if file:
                filename = secure_filename(file.filename)
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

                # create folder if it doesn't exist
                os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                # Save file to the file system
                file.save(filepath)

                setattr(book_to_edit, 'file_name', filename)
                setattr(book_to_edit, 'file_path', filepath)
            # iterate through the post data to update book_to_update
            try:
                db.session.add(book_to_edit)
                db.session.commit()
                return redirect(url_for('book.book_page', book_id=book.id))
            except:
                pass
    if kwargs.get('action') == 'delete':
        if not book:
            return redirect(request.referrer)
        book_to_delete = book
        if book_to_delete:
            try:
                db.session.delete(book_to_delete)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
        else:
            flash("Not authenticated")
        return redirect('/book/all')
    else:
        return redirect(request.referrer)




    
# All requests page for the librarian
@bp.route('/request/all/<type>')
@librarian_required
def librarian_all_requests(**kwargs):
    type = kwargs.get('type')
    template_data = {}
    if type == 'pending':
        page = db.paginate(db.select(BookIssueRequest).where(BookIssueRequest.status == 'pending'))
        template_data['subcategory'] = 'Pending'
    elif type == 'issued':
        template_data['subcategory'] = 'Issued'
        page = db.paginate(db.select(BookIssueRequest).where(BookIssueRequest.status == 'issued'))
    elif type == 'revoked':
        template_data['subcategory'] = 'Revoked'
        page = db.paginate(db.select(BookIssueRequest).where(BookIssueRequest.status == 'revoked'))
    elif type == 'rejected':
        template_data['subcategory'] = 'Rejected'
        page = db.paginate(db.select(BookIssueRequest).where(BookIssueRequest.status == 'rejected'))
    template_data['pagination'] = page

    template_data['content_listing_template'] = 'request/real_request_listing.html'
    template_data['category'] = 'request'
    return render_template('includes/content_management/all_content_paginated.html', **template_data)


@bp.route('/book_requests')
def book_requests():
    recent_pending_requests = db.session.scalars(db.select(BookIssueRequest).where(BookIssueRequest.status == 'pending').limit(5).order_by(BookIssueRequest.request_time.desc()))
    recent_rejected_requests = db.session.scalars(db.select(BookIssueRequest).where(BookIssueRequest.status == 'rejected').limit(5).order_by(BookIssueRequest.request_time.desc()))
    recent_revoked_accesses = db.session.scalars(db.select(BookIssueRequest).where(BookIssueRequest.status == 'revoked').limit(5).order_by(BookIssueRequest.request_time.desc()))
    recent_issued_requests = db.session.scalars(db.select(BookIssueRequest).where(BookIssueRequest.status == 'issued').limit(5).order_by(BookIssueRequest.request_time.desc()))
    template_data = dict(
        recent_pending_requests = scalars_to_list(recent_pending_requests),
        recent_rejected_requests = scalars_to_list(recent_rejected_requests),
        recent_revoked_accesses = scalars_to_list(recent_revoked_accesses),
        recent_issued_requests = scalars_to_list(recent_issued_requests),
        book_requests_link = 'active'
    )
    print(template_data['recent_revoked_accesses'], template_data['recent_issued_requests'])
    return render_template('request/all_requests.html', **template_data)




@bp.route('/author/<action>')
@librarian_required
def author_management(action):
    authors = scalars_to_list(author for author in db.session.scalars(db.select(Author)))
    if action == 'overview':
        template_data = dict(
            content_listing_template = 'content_listing_template/author/author_listing.html',
            links = {
                'Add New Author': '/librarian/author_management/add_author',
                'All authors': 'librarian/author_management/view_all'
            },
            authors = authors[:10]
        )
        return render_template('librarian/author_management.html', **template_data)
        

@bp.route('/book_management/<action>')
@librarian_required
def book_management(action):
    books = scalars_to_list(book for book in db.session.scalars(db.select(Book)))
    if action == 'overview':
        template_data = dict(
            content_listing_template = 'content_listing_template/author/author_listing.html',
            links = {
                'Add New Book': '/librarian/upload_book',
                'All Books': 'librarian/book/view_all'
            },
            books = books[:10]
        )
        return render_template('librarian/book_management.html', **template_data)
