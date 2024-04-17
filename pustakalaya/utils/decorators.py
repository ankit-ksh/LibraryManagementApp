from functools import wraps
from flask import abort, request, current_app, redirect
from flask_login import current_user, login_required

from pustakalaya.extensions import db
from pustakalaya.model import *


def librarian_required(f):
    @wraps(f)
    def wrapper(**kwargs):
        if (current_user.is_authenticated):
            pass
        else:
            return current_app.login_manager.unauthorized()
        if not current_user.role == 'librarian':
            return "You're not a librarian."
        return f(**kwargs)
    return wrapper



