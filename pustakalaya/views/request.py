# Implementing request display pages

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

bp = Blueprint('request', __name__, url_prefix='/request')


@bp.route('/my_requests')
def my_requests():
    recent_pending_requests = db.session.scalars(db.select(BookIssueRequest).where(BookIssueRequest.status == 'pending' and BookIssueRequest.user_id == current_user.id).limit(5).order_by(BookIssueRequest.request_time.desc()))
    recent_rejected_requests = db.session.scalars(db.select(BookIssueRequest).where(BookIssueRequest.status == 'rejected' and BookIssueRequest.user_id == current_user.id).limit(5).order_by(BookIssueRequest.request_time.desc()))
    recent_revoked_accesses = db.session.scalars(db.select(BookIssueRequest).where(BookIssueRequest.status == 'revoked' and BookIssueRequest.user_id == current_user.id).limit(5).order_by(BookIssueRequest.request_time.desc()))
    template_data = dict(
        recent_pending_requests = scalars_to_list(recent_pending_requests),
        recent_rejected_requests = scalars_to_list(recent_rejected_requests),
        recent_revoked_accesses = scalars_to_list(recent_revoked_accesses)
    )
    return render_template('request/all_requests.html', **template_data)


# All requests page for the general user
@bp.route('/all/<type>')
def user_all_requests(**kwargs):
    type = kwargs.get('type')
    template_data = {}
    if type == 'pending':
        page = db.paginate(db.select(BookIssueRequest).where(BookIssueRequest.status == 'pending' and BookIssueRequest.user_id == current_user.id))
        template_data['subcategory'] = 'Pending'
    elif type == 'issued':
        template_data['subcategory'] = 'Issued'
        page = db.paginate(db.select(BookIssueRequest).where(BookIssueRequest.status == 'issued' and BookIssueRequest.user_id == current_user.id))
    elif type == 'revoked':
        template_data['subcategory'] = 'Revoked'
        page = db.paginate(db.select(BookIssueRequest).where(BookIssueRequest.status == 'revoked' and BookIssueRequest.user_id == current_user.id))
    elif type == 'rejected':
        template_data['subcategory'] = 'Rejected'
        page = db.paginate(db.select(BookIssueRequest).where(BookIssueRequest.status == 'rejected' and BookIssueRequest.user_id == current_user.id))
    template_data['pagination'] = page

    template_data['content_listing_template'] = 'request/real_request_listing.html'
    template_data['category'] = 'request'
    return render_template('includes/content_management/all_content_paginated.html', **template_data)







# User making a request for a book
@bp.route('/<action>/<int:book_id>', methods=['GET', 'POST'])
def request_book(**kwargs):
    book_id = kwargs.get('book_id')
    book = db.session.get(Book, book_id)
    if (not book) or (not kwargs.get('action')):
        return abort(400)
    if kwargs.get('action') == 'make_request':
        if (book not in current_user.pending_issue_books) or (book not in current_user.currently_issued_books):
            if (len(current_user.currently_issued_books) >=5) or (len(current_user.pending_issue_requests) >= 5):
                flash("Max Limit Reached", "error")
                return redirect(request.referrer)
            new_request = BookIssueRequest(
                user_id = current_user.id,
                book_id = book_id,
                request_time = datetime.now(),
                requested_days = request.args.get('days_to_keep'),
                status = 'pending'
            )
            db.session.add(new_request)
    elif kwargs.get('action') == 'cancel_request':
        flash("Request Cancelled", "success")
        that_request = db.session.scalar(db.select(BookIssueRequest).where(BookIssueRequest.status == 'pending' and BookIssueRequest.user_id==current_user.id and BookIssueRequest.book_id==book_id))
        db.session.delete(that_request)
    elif kwargs.get('action') == 'return_book':
        if request.method == 'POST':
            rating = request.form.get('rating')
            comment = request.form.get('comment')
            if rating and comment and book:
                that_request = db.session.scalar(db.select(BookIssueRequest).where(BookIssueRequest.status == 'issued' and BookIssueRequest.user_id==current_user.id and BookIssueRequest.book_id==book_id))
                that_request.status = 'revoked'
                that_request.return_time = datetime.now()
                flash("Book Returned", "success")

            else:
                return abort(400)
    db.session.commit()
    return redirect(request.referrer)