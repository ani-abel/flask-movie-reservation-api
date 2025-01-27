from sqlalchemy.orm import validates
from sqlalchemy import inspect
from datetime import datetime
from sqlalchemy import event
from init_app import db
from uuid import uuid4

class Movie(db.Model):
    id = db.Column(db.String(50), primary_key=True, nullable=False, unique=True)
    date_created = db.Column(db.DateTime(timezone=True),
                             default=datetime.now)  # The Date of the Instance Creation => Created one Time when Instantiation
    date_updated = db.Column(db.DateTime(timezone=True), default=datetime.now,
                             onupdate=datetime.now)  # The Date of the Instance Update => Changed with Every Update
    status = db.Column(db.Boolean, nullable=False, default=True)

    title = db.Column(db.String(255), nullable=False, unique=True)
    synopsis = db.Column(db.String(255), nullable=False)
    runtime = db.Column(db.String(50), nullable=False)

    is_currently_active = db.Column(db.Boolean, nullable=False, default=True)
    promotional_image = db.Column(db.String(500), nullable=False)

    # Relations
    user_id = db.Column(db.String(100), db.ForeignKey("user.id"))
    user = db.relationship("User", back_populates="movies")

    # Relations
    movie_theatres = db.relationship("MovieTheatre", back_populates="movie")

    # Set an empty string to null for title field => https://stackoverflow.com/a/57294872
    @validates('title')
    def empty_string_to_null(self, key, value):
        if isinstance(value, str) and value == '':
            return None
        else:
            return value

    # How to serialize SqlAlchemy PostgreSQL Query to JSON => https://stackoverflow.com/a/46180522
    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    def __repr__(self):
        return "<%r>" % self.title


@event.listens_for(Movie, 'before_insert')
def before_insert_listener(mapper, connection, target):
    """
       This event listener generates a UUID before a new row is inserted.
       """
    # turn values to lowercase
    target.title = str(target.title).lower()
    target.synopsis = str(target.synopsis).lower()
    if not target.id:  # Only generate UUID if not already set
        target.id = str(uuid4())
