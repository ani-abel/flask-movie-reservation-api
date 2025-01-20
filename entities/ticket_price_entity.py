from sqlalchemy import inspect
from datetime import datetime
from sqlalchemy import event
from init_app import db
from uuid import uuid4

class TicketPrice(db.Model):
    id = db.Column(db.String(50), primary_key=True, nullable=False, unique=True)
    date_created = db.Column(db.DateTime(timezone=True),
                             default=datetime.now)  # The Date of the Instance Creation => Created one Time when Instantiation
    date_updated = db.Column(db.DateTime(timezone=True), default=datetime.now,
                             onupdate=datetime.now)  # The Date of the Instance Update => Changed with Every Update

    price = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=True, default=True)

    # Relations
    # ==> Admin who added this theatre_price to db
    user_id = db.Column(db.String(100), db.ForeignKey("user.id"))
    user = db.relationship("User", back_populates="ticketPrices")

    tickets = db.relationship("Ticket", back_populates="ticket_price")

    # How to serialize SqlAlchemy PostgreSQL Query to JSON => https://stackoverflow.com/a/46180522
    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    def __repr__(self):
        return "<%r>" % self.email


@event.listens_for(TicketPrice, 'before_insert')
def before_insert_listener(mapper, connection, target):
    """
       This event listener generates a UUID before a new row is inserted.
       """
    if not target.id:  # Only generate UUID if not already set
        target.id = str(uuid4())