import os
from flask import Flask, current_app
from oauthlib.oauth2 import WebApplicationClient
from flask_login import current_user
from pustakalaya.extensions import db
from pustakalaya.extensions import login_manager
from pustakalaya.extensions import api
# Following import is for getting the user object for the user loader of flask login LoginManager
from pustakalaya.model import User
# To register all api resources I need it all in this file so I need to import all the api blueprints outside the api function
# for the normal web app functionality, it works even when being inside a function, but for APIs I'll have to keep it inside
from pustakalaya.rest_api import general as general_api
from pustakalaya.views import auth, book, general, librarian, section, request


def create_app(test_config=None):
    # creating the flask app as an instance of the Flask Class
    app = Flask(__name__, instance_relative_config=True)
    app.app_context().push()
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI = "sqlite:///pustakalaya.sqlite3",
        SQLALCHEMY_TRACK_MODIFICATIONS = True, # False in production to increase performance, True in development for reloading without restarting the server
        # TEMPLATES_AUTO_RELOAD = True
        UPLOAD_FOLDER = "pustakalaya/static/pustakalaya_data/books",
		# Configuration
		GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None),
		GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None),
		GOOGLE_DISCOVERY_URL = (
			"https://accounts.google.com/.well-known/openid-configuration"
			)
    )

    # ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # initialising database, if required
    db.init_app(app)
    # from . import models
    with app.app_context():
        db.create_all()

    # OAuth 2 client setup
    client = WebApplicationClient(current_app.config.get('GOOGLE_CLIENT_ID'))


    # Intialising and configuring flask login
    login_manager.init_app(app)
    #loading the user
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
    
    # Intialising and configuring Flask Restful
    api.init_app(app)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    

    # registering the context processors
    from .utils.configuration import inject_user_based_data
    app.context_processor(inject_user_based_data)

    # registering the blueprints - for web application
    app.register_blueprint(auth.bp)
    app.register_blueprint(general.bp)
    app.register_blueprint(librarian.bp)
    app.register_blueprint(book.bp)
    app.register_blueprint(section.bp)
    app.register_blueprint(request.bp)

    # registering API blurprints
    app.register_blueprint(general_api.bp)


    return app

