from flask import Blueprint, request, jsonify
from pustakalaya.extensions import api
from pustakalaya.extensions import db
from pustakalaya.model import *
from flask_restful import Resource, reqparse, marshal_with, marshal
from flask_login import current_user, login_required
from .resource_fields import *
bp = Blueprint('general_api', __name__)


class BookApi(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('user_name')
        self.parser.add_argument('first_name')
        self.parser.add_argument('last_name')
        self.parser.add_argument('password')
        self.parser.add_argument('role')
    @marshal_with(book_resource_fields)
    def get(self, book_id):     # get info about a book
        book = db.session.get(Book, book_id)
        return book
api.add_resource(BookApi, '/api/book/<int:book_id>')

class SectionApi(Resource):
    def __init__(self):
        super().__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('section_name')
    def get(self, section_id):
        playlist = db.session.get(Section, section_id)
        return marshal(playlist, section_resource_fields)
    
api.add_resource(SectionApi, '/api/section/<int:section_id>')
