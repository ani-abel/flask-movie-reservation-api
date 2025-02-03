from time import timezone
from uuid import uuid4
from init_app import db
from sqlalchemy import event
from datetime import datetime
from sqlalchemy import inspect

class MovieTheatre(db.Model):
    id = db.Column(db.String(50), primary_key=True, nullable=False, unique=True)
    date_created = db.Column(db.DateTime(timezone=True),
                             default=datetime.now)  # The Date of the Instance Creation => Created one Time when Instantiation
    date_updated = db.Column(db.DateTime(timezone=True), default=datetime.now,
                             onupdate=datetime.now)  # The Date of the Instance Update => Changed with Every Update

    # Relations
    movie_id = db.Column(db.String(100), db.ForeignKey("movie.id"))
    movie = db.relationship("Movie", back_populates="movie_theatres")

    theatre_id = db.Column(db.String(100), db.ForeignKey("theatre.id"))
    theatre = db.relationship("Theatre", back_populates="movieTheatres")

    is_active = db.Column(db.Boolean, nullable=False, default=True)
    start_time = db.Column(db.String(20), nullable=False)
    end_time = db.Column(db.String(20), nullable=False)
    viewing_date = db.Column(db.DateTime(timezone=True), nullable=False)

    movie_theatres = db.relationship("Ticket", back_populates="movie_theatre")


    # How to serialize SqlAlchemy PostgreSQL Query to JSON => https://stackoverflow.com/a/46180522
    # def toDict(self):
    #     return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    def toDict(self, include_nested_fields=None):
        # Convert basic columns to dictionary
        result = {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

        # If no nested fields are specified, just return the result
        if not include_nested_fields:
            return result

        # Dynamically include nested fields
        for field in include_nested_fields:
            related_obj = getattr(self, field, None)
            if related_obj:
                # Call the `toDict` method of the related object, if it exists
                result[field] = related_obj.toDict() if hasattr(related_obj, 'toDict') else str(related_obj)

        return result

    def __repr__(self):
        return "<%r>" % self.id

@event.listens_for(MovieTheatre, 'before_insert')
def before_insert_listener(mapper, connection, target):
    """
       This event listener generates a UUID before a new row is inserted.
       """
    if not target.id:  # Only generate UUID if not already set
        target.id = str(uuid4())