from sqlalchemy.orm import validates
from util_constants import UserRole
from sqlalchemy import inspect
from datetime import datetime
from sqlalchemy import event
from init_app import db
from uuid import uuid4

class User(db.Model):
    id = db.Column(db.String(50), primary_key=True, nullable=False, unique=True)
    date_created = db.Column(db.DateTime(timezone=True),
                        default=datetime.now)  # The Date of the Instance Creation => Created one Time when Instantiation
    date_updated = db.Column(db.DateTime(timezone=True), default=datetime.now,
                        onupdate=datetime.now)  # The Date of the Instance Update => Changed with Every Update

    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(50), nullable=False)
    user_role = db.Column(db.String(50), nullable=False, default=UserRole.ADMIN.value)
    # user_role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.ADMIN.value)

    # Relations
    theatres = db.relationship("Theatre", back_populates="user", cascade="all, delete-orphan")
    tickets = db.relationship("Ticket", back_populates="user", cascade="all, delete-orphan")
    movies = db.relationship("Movie", back_populates="user", cascade="all, delete-orphan")
    ticket_prices = db.relationship("TicketPrice", back_populates="user", cascade="all, delete-orphan")

    # Set an empty string to null for username field => https://stackoverflow.com/a/57294872
    @validates('email')
    def empty_string_to_null(self, key, value):
        if isinstance(value, str) and value == '':
            return None
        else:
            return value

    # How to serialize SqlAlchemy PostgreSQL Query to JSON => https://stackoverflow.com/a/46180522
    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    def __repr__(self):
        return "<%r>" % self.email

@event.listens_for(User, 'before_insert')
def before_insert_listener(mapper, connection, target):
    """
       This event listener generates a UUID before a new row is inserted.
       """
    target.email = str(target.email).lower()
    if not target.id:  # Only generate UUID if not already set
        target.id = str(uuid4())
 