from os import getenv
from init_app import db
from operator import or_
from util_constants import UserRole
from entities.user_entity import User
from flask import jsonify, abort, request
from util_functions import validate_email_field, extract_request_body, check_password, generate_jwt_token, \
    check_for_required_fields, hash_password

def login():
    request_form = extract_request_body(request)
    check_for_required_fields(["email", "password"], request_form)
    username = request_form["email"]
    password = request_form['password']
    validate_email_field(username, 'email')
    # try:
    default_error_message = "Incorrect login details"

    validate_email_field(username, 'email')
    user_record = User.query.filter_by(email = username).first()

    if not user_record:
        abort(404, default_error_message)

    user_record = user_record.toDict()
    password_compared = check_password(password, user_record["password"])
    if not password_compared:
        abort(401, default_error_message)

    # convert json to jwt
    jwt_token_data = {
        "user_id": user_record["id"],
        "email": user_record["email"],
        "phone_number": user_record["phone_number"]
    }
    jwt_token = generate_jwt_token(jwt_token_data, secret_key=getenv('JWT_SECRET_KEY'))
    return jsonify({
        "success": True,
        "code": 200,
        "data": jwt_token_data,
        "token": jwt_token
    })
    # except Exception as ex:
    #     # Extract and print the error message
    #     message = f"An error occurred: {str(ex)}"
    #     print(message)
    #     # abort(500, ex)

def sign_up(user_role = UserRole.ADMIN.value):
    request_form = extract_request_body(request)
    check_for_required_fields(['email', 'password', 'phone_number'], request_form)

    email = request_form["email"]
    password = request_form["password"]
    phone_number = request_form["phone_number"]

    validate_email_field(email, "email")
    existing_record = User.query.filter(or_(User.email == str(email).lower(), User.phone_number == phone_number)).first()

    if existing_record is not None:
        abort(409, "Similar user record already exists")

    # Encrypt password
    encrypted_password = hash_password(password)

    new_user = User(email=email, phone_number=phone_number, password=encrypted_password, user_role=user_role)
    db.session.add(new_user)
    db.session.commit()

    new_user_account = User.query.get(new_user.id).toDict()
    return jsonify({
        "success": True,
        "code": 201,
        "message": "Created",
        "data": new_user_account
    })


def find_users():
    users = User.query.all()
    result = []
    for user in users: result.append(user.toDict())
    return jsonify({
        "success": True,
        "code": 200,
        "message": "Records found",
        "data": result
    })

def find_user_by_id(user_id: str):
    result = User.query.get(user_id)
    if not result or result is None:
        abort(404,"User was not found")

    return jsonify({
        "success": True,
        "code": 200,
        "message": "Record found",
        "data": result.toDict()
    })