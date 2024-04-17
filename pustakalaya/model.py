from .extensions import db
from .extensions import login_manager
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property






########################## Association tables ##################################

# Association table for many to many relationship between collection and books table
collection_books = db.Table(
    "collection_books",
    db.Column("collection_id", db.ForeignKey('collection.id'), primary_key=True),
    db.Column("book_id", db.ForeignKey('book.id'), primary_key=True)
)

# Association table for many to many relationship between users and books table - storing likes
book_likes = db.Table(
    "book_likes",
    db.Column("user_id", db.ForeignKey('user.id'), primary_key=True),
    db.Column("book_id", db.ForeignKey('book.id'), primary_key=True)
)

# Association table for many to many relationship between users and books table - storing dislikes
book_dislikes = db.Table(
    "book_dislikes",
    db.Column("user_id", db.ForeignKey('user.id'), primary_key=True),
    db.Column("book_id", db.ForeignKey('book.id'), primary_key=True)
)

# Association table for many to many relationship between Book and Author table
class BookAuthor(db.Model):
    __tablename__ = "book_author"
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("author.id"), primary_key=True)


# Association table for many to many relationship between Book and User table for storing rating
class Feedback(db.Model):
    __tablename__ = "feedback"
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), primary_key=True)
    rating = db.Column(db.Integer)
    comment = db.Column(db.String)







################################### Handling Book Requests (Basically association table) ########################################
class BookIssueRequest(db.Model):
    __tablename__ = 'book_issue_request'
    request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), index=True)
    request_time = db.Column(db.DateTime, nullable=False)
    requested_days = db.Column(db.Integer, nullable=False, default = 2)
    status = db.Column(db.String(10), nullable=False)
    # status - pending
    @hybrid_property
    def days_since_request(self):
        return f"{(datetime.now() - self.request_time).days()}"
    # status - rejected
    rejection_time = db.Column(db.DateTime)
    # status - approved
    issue_time = db.Column(db.DateTime)
    @hybrid_property
    def access_remaining_for_days(self):
        return f"{self.requested_days - (datetime.today()-self.issue_time).days()}"
    # status - revoked
    return_time = db.Column(db.DateTime)
    @hybrid_property
    def days_issued(self):
        return f"{(self.return_time - self.issue_time).days()}"
    # establising the relationship with book and user table to get the book and user related to the request - Many to One
    book = db.relationship('Book', viewonly=True)
    user = db.relationship('User', back_populates='all_requests')
    







################################## Handling Users and Librarians ######################################

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(10), nullable=False, unique=True)
    first_name = db.Column(db.String(15), nullable=False)
    last_name = db.Column(db.String(15), default='')
    password = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(15), nullable=False)
    profile_pic_src = db.Column(db.String(50), nullable=True)
    ## ----------------------Relationships -------------------------
    # establish relationship with Collection table One to Many
    collections = db.relationship('Collection', back_populates='curator', cascade="all, delete")
    # establish relationship with Book table for Knowing the likes of a user and also to know about the users who liked a particular song - Many to Many
    liked_books = db.relationship('Book', secondary=book_likes, back_populates='liked_by')
    # establish relationship with Book table for Knowing the dislikes of a user and also to know about the users who liked a particular song - Many to Many
    disliked_books = db.relationship('Book', secondary=book_dislikes, back_populates='disliked_by')
    # establishing the relationship with user table and book_issue_request table to get the book requests related to a user
    all_requests = db.relationship('BookIssueRequest', back_populates='user')
    # relationship with Feedback table - Many to Many
    feedbacks_given = db.relationship('Book', secondary='feedback', back_populates='all_feedbacks')


    # to be able to access user.name
    @hybrid_property
    def name(self):
        return f"{self.first_name} {self.last_name}"
    # to get the currently_issued_books for a user
    @hybrid_property
    def currently_issued_books(self):
        issued_books = [book_request.book for book_request in self.all_requests if book_request.status == "issued"]
        return issued_books
    # to get the pending_issue_requests for a user
    @hybrid_property
    def pending_issue_requests(self):
        pending_requests = [book_request for book_request in self.all_requests if book_request.status == "pending"]
        return pending_requests
    # to get the pending_issue_books for a user
    @hybrid_property
    def pending_issue_books(self):
        pending_books = [book_request.book for book_request in self.all_requests if book_request.status == "pending"]
        return pending_books
    # to get the rejected_issue_requests for a user
    @hybrid_property
    def rejected_issue_requests(self):
        rejected_requests = [book_request for book_request in self.all_requests if book_request.status == "rejected"]
        return rejected_requests
    


    # for a polymorphic relationship
    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': 'role'
    }


