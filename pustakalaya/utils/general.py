import math
from pustakalaya.extensions import db
from pustakalaya.model import *
from pydub.utils import mediainfo
from flask_login import current_user


# ----------------------------- For Pustakalaya app ---------------------------------------------

def scalars_to_list(scalar_result):
    return [result for result in scalar_result]

def get_books_display_data(**kwargs):
    if kwargs.get('type') == 'all':
        books = db.session.execute(db.select(Book)).scalars()
        books_list = [book for book in books]
    all_books_data = []
    for book in books_list:
        single_book_data = dict(
            book = book,
            access_level = current_user.role
            )
        all_books_data.append(single_book_data)
    return all_books_data
        

def get_top_n(table, n):
    query_result = db.session.execute(db.select(table).limit(n)).scalars()
    list = [entry for entry in query_result]
    return list