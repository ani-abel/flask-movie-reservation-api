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

    # Relations
    user_id = db.Column(db.String(100), db.ForeignKey("user.id"))
    user = db.relationship("User", back_populates="payments")

    amount = db.Column(db.Float, nullable=False, default=0)
    payment_ref = db.Column(db.String(255), nullable=False)
    # gateway = db.Column(db.Enum(PaymentGateway), nullable=False, default=PaymentGateway.PAYSTACK.value)
    # payment_status = db.Column(db.Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING.value)
    channel = db.Column(db.String(50), nullable=False)
    gateway = db.Column(db.String(50), nullable=False, default=PaymentGateway.PAYSTACK.value)
    payment_status = db.Column(db.String(50), nullable=False, default=PaymentStatus.PENDING.value)
    data_payload = db.Column(db.JSON, nullable=True)

    # Relations
    # One-to-many
    tickets = db.relationship("Ticket", back_populates="payment", cascade="all, delete-orphan")

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
        return "<%r>" % self.id


@event.listens_for(Payment, 'before_insert')
def before_insert_listener(mapper, connection, target):
    """
       This event listener generates a UUID before a new row is inserted.
       """
    if not target.id:  # Only generate UUID if not already set
        target.id = str(uuid4())



