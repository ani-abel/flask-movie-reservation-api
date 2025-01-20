import re
import jwt
from flask import abort
from datetime import datetime, timedelta
from bcrypt import gensalt, hashpw, checkpw


def extract_request_body(request) -> dict:
    request_form: dict = {}
    if request.content_type.startswith('multipart/form-data'):
        request_form = request.form.to_dict()
    else:
        request_form = request.get_json()

    return request_form

def validate_uuid(uuid_string: str) -> bool:
    # /^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/;
    reg_exp = r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
    return bool(re.match(reg_exp, uuid_string))

def validate_uuid_field(uuid_string: str, field_name="uuid"):
    if not validate_uuid(uuid_string):
        abort(400, f"Field {field_name} has invalid uuid format")

def validate_email(email: str) -> bool:
    reg_exp = r'^[a-zA-Z0-9.!#$%&\'*+\/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$'
    return bool(re.match(reg_exp, email))

def validate_email_field(email: str, field_name="email"):
    if not validate_email(email):
        abort(400, f'Field {field_name} has invalid format')

def decode_jwt_token(encoded_token: str, secret_key: str) -> dict:
    # Decode the JWT
    return jwt.decode(encoded_token, secret_key, algorithms=['HS256'])

def generate_jwt_token(payload: dict, secret_key: str) -> str:
    # Encode the JWT
    return jwt.encode(
        payload={ "profile": payload, "exp": datetime.utcnow() + timedelta(hours=24)},
        key=secret_key,
        algorithm="HS256"
    )

def hash_password(password: str) -> str:
    try:
        pw_hash = hashpw(password.encode('utf8'), gensalt())
        return pw_hash.decode('utf8')
    except Exception as ex:
        print(f"An error occurred: {ex}")
        raise Exception(ex)

def check_password(plain_password: str, hashed_password: str) -> bool:
    # Compare the plain password with the hashed password
    try:
        # Hashing in bcrypt includes the salt, so we can use `checkpw`
        is_valid = checkpw(plain_password.encode('utf8'), hashed_password.encode('utf8'))
        return is_valid
    except Exception as ex:
        print(f"An error occurred: {ex}")
        return False
