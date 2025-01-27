from sqlalchemy import inspect
from datetime import datetime
from sqlalchemy import event
from init_app import db
from uuid import uuid4

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

    movie_theatres = db.relationship("Ticket", back_populates="movie_theatre")
    # tickets = db.relationship("Ticket", back_populates="movie_theatre")
    # movies = db.relationship("Movie", back_populates="user")


    # How to serialize SqlAlchemy PostgreSQL Query to JSON => https://stackoverflow.com/a/46180522
    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    def __repr__(self):
        return "<%r>" % self.id

@event.listens_for(MovieTheatre, 'before_insert')
def before_insert_listener(mapper, connection, target):
    """
       This event listener generates a UUID before a new row is inserted.
       """
    if not target.id:  # Only generate UUID if not already set
        target.id = str(uuid4())