from books_data import *


for data in books_data:
    book = Book(**data)
    db.session.add(book)

db.session.commit()


u = User(user_name='test_u', first_name='test_user', password='password')
l = Librarian(user_name='test_l', first_name='test_l', password='password')

a1 = Author(name='Benjamin Franklin')
a2 = Author(name='Aristotle')
a3 = Author(name='Newton')
a4 = Author(name='Plato')

s1 = Section(name='Science')
s2 = Section(name='History')

db.session.add_all([u, l, a1, a2, a3, a4, s1, s2])
db.session.commit()