class Librarian(User):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True, autoincrement=True)
    ## ----------------------Relationships -------------------------
    # establish relationship with Book table (Books uploaded by the librarian) - One to Many
    uploaded_books = db.relationship('Book', back_populates='uploaded_by')
    # polymorphic identity of librarian
    __mapper_args__ = {"polymorphic_identity": "librarian"}






############################# Handling Other entities related to library such as Books, Authors, Sections etc #################################

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    ## ----------------------Relationships -------------------------
    # relationship with Book table - Many to Many
    books = db.relationship('Book', secondary='book_author', back_populates='authors', cascade="all, delete")


class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String)
    ## ----------------------Relationships -------------------------
    # relationship with Book table - One to Many
    books = db.relationship('Book', back_populates='section', cascade="all, delete")

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    description = db.Column(db.String)
    isbn = db.Column(db.String(13))
    publisher = db.Column(db.String(20), nullable=True)
    publish_year = db.Column(db.String, default=None)
    file_name = db.Column(db.String, nullable=False)
    cover_image = db.Column(db.String)
    times_issued = db.Column(db.Integer, default=0)
    is_flagged = db.Column(db.Boolean, unique=False, default=False)
    file_path = db.Column(db.String(200), default='#')
    upload_date = db.Column(db.DateTime, default=datetime.now())
    number_of_volumes = db.Column(db.Integer, default=1)
    number_of_pages = db.Column(db.Integer)
    ## ----------------------Relationships -------------------------
    # relationship with Genre table - Many to One
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'), nullable=True)
    genre = db.relationship('Genre', back_populates='books')
    # relationship with Feedback table - Many to Many
    all_feedbacks = db.relationship('User', secondary='feedback', back_populates='feedbacks_given')
    # relationship with Section table - Many to One
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=True)
    section = db.relationship('Section', back_populates='books')
    # relationship with Librarian table(which librarian uploaded it) - Many to One
    librarian_id = db.Column(db.Integer, db.ForeignKey('librarian.id'))
    uploaded_by = db.relationship('Librarian', back_populates='uploaded_books')
    # establish relationship with Collection table - Many to Many
    belongs_to_collections = db.relationship('Collection', secondary=collection_books, back_populates='books')
    # establish relationship with Language table - Many to One
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'), nullable=True)
    language = db.relationship('Language', back_populates='books')
    # establish relationship with Book table for Knowing the likes of a user and also to know about the users who liked a particular song - Many to Many
    liked_by = db.relationship('User', secondary=book_likes, back_populates='liked_books')
    # establish relationship with Book table for Knowing the likes of a user and also to know about the users who liked a particular song - Many to Many
    disliked_by = db.relationship('User', secondary=book_dislikes, back_populates='disliked_books')
    # establish relationship with Author - Many to Many
    authors = db.relationship('Author', secondary='book_author', back_populates='books')
    @hybrid_property
    def cover_image(self):
        return self.file_name[:-4]+'.jpg'

class Language(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(12), nullable=False, unique=True)
    ## ----------------------Relationships -------------------------
    # establishing relationship with Book table - One to Many
    books = db.relationship('Book', back_populates='language')












###################### Some extra features such as collection and genre support ###############################

class Collection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    is_public = db.Column(db.Boolean, unique=False, default=True)
    ## ----------------------Relationships -------------------------
    # establish relationship with User table - Many to One
    curator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    curator = db.relationship('User', back_populates='collections')
    # establish relationshiop with Book table - Many to Many
    books = db.relationship('Book', secondary=collection_books, back_populates='belongs_to_collections')

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), nullable=False)
    ## ----------------------Relationships -------------------------
    # establish relationship with Book table - One to Many
    books = db.relationship('Book', back_populates='genre')

