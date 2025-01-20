from sqlalchemy.orm import validates
from sqlalchemy import inspect
from datetime import datetime
from sqlalchemy import event
from init_app import db
from uuid import uuid4

class Theatre(db.Model):
    id = db.Column(db.String(50), primary_key=True, nullable=False, unique=True)
    date_created = db.Column(db.DateTime(timezone=True),
                             default=datetime.now)  # The Date of the Instance Creation => Created one Time when Instantiation
    date_updated = db.Column(db.DateTime(timezone=True), default=datetime.now,
                             onupdate=datetime.now)  # The Date of the Instance Update => Changed with Every Update

    name = db.Column(db.String(255), nullable=False)

    location = db.Column(db.String(500), nullable=False)
    seat_count = db.Column(db.Integer, nullable=False, default=0)

    # Relations
    # ==> Admin who added this theatre to db
    user_id = db.Column(db.String(100), db.ForeignKey("user.id"))
    user = db.relationship("User", back_populates="theatres")

    # Relations
    movieTheatres = db.relationship("MovieTheatre", back_populates="theatre")

    # Set an empty string to null for username field => https://stackoverflow.com/a/57294872
    @validates('name')
    def empty_string_to_null(self, key, value):
        if isinstance(value, str) and value == '':
            return None
        else:
            return value

    # How to serialize SqlAlchemy PostgreSQL Query to JSON => https://stackoverflow.com/a/46180522
    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    def __repr__(self):
        return "<%r>" % self.name

@event.listens_for(Theatre, 'before_insert')
def before_insert_listener(mapper, connection, target):
    """
       This event listener generates a UUID before a new row is inserted.
       """
    if not target.id:  # Only generate UUID if not already set
        target.id = str(uuid4())



