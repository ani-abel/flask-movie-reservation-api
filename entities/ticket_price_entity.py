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
    # Many-to-one
    user_id = db.Column(db.String(100), db.ForeignKey("user.id"))
    user = db.relationship("User", back_populates="ticket_prices")

    # One-to-many
    tickets = db.relationship("Ticket", back_populates="ticket_price")

    # How to serialize SqlAlchemy PostgreSQL Query to JSON => https://stackoverflow.com/a/46180522
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
        return "<%r>" % self.email


@event.listens_for(TicketPrice, 'before_insert')
def before_insert_listener(mapper, connection, target):
    """
       This event listener generates a UUID before a new row is inserted.
       """
    if not target.id:  # Only generate UUID if not already set
        target.id = str(uuid4())