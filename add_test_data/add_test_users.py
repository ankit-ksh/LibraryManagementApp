from pustakalaya import app, db  # Import Flask app and SQLAlchemy objects
from pustakalaya.model import User, Librarian  # Import User model from SQLAlchemy
from pustakalaya.extensions import db

def create_test_users():
    # Create test users
    u = User(user_name='test_u', first_name='test_user', password='password')
    l = Librarian(user_name='test_l', first_name='test_l', password='password')
    db.session.add_all([u, l])
    db.session.commit()    

if __name__ == '__main__':
    with app.app_context():
        create_test_users()
