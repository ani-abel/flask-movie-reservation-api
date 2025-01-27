from util_constants import PaymentStatus, PaymentGateway
from sqlalchemy import inspect
from datetime import datetime
from sqlalchemy import event
from init_app import db
from uuid import uuid4

class Payment(db.Model):
    id = db.Column(db.String(50), primary_key=True, nullable=False, unique=True)
    date_created = db.Column(db.DateTime(timezone=True),
                        default=datetime.now)  # The Date of the Instance Creation => Created one Time when Instantiation
    date_updated = db.Column(db.DateTime(timezone=True), default=datetime.now,
                        onupdate=datetime.now)  # The Date of the Instance Update => Changed with Every Update
    status = db.Column(db.Boolean, nullable=False, default=True)


    payment_ref = db.Column(db.String(255), nullable=False)
    gateway = db.Column(db.Enum(PaymentGateway), nullable=False, default=PaymentGateway.PAYSTACK)
    payment_status = db.Column(db.Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    data_payload = db.Column(db.JSON, nullable=True)

    # Relations
    ticket_id = db.Column(db.String(100), db.ForeignKey("ticket.id"))
    ticket = db.relationship("Ticket", back_populates="payments")

    # How to serialize SqlAlchemy PostgreSQL Query to JSON => https://stackoverflow.com/a/46180522
    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    def __repr__(self):
        return "<%r>" % self.id


@event.listens_for(Payment, 'before_insert')
def before_insert_listener(mapper, connection, target):
    """
       This event listener generates a UUID before a new row is inserted.
       """
    if not target.id:  # Only generate UUID if not already set
        target.id = str(uuid4())



