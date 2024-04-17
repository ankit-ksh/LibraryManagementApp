# extension for database - ORM flask-sqlalchemy
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# extension for authentication management - flask-login
from flask_login import LoginManager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.blueprint_login_views = {
    'librarian.librarian_home': '/login/librariran',
}
login_manager.login_message = 'You Need to Log in!'


# extension for api - flask restful
from flask_restful import Api
api = Api()




# # extension flask migration for tracking changes in the database (NOT ABLE TO MAKE IT WORK)
# from flask_migrate import Migrate
# migrate = Migrate()




# import functools
# from flask import (
#     Blueprint, flash, g, redirect, render_template, request, session, url_for
# )
# from werkzeug.security import check_password_hash, generate_password_hash
