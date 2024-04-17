from books_data import *


for data in books_data:
    book = Book(**data)
    db.session.add(book)

db.session.commit()


u = User(user_name='test_u', first_name='test_user', password='password')
l = Librarian(user_name='test_l', first_name='test_l', password='password')

a1 = Author(name='Author 1')
a2 = Author(name='Author 2')
a3 = Author(name='Author 3')
a4 = Author(name='Author 4')

s1 = Section(name='Section 1')
s2 = Section(name='Section 2')

db.session.add_all([u, l, a1, a2, a3, a4, s1, s2])
db.session.commit()
