from .extensions import db
from .extensions import login_manager
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property


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
    

class CurrentBookIssue(db.Model):
    __tablename__ = "current_book_issue"
    current_issue_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), primary_key=True)
    issue_date = db.Column(db.DateTime, nullable=False)
    
    @hybrid_property
    def days_issued(self):
        return f"({datetime.datetime.today()}-{self.return_date}).days"


class BookIssueHistory(db.Model):
    __tablename__ = "book_issue_history"
    issue_history_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), primary_key=True)
    issue_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime, nullable=False)

    @hybrid_property
    def days_issued(self):
        return f"({self.return_date}-{self.return_date}).days"

class CurrentBookRequest(db.Model):
    __tablename__ = "current_book_request"
    book_request_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), primary_key=True)
    issue_date = db.Column(db.DateTime, nullable=False)
    
    @hybrid_property
    def days_issued(self):
        return f"({datetime.datetime.today()}-{self.return_date}).days"

class RejectedBookRequest(db.Model):
    __tablename__ = "rejected_book_request"
    current_issue_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), primary_key=True)
    issue_date = db.Column(db.DateTime, nullable=False)
    
    @hybrid_property
    def days_issued(self):
        return f"({datetime.datetime.today()}-{self.return_date}).days"


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
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
    # to be able to access user.name
    # establish relationship with Books (to know currently issued books) with the help of CurrentBookIssue table - Many to Many
    currently_issued_books = db.relationship('Book', secondary='current_book_issue', back_populates='currently_issued_by')
    # establish relationship with Books (to know previously issued books) with the help of BookIssueHistory table - Many to Many
    previously_issued_books = db.relationship('Book', secondary='book_issue_history', back_populates='previously_issued_by')

    @hybrid_property
    def name(self):
        return f"{self.first_name} {self.last_name}"


    # for a polymorphic relationship
    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': 'role'
    }


class Librarian(User):
    librarian_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    ## ----------------------Relationships -------------------------
    # establish relationship with Book table (Books uploaded by the librarian) - One to Many
    uploaded_books = db.relationship('Book', back_populates='uploaded_by')
    # polymorphic identity of librarian
    __mapper_args__ = {"polymorphic_identity": "librarian"}


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_blacklisted = db.Column(db.Boolean, unique=False, default=False)
    ## ----------------------Relationships -------------------------
    # relationship with Book table - Many to Many
    books = db.relationship('Book', secondary='book_author', back_populates='authors', cascade="all, delete")


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


class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    section_id = db.Column(db.Integer)
    description = db.Column(db.String)
    ## ----------------------Relationships -------------------------
    # relationship with Book table - One to Many
    books = db.relationship('Book', back_populates='section', cascade="all, delete")


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    isbn = db.Column(db.String(13))
    publisher = db.Column(db.String(20), nullable=True)
    publish_year = db.Column(db.String, default=None)
    file_name = db.Column(db.String, nullable=False)
    times_issued = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0, index=True)
    dislikes = db.Column(db.Integer, default=0, index=True)
    is_flagged = db.Column(db.Boolean, unique=False, default=False)
    file_path = db.Column(db.String(200), default='#')
    upload_date = db.Column(db.DateTime, default=datetime.now())
    number_of_volumes = db.Column(db.Integer, default=1)
    number_of_pages = db.Column(db.Integer)
    ## ----------------------Relationships -------------------------
    # relationship with Genre table - Many to One
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'), nullable=True)
    genre = db.relationship('Genre', back_populates='books')
    # relationship with Section table - Many to One
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=True)
    section = db.relationship('Section', back_populates='books')
    # relationship with Librarian table(which librarian uploaded it) - Many to One
    librarian_id = db.Column(db.Integer, db.ForeignKey('librarian.librarian_id'))
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
    # establish relationship with Users (to know currently issued books) with the help of CurrentBookIssue table - Many to Many
    currently_issued_by = db.relationship('User', secondary='current_book_issue', back_populates='currently_issued_books')
    # establish relationship with Users (to know previously issued books) with the help of BookIssueHistory table - Many to Many
    previously_issued_by = db.relationship('User', secondary='book_issue_history', back_populates='previously_issued_books')


class Language(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(12), nullable=False, unique=True)
    ## ----------------------Relationships -------------------------
    # establishing relationship with Book table - One to Many
    books = db.relationship('Book', back_populates='language')

