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







################################### Handling Book Requests (Basically association tables) ########################################
class PendingIssueRequest(db.Model):
    __tablename__ = 'pending_issue_request'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), primary_key=True)
    request_time = db.Column(db.DateTime, nullable=False)
    requested_days = db.Column(db.Integer, nullable=False, default = 2)
    # establising the relationship with book and user table to get the book and user related to the request - Many to One
    book = db.relationship('Book', viewonly=True)
    user = db.relationship('User', viewonly=True)
    @hybrid_property
    def days_since_request(self):
        return f"({datetime.now() - self.request_time}).days"

class RejectedIssueRequest(db.Model):
    __tablename__ = 'rejected_issue_request'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), primary_key=True)
    request_time = db.Column(db.DateTime, nullable=False)
    rejection_time = db.Column(db.DateTime, nullable=False)
    # establising the relationship with book and user table to get the book and user related to the request - Many to One
    book = db.relationship('Book', viewonly=True)
    user = db.relationship('User', viewonly=True)
    responsed_librarian_id = db.Column(db.Integer, db.ForeignKey('librarian.id'))
    rejected_by = db.relationship('Librarian', back_populates='rejected_issue_requests', foreign_keys=[responsed_librarian_id])



class ApprovedIssueRequest(db.Model):
    __tablename__ = 'approved_issue_request'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), primary_key=True)
    request_time = db.Column(db.DateTime, nullable=False)
    issue_time = db.Column(db.DateTime, nullable=False)
    # establishing relationships with Librarian table(which librarian approved). Many to one
    responsed_librarian_id = db.Column(db.Integer, db.ForeignKey('librarian.id'))
    approved_by = db.relationship('Librarian', back_populates='approved_issue_requests', foreign_keys=[responsed_librarian_id])
    # establising the relationship with book and user table to get the book and user related to the request - Many to One
    book = db.relationship('Book', viewonly=True)
    user = db.relationship('User', viewonly=True)
    @hybrid_property
    def access_remaining_for_days(self):
        return f"{self.requested_days - (datetime.today()-self.issue_time).days}"
    

class RevokedBookAccess(db.Model):
    __tablename__ = 'revoked_book_access'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), primary_key=True)
    request_time = db.Column(db.DateTime, nullable=False)
    return_time = db.Column(db.DateTime, nullable=False)
    # establishing relationships with Librarian table(which librarian approved). Many to one
    responsed_librarian_id = db.Column(db.Integer, db.ForeignKey('librarian.id'))
    revoked_by = db.relationship('Librarian', back_populates='revoked_book_accesses', foreign_keys=[responsed_librarian_id])
    # establising the relationship with book and user table to get the book and user related to the request - Many to One
    book = db.relationship('Book', viewonly=True)
    user = db.relationship('User', viewonly=True)
    @hybrid_property
    def days_issued(self):
        return f"{(self.issue_time - self.return_time).days}"








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
    # to be able to access user.name
    # establish relationship with Books (to know currently issued books) with the help of ApprovedIssueRequest table - Many to Many
    currently_issued_books = db.relationship('Book', secondary='approved_issue_request', back_populates='currently_issued_by')
    # establish relationship with Books (to know previously issued books) with the help of BookIssueHistory table - Many to Many
    previously_issued_books = db.relationship('Book', secondary='revoked_book_access', back_populates='previously_issued_by')
    # establish relationship with Books (to know previously issued books) with the help of PendingIssueRequest table - Many to Many
    pending_issue_requests = db.relationship('Book', secondary='pending_issue_request', back_populates='pending_requests_for')

    @hybrid_property
    def name(self):
        return f"{self.first_name} {self.last_name}"


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
    # establish relationship with RejectedIssueRequest table (books rejected by librarian) - One to Many
    rejected_issue_requests = db.relationship('RejectedIssueRequest', back_populates='rejected_by', foreign_keys="RejectedIssueRequest.responsed_librarian_id")
    # establish relationship with ApprovedIssueRequest table (books approved by librarian) - One to Many
    approved_issue_requests = db.relationship('ApprovedIssueRequest', back_populates='approved_by', foreign_keys="ApprovedIssueRequest.responsed_librarian_id")
    # establish relationship with RevokedBookAccess table (books revoked by librarian) - One to Many
    revoked_book_accesses = db.relationship('RevokedBookAccess', back_populates='revoked_by', foreign_keys="RevokedBookAccess.responsed_librarian_id")
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
    # establish relationship with Users (to know currently issued books) with the help of CurrentBookIssue table - Many to Many
    currently_issued_by = db.relationship('User', secondary='approved_issue_request', back_populates='currently_issued_books')
    # establish relationship with Users (to know previously issued books) with the help of BookIssueHistory table - Many to Many
    previously_issued_by = db.relationship('User', secondary='revoked_book_access', back_populates='previously_issued_books')
    # establish relationship with Users (to know currently pending issue of books) with the help of PendingIssueRequest table - Many to Many
    pending_requests_for = db.relationship('User', secondary='pending_issue_request', back_populates='pending_issue_requests')


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

