from sqlalchemy import inspect
from datetime import datetime
from sqlalchemy import event
from init_app import db
from uuid import uuid4

class Ticket(db.Model):
    id = db.Column(db.String(50), primary_key=True, nullable=False, unique=True)
    date_created = db.Column(db.DateTime(timezone=True),
                             default=datetime.now)  # The Date of the Instance Creation => Created one Time when Instantiation
    date_updated = db.Column(db.DateTime(timezone=True), default=datetime.now,
                             onupdate=datetime.now)  # The Date of the Instance Update => Changed with Every Update

    number_bought = db.Column(db.Integer, default=0, nullable=False)

    # Relations
    user_id = db.Column(db.String(100), db.ForeignKey("user.id"))
    user = db.relationship("User", back_populates="tickets")

    movie_theatre_id = db.Column(db.String(100), db.ForeignKey("movie_theatre.id"))
    movie_theatre = db.relationship("MovieTheatre", back_populates="movie_theatres")

    ticket_price_id = db.Column(db.String(100), db.ForeignKey("ticket_price.id"))
    ticket_price = db.relationship("TicketPrice", back_populates="tickets")

    # One-to-many
    payments = db.relationship("Payment", back_populates="ticket")

    # How to serialize SqlAlchemy PostgreSQL Query to JSON => https://stackoverflow.com/a/46180522
    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    def __repr__(self):
        return "<%r>" % self.id


@event.listens_for(Ticket, 'before_insert')
def before_insert_listener(mapper, connection, target):
    """
       This event listener generates a UUID before a new row is inserted.
       """
    if not target.id:  # Only generate UUID if not already set
        target.id = str(uuid4())

