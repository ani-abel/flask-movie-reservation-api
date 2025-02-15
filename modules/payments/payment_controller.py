from flask import Blueprint
from middlewares.middleware import token_required
from modules.payments.payment_service import initiate_paystack_payment, verify_paystack_payment

payment_blueprint_api = Blueprint('payment_routes', __name__)

@payment_blueprint_api.route("/initiate-paystack-payment", methods=["GET"])
@token_required
def controller_initiate_paystack_payment(current_user):
    print(f"current_user => {current_user}")
    return initiate_paystack_payment(current_user)

@payment_blueprint_api.route("/verify-paystack-payment", methods=["GET"])
@token_required
def controller_verify_paystack_payment(current_user):
    print(f"current_user => {current_user}")
    return verify_paystack_payment(current_user)
