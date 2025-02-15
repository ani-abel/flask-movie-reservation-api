from os import getenv
from init_app import db
from dotenv import load_dotenv
from flask import request, jsonify, abort
from entities.payment_entity import Payment
from util_constants import PaymentGateway, PaymentStatus
from util_functions import get_api_request, extract_request_query_params, convert_price_to_kobo, \
    check_for_required_fields, post_api_request, \
    validate_uuid_field, convert_price_to_naira

load_dotenv("./.env")

def verify_paystack_payment(current_user):
    request_form = extract_request_query_params(request)
    check_for_required_fields(["reference"], request_form)
    reference = request_form["reference"]

    paystack_secret_key = getenv('PAYSTACK_SECRET_KEY')
    if not paystack_secret_key:
        abort(400, "No paystack secret key has been set")

    verification_url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {paystack_secret_key}",
        "Content-Type": "application/json"
    }
    paystack_result = get_api_request(verification_url, headers)
    if not paystack_result["status"]:
        error_message = paystack_result["code"] if paystack_result["code"] else "Could not verify payment"
        abort(503, error_message)

    # Check if existing record exists
    existing_payment = Payment.query.filter(Payment.payment_ref == reference).first()
    if existing_payment:
        return jsonify({
            "success": True,
            "code": 200,
            "message": "Payment already verified",
            "data": remove_sensitive_fields(existing_payment.toDict())
        })

    # Save to DB
    paystack_result_data = paystack_result["data"]
    payment_ref = reference
    amount = convert_price_to_naira(float(paystack_result_data["amount"]))
    user_id = paystack_result_data["metadata"]["user_id"]
    movie_theatre_id = paystack_result_data["metadata"]["movie_theatre_id"]
    gateway = PaymentGateway.PAYSTACK.value
    payment_status = PaymentStatus.SUCCESSFUL.value
    data_payload = paystack_result_data
    channel = paystack_result_data["channel"]

    new_payment_record = Payment(
        channel=channel,
        data_payload=data_payload,
        gateway=gateway,
        user_id=user_id,
        amount=amount,
        payment_ref=payment_ref,
        payment_status=payment_status
    )
    db.session.add(new_payment_record)
    db.session.commit()

    newly_saved_payment_record = Payment.query.get(new_payment_record.id).toDict()
    return jsonify({
        "success": True,
        "code": 200,
        "message": "Payment verified",
        "data": remove_sensitive_fields(newly_saved_payment_record)
    })

def initiate_paystack_payment(current_user):
    request_form = extract_request_query_params(request)
    check_for_required_fields(["movie_theatre_id", "amount"], request_form)
    user_id = current_user["id"]
    user_email = current_user["email"]
    amount = float(request_form["amount"])
    movie_theatre_id = request_form["movie_theatre_id"]
    validate_uuid_field(movie_theatre_id, "movie_theatre_id")
    if amount <= 0:
        abort(400, "Field amount must be > 0")

    paystack_secret_key = getenv('PAYSTACK_SECRET_KEY')
    if not paystack_secret_key:
        abort(400, "No paystack secret key has been set")

    paystack_init_url = 'https://api.paystack.co/transaction/initialize'
    price_in_kobo = convert_price_to_kobo(amount)
    paystack_result = post_api_request(url=paystack_init_url, body={
        "amount": price_in_kobo,
        "email": user_email,
        "channels": ['card', 'bank', 'ussd', 'bank_transfer'],
        "metadata": {
            "user_id": user_id,
            "movie_theatre_id": movie_theatre_id,
        }
    }, headers={
        "Authorization": f"Bearer {paystack_secret_key}",
        "Content-Type": "application/json"
    })
    if not paystack_result["status"]:
        error_message = paystack_result["code"] if paystack_result["code"] else "Could not get payment initiation response"
        abort(502,  error_message)

    response_data = paystack_result["data"]
    return jsonify({
        "success": True,
        "code": 200,
        "message": "Paystack payment session initialized",
        "data": {
            "auth_url": response_data["authorization_url"],
            "access_code": response_data["access_code"],
            "reference": response_data["reference"]
        }
    })

def remove_sensitive_fields(payment_record: dict) -> dict:
    payment_record["data_payload"] = None
    return payment_record