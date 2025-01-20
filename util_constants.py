from enum import  Enum

class UserRole(Enum):
    CUSTOMER = 'customer'
    ADMIN = 'admin'
    SUPER_ADMIN = 'super_admin'

class PaymentGateway(Enum):
    PAYSTACK = 'paystack'
    FLUTTERWAVE = 'flutterwave'

class PaymentStatus(Enum):
    SUCCESSFUL = 'successful'
    FAILED = 'failed'
    PENDING = 'pending'
