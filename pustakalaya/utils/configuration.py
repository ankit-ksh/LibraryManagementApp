from flask_login import current_user, login_required
from .general import *
def logged_in_vars():
    user_role = current_user.role
    layout_paths = {
        'user' : 'layouts/user_layout.html',
        'librarian' : 'layouts/librarian_layout.html',
    }
    book_listing_paths = {
        'book' : 'book/general_book_listing.html'
    }
    return dict(
        book_listing_template = book_listing_paths.get('book'),
        layout_path = layout_paths.get(user_role),
        hello = 'hello'
    )

def logged_out_vars():
    return dict(
        layout  = 'layouts/logged_out_layout.html',
    )


# This function is passed to the context processor which runs this function every time a template is rendered and 
# accordingly passes the values defined here to the template
# Note : If I just use the @login_required decorator, it won't work since in that case no response is returned by the function
# if the user is not authenticated
def inject_user_based_data():
    if current_user.is_authenticated:
        context_dict =  dict(
            appropriate_layout = logged_in_vars().get('layout_path'),
            book_listing_template = logged_in_vars().get('book_listing_template'),
        )
    else:
        context_dict = dict(
            appropriate_layout = logged_out_vars().get('layout'),
            book_listing_template = 'books/general_book_listing.html'
        )
    return context_dict


