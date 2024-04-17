from flask_restful import fields

book_resource_fields = {
    'name' : fields.String,
    'description' : fields.String,
    'isbn' : fields.String,
    'publisher' : fields.String,
    'publish_year' : fields.String,
    'number_of_volumes' : fields.String,
    'number_of_pages' : fields.String,
    'section' : fields.String,
    'language' : fields.String,
    'authors' : fields.String,
}

section_resource_fields = {
    'name' : fields.String,
    'description' : fields.String,
    'books' : fields.Nested(book_resource_fields),
}
